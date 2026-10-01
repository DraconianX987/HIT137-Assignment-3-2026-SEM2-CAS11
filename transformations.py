class Transformation:
    """
    Abstract base class for a single scramble operation.

    Inheritance/polymorphism: Puzzle.scramble() builds a list containing a
    random mix of SwapTransformation, RotateTransformation and
    FlipTransformation objects, then calls .apply(puzzle) on each one
    without caring which subclass it actually is — each subclass provides
    its own apply() that does something different.
    """

    def apply(self, puzzle):
        raise NotImplementedError("Subclasses must implement apply()")

    def describe(self):
        return self.__class__.__name__


class SwapTransformation(Transformation):
    def __init__(self, position1, position2):
        self._position1 = position1
        self._position2 = position2

    def apply(self, puzzle):
        puzzle.swap_tiles(self._position1, self._position2, count_move=False)

    def describe(self):
        return f"Swap {self._position1} <-> {self._position2}"


class RotateTransformation(Transformation):
    def __init__(self, position, angle):
        self._position = position
        self._angle = angle  # 90, 180 or 270

    def apply(self, puzzle):
        steps = (self._angle // 90) % 4
        for _ in range(steps):
            puzzle.rotate_tile(self._position, count_move=False)

    def describe(self):
        return f"Rotate {self._position} by {self._angle} degrees"


class FlipTransformation(Transformation):
    def __init__(self, position, direction):
        self._position = position
        self._direction = direction  # 'horizontal' or 'vertical'

    def apply(self, puzzle):
        puzzle.flip_tile(self._position, self._direction, count_move=False)

    def describe(self):
        return f"Flip {self._position} {self._direction}"