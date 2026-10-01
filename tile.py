import cv2


class Tile:
    """
    One piece of the scrambled image.

    Encapsulation: the tile's pixel data and transform state (rotation,
    flips) are private (_prefixed) and only reachable through methods or
    read-only properties — nothing outside this class reaches in and
    edits them directly.
    """

    ROTATION_STEP = 90
    FULL_ROTATION = 360

    def __init__(self, image, home_row, home_col):
        """
        image: the tile's original, unrotated/unflipped pixels (numpy array).
        home_row, home_col: where this tile belongs when the puzzle is solved.
        """
        self._base_image = image
        self._home_row = home_row
        self._home_col = home_col
        self._current_row = home_row
        self._current_col = home_col
        self._rotation = 0
        self._flip_horizontal = False
        self._flip_vertical = False

    @property
    def home_row(self):
        return self._home_row

    @property
    def home_col(self):
        return self._home_col

    @property
    def current_row(self):
        return self._current_row

    @property
    def current_col(self):
        return self._current_col

    def set_current_position(self, row, col):
        self._current_row = row
        self._current_col = col

    def rotate(self, clockwise=True):
        step = self.ROTATION_STEP if clockwise else -self.ROTATION_STEP
        self._rotation = (self._rotation + step) % self.FULL_ROTATION

    def flip(self, direction):
        """direction is 'horizontal' or 'vertical'."""
        if direction == 'horizontal':
            self._flip_horizontal = not self._flip_horizontal
        elif direction == 'vertical':
            self._flip_vertical = not self._flip_vertical
        else:
            raise ValueError("direction must be 'horizontal' or 'vertical'")

    def reset(self):
        """Clears rotation/flip state, but leaves current position alone —
        Puzzle.solve() is responsible for moving tiles back home."""
        self._rotation = 0
        self._flip_horizontal = False
        self._flip_vertical = False

    def is_correct(self):
        return (
            self._current_row == self._home_row
            and self._current_col == self._home_col
            and self._rotation == 0
            and not self._flip_horizontal
            and not self._flip_vertical
        )

    def get_display_image(self):
        """Returns the tile's pixels with its current rotation/flip applied,
        without touching the stored original."""
        image = self._base_image

        if self._flip_horizontal:
            image = cv2.flip(image, 1)
        if self._flip_vertical:
            image = cv2.flip(image, 0)

        if self._rotation == 90:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif self._rotation == 180:
            image = cv2.rotate(image, cv2.ROTATE_180)
        elif self._rotation == 270:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return image