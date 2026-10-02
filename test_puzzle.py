import cv2
import numpy as np

from puzzle import Puzzle


def make_test_image(path):
    """Makes a simple colourful test picture so we don't need a real photo.
    It's a rectangle (like a normal photo), not a square."""
    image = np.zeros((300, 400, 3), dtype=np.uint8)
    for row in range(300):
        for col in range(400):
            image[row, col] = [(row * 255) // 300, (col * 255) // 400, 128]
    cv2.imwrite(path, image)


def main():
    make_test_image("test.png")

    puzzle = Puzzle(grid_size=3)
    puzzle.load_image("test.png")

    print("Loaded image into a 3x3 puzzle.")
    print("Moves:", puzzle.moves)
    print("Incorrect tiles:", puzzle.incorrect_count())
    print("Is it solved?", puzzle.is_solved)
    print()

    print("Swapping tile (0,0) with tile (1,1)...")
    puzzle.swap_tiles((0, 0), (1, 1))
    print("Moves:", puzzle.moves)
    print()

    print("Rotating tile (2,2)...")
    puzzle.rotate_tile((2, 2))
    print("Moves:", puzzle.moves)
    print()

    print("Flipping tile (0,1)...")
    puzzle.flip_tile((0, 1))
    print("Moves:", puzzle.moves)
    print()

    print("Asking for a hint...")
    hint = puzzle.request_hint()
    print("Hint says: move the tile at", hint[0], "back to", hint[1])
    print("Hints left:", puzzle.hints_remaining())
    print()

    print("Solving the whole puzzle...")
    puzzle.solve()
    print("Moves:", puzzle.moves)
    print("Incorrect tiles:", puzzle.incorrect_count())
    print("Is it solved?", puzzle.is_solved)
    print()

    print("Saving the reassembled picture as result.png so you can look at it.")
    cv2.imwrite("result.png", puzzle.reassemble())

    print("Done. If nothing crashed and 'Is it solved?' said True at the end, your part works.")


if __name__ == '__main__':
    main()