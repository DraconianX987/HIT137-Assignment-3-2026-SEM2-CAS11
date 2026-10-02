import random

import cv2
import numpy as np

from tile import Tile
from transformations import SwapTransformation, RotateTransformation, FlipTransformation


class Puzzle:
    

    TRANSFORM_COUNTS = {3: 6, 4: 12, 5: 20}
    MAX_DISPLAY_SIZE = 600
    MAX_HINTS = 3

    def __init__(self, grid_size=3):
        if grid_size not in (3, 4, 5):
            raise ValueError("grid_size must be 3, 4 or 5")

        self._grid_size = grid_size
        self._tiles = []
        self._moves = 0
        self._hints_used = 0
        self._hint_tile_position = None
        self._hint_home_position = None
        self._solved = False

    @property
    def grid_size(self):
        return self._grid_size

    @property
    def moves(self):
        return self._moves

    @property
    def is_solved(self):
        return self._solved

    def load_image(self, path):
        # np.fromfile + imdecode also works for folders with special
        # characters in their name, which cv2.imread can't open on Windows
        try:
            data = np.fromfile(path, dtype=np.uint8)
        except OSError:
            raise ValueError(f"Could not read image: {path}")
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Could not read image: {path}")

        image = self._resize_to_fit(image)
        image = self._crop_to_grid(image)

        self._original_image = image
        self._tiles = self._split_into_tiles(image)
        self._moves = 0
        self._hints_used = 0
        self._hint_tile_position = None
        self._hint_home_position = None
        self._solved = False

        self.scramble()

    def _resize_to_fit(self, image):
        height, width = image.shape[:2]
        largest_side = max(height, width)
        scale = self.MAX_DISPLAY_SIZE / largest_side
        new_size = (int(width * scale), int(height * scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    def _crop_to_grid(self, image):
        # Tiles must be square, otherwise a rotated tile would no longer
        # fit back in its spot. So cut a square from the middle of the
        # picture, sized so it divides evenly into the grid.
        height, width = image.shape[:2]
        side = (min(height, width) // self._grid_size) * self._grid_size
        if side == 0:
            raise ValueError("Image is too small for this grid size")
        top = (height - side) // 2
        left = (width - side) // 2
        return image[top:top + side, left:left + side]

    def _split_into_tiles(self, image):
        height, width = image.shape[:2]
        tile_h = height // self._grid_size
        tile_w = width // self._grid_size

        tiles = []
        for row in range(self._grid_size):
            for col in range(self._grid_size):
                piece = image[row * tile_h:(row + 1) * tile_h,
                               col * tile_w:(col + 1) * tile_w].copy()
                tiles.append(Tile(piece, row, col))
        return tiles

    def _index_of(self, position):
        row, col = position
        return row * self._grid_size + col

    def tile_at(self, position):
        return self._tiles[self._index_of(position)]

    def swap_tiles(self, position1, position2, count_move=True):
        if count_move and self._solved:
            return
        i1 = self._index_of(position1)
        i2 = self._index_of(position2)

        self._tiles[i1], self._tiles[i2] = self._tiles[i2], self._tiles[i1]
        self._tiles[i1].set_current_position(*position1)
        self._tiles[i2].set_current_position(*position2)

        self._after_move(count_move)

    def rotate_tile(self, position, count_move=True):
        if count_move and self._solved:
            return
        self.tile_at(position).rotate()
        self._after_move(count_move)

    def flip_tile(self, position, direction='horizontal', count_move=True):
        if count_move and self._solved:
            return
        self.tile_at(position).flip(direction)
        self._after_move(count_move)

    def _after_move(self, count_move):
        if count_move:
            self._moves += 1
            self._clear_hint()
        self._solved = all(tile.is_correct() for tile in self._tiles)

    def scramble(self):
        count = self.TRANSFORM_COUNTS.get(self._grid_size, self._grid_size ** 2 * 2)

        # All transformations are made at once, then applied. In the rare
        # case they cancel each other out, scramble again.
        while True:
            transformations = [self._random_transformation() for _ in range(count)]
            for transformation in transformations:
                transformation.apply(self)
            if not all(tile.is_correct() for tile in self._tiles):
                break

        self._moves = 0
        self._hints_used = 0
        self._clear_hint()
        self._solved = all(tile.is_correct() for tile in self._tiles)

    def _random_transformation(self):
        n = self._grid_size
        kind = random.choice(['swap', 'rotate', 'flip'])

        if kind == 'swap':
            pos1 = (random.randrange(n), random.randrange(n))
            pos2 = (random.randrange(n), random.randrange(n))
            while pos2 == pos1:
                pos2 = (random.randrange(n), random.randrange(n))
            return SwapTransformation(pos1, pos2)

        if kind == 'rotate':
            pos = (random.randrange(n), random.randrange(n))
            angle = random.choice([90, 180, 270])
            return RotateTransformation(pos, angle)

        pos = (random.randrange(n), random.randrange(n))
        direction = random.choice(['horizontal', 'vertical'])
        return FlipTransformation(pos, direction)

    def reassemble(self):
        """Stitches all current tiles back into one image, in their current
        (possibly scrambled) arrangement."""
        sample = self._tiles[0].get_display_image()
        tile_h, tile_w = sample.shape[:2]
        n = self._grid_size

        canvas = np.zeros((tile_h * n, tile_w * n, 3), dtype=np.uint8)
        for row in range(n):
            for col in range(n):
                tile_image = self._tiles[row * n + col].get_display_image()
                canvas[row * tile_h:(row + 1) * tile_h,
                       col * tile_w:(col + 1) * tile_w] = tile_image
        return canvas

    def get_original_image(self):
        return self._original_image

    def incorrect_count(self):
        return sum(1 for tile in self._tiles if not tile.is_correct())

    def hints_remaining(self):
        return max(0, self.MAX_HINTS - self._hints_used)

    def request_hint(self):
        if self.hints_remaining() <= 0:
            return None

        incorrect_tiles = [t for t in self._tiles if not t.is_correct()]
        if not incorrect_tiles:
            return None

        tile = random.choice(incorrect_tiles)
        self._hint_tile_position = (tile.current_row, tile.current_col)
        self._hint_home_position = (tile.home_row, tile.home_col)
        self._hints_used += 1

        return self._hint_tile_position, self._hint_home_position

    def active_hint(self):
        return self._hint_tile_position, self._hint_home_position

    def _clear_hint(self):
        self._hint_tile_position = None
        self._hint_home_position = None

    def solve(self):
        ordered = sorted(self._tiles, key=lambda t: (t.home_row, t.home_col))
        for tile in ordered:
            tile.reset()
            tile.set_current_position(tile.home_row, tile.home_col)

        self._tiles = ordered
        self._moves = 0
        self._hints_used = 0
        self._clear_hint()
        self._solved = True