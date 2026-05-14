import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import cv2
from image_manager import ImageManager


class SpotTheDifferenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Spot The Difference')
        # sensible default window size and minimums so UI is usable immediately
        default_w, default_h = 1100, 720
        self.root.geometry(f'{default_w}x{default_h}')
        self.root.minsize(900, 600)
        # center the window
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - default_w) // 2
        y = (sh - default_h) // 2
        try:
            self.root.geometry(f'{default_w}x{default_h}+{x}+{y}')
        except Exception:
            pass
        self.im_manager = ImageManager()

        # control buttons will be placed in the center area below images

        status_frame = tk.Frame(root, pady=4)
        status_frame.pack(fill='x')
        self.remaining_var = tk.StringVar(value='Remaining: 0')
        self.mistakes_var = tk.StringVar(value='Mistakes: 0')
        tk.Label(status_frame, textvariable=self.remaining_var).pack(side='left', padx=6)
        tk.Label(status_frame, textvariable=self.mistakes_var).pack(side='left', padx=6)

        # progress bar for found differences
        self.progress = ttk.Progressbar(status_frame, length=200, maximum=5)
        self.progress.pack(side='right', padx=6)
        self.mistakes_left_label = tk.Label(status_frame, text='Mistakes left: ♥♥♥', fg='red')
        self.mistakes_left_label.pack(side='right', padx=6)

        images_frame = tk.Frame(root, pady=8)
        images_frame.pack()

        self.left_label = tk.Label(images_frame, bd=2, relief='sunken')
        self.left_label.pack(side='left', padx=8)
        self.right_label = tk.Label(images_frame, bd=2, relief='sunken')
        self.right_label.pack(side='left', padx=8)

        self.right_label.bind('<Button-1>', self.on_click)

        self.display_size = (500, 500)
        self.scale = 1.0

        # center control buttons in the middle area
        center_frame = tk.Frame(root)
        center_frame.pack(expand=True, fill='both')
        control_frame = tk.Frame(center_frame)
        control_frame.place(relx=0.5, rely=0.5, anchor='center')

        ttk.Button(control_frame, text='Load Image', command=self.load_image).pack(side='left', padx=6)
        ttk.Button(control_frame, text='Reveal', command=self.reveal).pack(side='left', padx=6)
        ttk.Button(control_frame, text='Restart', command=self.restart_current).pack(side='left', padx=6)
        ttk.Button(control_frame, text='Quit', command=root.quit).pack(side='left', padx=6)

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
        self.session_found = 0
        self.game_over = False
        self.mistakes = 0
        self.update_status()
        self.update_display()

    def restart_current(self):
        if not hasattr(self, 'diffs'):
            return
        self.found = [False] * len(self.diffs)
        self.revealed = [False] * len(self.diffs)
        self.mistakes = 0
        self.update_status()
        self.update_display()

    def update_status(self):
        remaining = sum(1 for f in self.found if not f)
        self.remaining_var.set(f'Remaining: {remaining}')
        self.mistakes_var.set(f'Mistakes: {self.mistakes}/3')
        # update progress bar
        found = sum(1 for f in self.found if f)
        self.progress['value'] = found
        # update mistakes left label
        left = max(0, 3 - self.mistakes)
        hearts = '♥' * left + '♡' * (3 - left)
        self.mistakes_left_label.config(text=f'Mistakes left: {hearts}')

    def cv_to_tk(self, cv_img):
        # cv image BGR -> RGB
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        # fit into display_size while preserving aspect
        pil.thumbnail(self.display_size, Image.LANCZOS)
        return pil

    def update_display(self):
        left_pil = self.cv_to_tk(self.original_cv).copy()
        right_pil = self.cv_to_tk(self.modified_cv).copy()

        # draw markers for found differences
        ld = ImageDraw.Draw(left_pil)
        rd = ImageDraw.Draw(right_pil)

        # compute scale between original image and displayed image
        h, w = self.modified_cv.shape[:2]
        disp_w, disp_h = right_pil.size
        self.scale = w / disp_w

        for i, diff in enumerate(self.diffs):
            cx, cy, r = diff.marker_for_display()
            ddx = cx / self.scale
            ddy = cy / self.scale
            rr = r / self.scale
            bbox = [ddx-rr, ddy-rr, ddx+rr, ddy+rr]
            if self.found[i]:
                ld.ellipse(bbox, outline='red', width=3)
                rd.ellipse(bbox, outline='red', width=3)
            elif self.revealed[i]:
                ld.ellipse(bbox, outline='blue', width=3)
                rd.ellipse(bbox, outline='blue', width=3)

        self.left_imgtk = ImageTk.PhotoImage(left_pil)
        self.right_imgtk = ImageTk.PhotoImage(right_pil)

        self.left_label.configure(image=self.left_imgtk)
        self.right_label.configure(image=self.right_imgtk)

    def on_click(self, event):
        if not hasattr(self, 'diffs') or not self.diffs:
            return
        if getattr(self, 'game_over', False):
            return
        if self.mistakes >= 3:
            # when out of guesses, show end dialog
            self.end_round('You reached 3 mistakes. Load a new image to try again.')
            return

        x = int(event.x * self.scale)
        y = int(event.y * self.scale)

        matched = False
        for i, diff in enumerate(self.diffs):
            if self.found[i]:
                continue
            if diff.contains_point((x, y)):
                self.found[i] = True
                self.revealed[i] = True
                matched = True
                break

        if not matched:
            self.mistakes += 1

        self.update_status()
        self.update_display()

        if sum(1 for f in self.found if not f) == 0:
            self.end_round('You found all differences! Choose Restart or Load New Image.')

        if self.mistakes >= 3:
            self.end_round('You reached 3 mistakes. Load a new image to try again.')

    def reveal(self):
        if not hasattr(self, 'diffs'):
            return
        for i in range(len(self.found)):
            if not self.found[i]:
                self.revealed[i] = True
        self.update_status()
        self.update_display()

    def end_round(self, message):
        # mark game over and show a modal dialog offering Restart or Load
        self.game_over = True
        dlg = tk.Toplevel(self.root)
        dlg.title('Round Complete')
        dlg.transient(self.root)
        dlg.resizable(False, False)

        # contents
        tk.Label(dlg, text=message, pady=10, padx=10).pack()
        btn_frame = tk.Frame(dlg, pady=8)
        btn_frame.pack()

        def do_load():
            dlg.destroy()
            self.load_image()

        def do_restart():
            dlg.destroy()
            self.restart_current()

        ttk.Button(btn_frame, text='Load New Image', command=do_load).pack(side='left', padx=6)
        ttk.Button(btn_frame, text='Restart', command=do_restart).pack(side='left', padx=6)
        ttk.Button(btn_frame, text='Close', command=dlg.destroy).pack(side='left', padx=6)

        # center dialog over main window
        self.root.update_idletasks()
        dlg.update_idletasks()
        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            dw = dlg.winfo_width()
            dh = dlg.winfo_height()
            x = rx + max(0, (rw - dw) // 2)
            y = ry + max(0, (rh - dh) // 2)
            dlg.geometry(f'+{x}+{y}')
        except Exception:
            pass

        dlg.grab_set()
        dlg.focus_set()
        dlg.wait_window()


if __name__ == '__main__':
    root = tk.Tk()
    app = SpotTheDifferenceApp(root)
    root.mainloop()