import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from puzzle import Puzzle


class PuzzleApp:

    CANVAS_SIZE = 600

    def __init__(self, root):
        self._root = root
        self._root.title("Scrambled Image Puzzle")

        self._puzzle = None
        self._selected_position = None
        self._locked = True

        self._grid_size_var = tk.IntVar(value=3)

        self._tk_original_image = None
        self._tk_transformed_image = None

        self._build_widgets()

    def _build_widgets(self):
        control_frame = tk.Frame(self._root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        tk.Button(control_frame, text="Load Image", command=self._on_load_image).pack(
            side=tk.LEFT, padx=4
        )

        tk.Label(control_frame, text="Grid size:").pack(side=tk.LEFT, padx=(16, 4))
        for size in (3, 4, 5):
            tk.Radiobutton(
                control_frame, text=f"{size}x{size}",
                variable=self._grid_size_var, value=size
            ).pack(side=tk.LEFT)

        self._hint_button = tk.Button(
            control_frame, text="Hint", command=self._on_hint, state=tk.DISABLED
        )
        self._hint_button.pack(side=tk.LEFT, padx=(16, 4))

        self._solve_button = tk.Button(
            control_frame, text="Solve", command=self._on_solve, state=tk.DISABLED
        )
        self._solve_button.pack(side=tk.LEFT, padx=4)

        status_frame = tk.Frame(self._root)
        status_frame.pack(side=tk.TOP, fill=tk.X, padx=8)

        self._moves_label = tk.Label(status_frame, text="Moves: 0")
        self._moves_label.pack(side=tk.LEFT, padx=4)

        self._incorrect_label = tk.Label(status_frame, text="Incorrect tiles: 0")
        self._incorrect_label.pack(side=tk.LEFT, padx=4)

        images_frame = tk.Frame(self._root)
        images_frame.pack(side=tk.TOP, padx=8, pady=8)

        left_frame = tk.Frame(images_frame)
        left_frame.pack(side=tk.LEFT, padx=8)
        tk.Label(left_frame, text="Original (reference only)").pack()
        self._original_canvas = tk.Canvas(
            left_frame, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE, bg="gray90"
        )
        self._original_canvas.pack()

        right_frame = tk.Frame(images_frame)
        right_frame.pack(side=tk.LEFT, padx=8)
        tk.Label(right_frame, text="Scrambled (click to solve)").pack()
        self._puzzle_canvas = tk.Canvas(
            right_frame, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE, bg="gray90"
        )
        self._puzzle_canvas.pack()

        self._puzzle_canvas.bind("<Button-1>", self._on_left_click)
        self._puzzle_canvas.bind("<Shift-Button-1>", self._on_shift_left_click)
        self._puzzle_canvas.bind("<Button-3>", self._on_right_click)
        if sys.platform == "darwin":
            # on a Mac, right click is Button-2
            self._puzzle_canvas.bind("<Button-2>", self._on_right_click)

    def _on_load_image(self):
        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return

        grid_size = self._grid_size_var.get()
        puzzle = Puzzle(grid_size)
        try:
            puzzle.load_image(path)
        except ValueError as error:
            messagebox.showerror("Could not load image", str(error))
            return

        self._puzzle = puzzle
        self._selected_position = None
        self._locked = False
        self._hint_button.config(state=tk.NORMAL)
        self._solve_button.config(state=tk.NORMAL)
        self._redraw()

    def _tile_size(self):
        image = self._puzzle.get_original_image()
        height, width = image.shape[:2]
        n = self._puzzle.grid_size
        return height // n, width // n

    def _event_to_position(self, event):
        tile_h, tile_w = self._tile_size()
        n = self._puzzle.grid_size
        col = min(max(event.x // tile_w, 0), n - 1)
        row = min(max(event.y // tile_h, 0), n - 1)
        return row, col

    def _on_left_click(self, event):
        if self._locked or self._puzzle is None:
            return

        position = self._event_to_position(event)

        if self._selected_position is None:
            self._selected_position = position
            self._redraw()
        elif self._selected_position == position:
            self._selected_position = None
            self._redraw()
        else:
            self._puzzle.swap_tiles(self._selected_position, position)
            self._selected_position = None
            self._after_move()

    def _on_shift_left_click(self, event):
        if self._locked or self._puzzle is None:
            return

        position = self._event_to_position(event)
        self._puzzle.flip_tile(position, 'horizontal')
        self._selected_position = None
        self._after_move()

    def _on_right_click(self, event):
        if self._locked or self._puzzle is None:
            return

        position = self._event_to_position(event)
        self._puzzle.rotate_tile(position)
        self._selected_position = None
        self._after_move()

    def _after_move(self):
        self._redraw()
        if self._puzzle.is_solved:
            self._locked = True
            self._hint_button.config(state=tk.DISABLED)
            messagebox.showinfo(
                "Solved!", f"You solved it in {self._puzzle.moves} moves. "
                           "Load another image to keep playing."
            )

    def _on_hint(self):
        if self._puzzle is None or self._locked:
            return

        result = self._puzzle.request_hint()
        if result is None and self._puzzle.hints_remaining() <= 0:
            messagebox.showinfo("No hints left", "You've used all 3 hints for this image.")

        if self._puzzle.hints_remaining() <= 0:
            self._hint_button.config(state=tk.DISABLED)

        self._redraw()

    def _on_solve(self):
        if self._puzzle is None:
            return

        self._puzzle.solve()
        self._selected_position = None
        self._locked = True
        self._hint_button.config(state=tk.DISABLED)
        self._redraw()
        messagebox.showinfo("Solved", "The puzzle has been solved for you.")

    def _redraw(self):
        if self._puzzle is None:
            return

        self._draw_original()
        self._draw_transformed()
        self._moves_label.config(text=f"Moves: {self._puzzle.moves}")
        self._incorrect_label.config(
            text=f"Incorrect tiles: {self._puzzle.incorrect_count()}"
        )

    def _draw_original(self):
        image = self._puzzle.get_original_image()
        self._tk_original_image = self._to_photo_image(image)

        self._original_canvas.delete("all")
        self._original_canvas.config(width=image.shape[1], height=image.shape[0])
        self._original_canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_original_image)

        _, hint_home_pos = self._puzzle.active_hint()
        if hint_home_pos is not None:
            self._draw_circle_at(self._original_canvas, hint_home_pos, 'blue')

    def _draw_transformed(self):
        image = self._puzzle.reassemble()
        self._tk_transformed_image = self._to_photo_image(image)

        self._puzzle_canvas.delete("all")
        self._puzzle_canvas.config(width=image.shape[1], height=image.shape[0])
        self._puzzle_canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_transformed_image)

        tile_h, tile_w = self._tile_size()
        n = self._puzzle.grid_size

        for i in range(1, n):
            self._puzzle_canvas.create_line(
                i * tile_w, 0, i * tile_w, image.shape[0], fill='gray70'
            )
            self._puzzle_canvas.create_line(
                0, i * tile_h, image.shape[1], i * tile_h, fill='gray70'
            )

        if self._selected_position is not None:
            row, col = self._selected_position
            self._puzzle_canvas.create_rectangle(
                col * tile_w, row * tile_h, (col + 1) * tile_w, (row + 1) * tile_h,
                outline='red', width=3
            )

        for row in range(n):
            for col in range(n):
                if self._puzzle.tile_at((row, col)).is_correct():
                    x = col * tile_w + 10
                    y = row * tile_h + 10
                    self._puzzle_canvas.create_text(
                        x, y, text="\u2714", fill='green',
                        font=('Arial', 14, 'bold'), anchor=tk.NW
                    )

        hint_tile_pos, _ = self._puzzle.active_hint()
        if hint_tile_pos is not None:
            self._draw_circle_at(self._puzzle_canvas, hint_tile_pos, 'blue')

    def _draw_circle_at(self, canvas, position, color):
        tile_h, tile_w = self._tile_size()
        row, col = position
        cx = col * tile_w + tile_w / 2
        cy = row * tile_h + tile_h / 2
        radius = min(tile_w, tile_h) / 4
        canvas.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius,
            outline=color, width=3
        )

    def _to_photo_image(self, image_bgr):
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        return ImageTk.PhotoImage(pil_image)