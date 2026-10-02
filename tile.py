import cv2

class Tile:
    
    def __init__(self, image, home_row, home_col):
        """
        image: the tile's original pixels (numpy array).
        home_row, home_col: where this tile belongs when the puzzle is solved.
        """
        self._base_image = image
        self._home_row = home_row
        self._home_col = home_col
        self._current_row = home_row
        self._current_col = home_col
        self._turns = 0
        self._mirrored = False

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
        """Turns the tile 90 degrees."""
        if clockwise:
            self._turns = (self._turns + 1) % 4
        else:
            self._turns = (self._turns - 1) % 4

    def flip(self, direction):
        """direction is 'horizontal' or 'vertical'."""
        if direction == 'horizontal':
            # mirroring a turned tile is the same as mirroring first
            # and then turning the other way
            self._turns = (-self._turns) % 4
        elif direction == 'vertical':
            # a vertical flip is a horizontal flip plus a half turn
            self._turns = (2 - self._turns) % 4
        else:
            raise ValueError("direction must be 'horizontal' or 'vertical'")
        self._mirrored = not self._mirrored

    def reset(self):
        """Clears rotation/flip, but leaves current position alone.
        Puzzle.solve() is responsible for moving tiles back home."""
        self._turns = 0
        self._mirrored = False

    def is_correct(self):
        return (
            self._current_row == self._home_row
            and self._current_col == self._home_col
            and self._turns == 0
            and not self._mirrored
        )

    def get_display_image(self):
        """Returns the tile's pixels with its current orientation applied,
        without changing the stored original."""
        image = self._base_image

        if self._mirrored:
            image = cv2.flip(image, 1)

        if self._turns == 1:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif self._turns == 2:
            image = cv2.rotate(image, cv2.ROTATE_180)
        elif self._turns == 3:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return image