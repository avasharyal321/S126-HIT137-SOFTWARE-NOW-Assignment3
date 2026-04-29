import tkinter as tk
from tkinter import filedialog, messagebox
from image_manager import ImageManager


class SpotTheDifferenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Spot The Difference')
        self.im_manager = ImageManager()

    def load_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            self.original_cv, self.modified_cv, self.diffs = self.im_manager.load_and_generate(path)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load image: {e}')


if __name__ == '__main__':
    root = tk.Tk()
    app = SpotTheDifferenceApp(root)
    root.mainloop()