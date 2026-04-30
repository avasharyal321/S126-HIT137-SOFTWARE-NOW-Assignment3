import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
from image_manager import ImageManager


class SpotTheDifferenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Spot The Difference')

        self.im_manager = ImageManager()
        self.display_size = (500, 500)
        self.scale = 1.0
        self.max_mistakes = 3

        self.found = []
        self.revealed = []
        self.mistakes = 0

        self.status_var = tk.StringVar(value='Load an image to start')
        tk.Label(root, textvariable=self.status_var).pack(pady=6)

        images_frame = tk.Frame(root)
        images_frame.pack(pady=6)
        self.left_label = tk.Label(images_frame)
        self.left_label.pack(side='left', padx=6)
        self.right_label = tk.Label(images_frame)
        self.right_label.pack(side='left', padx=6)
        self.right_label.bind('<Button-1>', self.on_click)

        buttons = tk.Frame(root)
        buttons.pack(pady=8)
        tk.Button(buttons, text='Load Image', command=self.load_image).pack(side='left', padx=4)
        tk.Button(buttons, text='Quit', command=root.quit).pack(side='left', padx=4)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[('Images', '*.png;*.jpg;*.jpeg;*.bmp')])
        if not path:
            return

        try:
            self.original_cv, self.modified_cv, self.diffs = self.im_manager.load_and_generate(path)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load image: {e}')
            return

        self.found = [False] * len(self.diffs)
        self.revealed = [False] * len(self.diffs)
        self.mistakes = 0
        self.update_status()
        self.update_display()

    def update_status(self):
        if not self.found:
            self.status_var.set('Load an image to start')
            return
        remaining = sum(1 for f in self.found if not f)
        self.status_var.set(f'Remaining: {remaining} | Mistakes: {self.mistakes}/{self.max_mistakes}')

    def cv_to_pil(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil.thumbnail(self.display_size, Image.LANCZOS)
        return pil

    def update_display(self):
        left_pil = self.cv_to_pil(self.original_cv).copy()
        right_pil = self.cv_to_pil(self.modified_cv).copy()

        draw_left = ImageDraw.Draw(left_pil)
        draw_right = ImageDraw.Draw(right_pil)

        _, w = self.modified_cv.shape[:2]
        disp_w, _ = right_pil.size
        self.scale = w / disp_w

        for i, diff in enumerate(self.diffs):
            cx, cy, r = diff.marker_for_display()
            dx = cx / self.scale
            dy = cy / self.scale
            rr = r / self.scale
            bbox = [dx - rr, dy - rr, dx + rr, dy + rr]

            if self.found[i]:
                draw_left.ellipse(bbox, outline='red', width=3)
                draw_right.ellipse(bbox, outline='red', width=3)

        self.left_imgtk = ImageTk.PhotoImage(left_pil)
        self.right_imgtk = ImageTk.PhotoImage(right_pil)
        self.left_label.configure(image=self.left_imgtk)
        self.right_label.configure(image=self.right_imgtk)

    def on_click(self, event):
        if not hasattr(self, 'diffs') or not self.diffs:
            return

        if all(self.found):
            return

        if self.mistakes >= self.max_mistakes:
            return

        x = int(event.x * self.scale)
        y = int(event.y * self.scale)

        matched = False
        for i, diff in enumerate(self.diffs):
            if not self.found[i] and diff.contains_point((x, y)):
                self.found[i] = True
                self.revealed[i] = True
                matched = True
                break

        if not matched:
            self.mistakes += 1

        self.update_status()
        self.update_display()

        if all(self.found):
            messagebox.showinfo('Result', 'You found all differences!')
        elif self.mistakes >= self.max_mistakes:
            messagebox.showinfo('Result', 'You reached 3 mistakes.')


if __name__ == '__main__':
    root = tk.Tk()
    app = SpotTheDifferenceApp(root)
    root.mainloop()
