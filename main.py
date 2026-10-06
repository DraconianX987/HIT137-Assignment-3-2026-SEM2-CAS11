import tkinter as tk

from gui import PuzzleApp


def main():
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()