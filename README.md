# HIT137 Assignment 3 - Scrambled Image Puzzle (CAS11)

s320112 - Ian Lu

s400171 - Gokul Shajan Shajan

## What it does
A desktop game. You load a photo, it gets cut into a grid of tiles, and the tiles are
swapped, rotated and flipped at random. You click the tiles to put the picture back together.

## How to run
pip install -r requirements.txt
python main.py

## How to play
- Choose a grid size (3x3, 4x4 or 5x5), then click Load Image
- Left click a tile to select it, then left click another tile to swap them
- Left click the same tile again to deselect it
- Right click a tile to rotate it 90 degrees clockwise
- Shift + left click a tile to flip it horizontally
- A green tick shows on tiles that are in the right place
- Hint shows a blue circle on a wrong tile and where it belongs (3 per image)
- Solve finishes the puzzle for you

## Files
- main.py - starts the app
- gui.py - the Tkinter window (PuzzleApp class)
- puzzle.py - the game logic (Puzzle class)
- tile.py - one puzzle piece (Tile class)
- transformations.py - Swap, Rotate and Flip (Transformation classes)
- test_puzzle.py - tests the game logic without the window
- test_output.txt, result.png, screenshot_*.png - outputs

## OOP used
- Encapsulation: tile and puzzle data is private (starts with _), changed only through methods
- Inheritance: SwapTransformation, RotateTransformation and FlipTransformation inherit from Transformation
- Polymorphism: each transformation has its own apply(), and the puzzle calls apply() on all of them the same way
- Class interaction: PuzzleApp uses Puzzle, Puzzle creates Tile objects and uses Transformation objects