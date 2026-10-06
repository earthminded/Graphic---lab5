import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    v = max_c
    delta = max_c - min_c

    if max_c == 0:
        s = 0.0
    else:
        s = delta / max_c

    if delta == 0:
        h = 0.0
    elif max_c == r:
        h = (60.0 * ((g - b) / delta)) % 360.0
    elif max_c == g:
        h = (60.0 * ((b - r) / delta) + 120.0) % 360.0
    else:
        h = (60.0 * ((r - g) / delta) + 240.0) % 360.0

    return h, s, v


def hsv_to_rgb(h, s, v):
    hi = int(h // 60) % 6
    f = (h / 60.0) - int(h // 60)
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)

    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Преобразование изображений")
        self.root.geometry("1100x680")

        self.img1 = None
        self.img2 = None
        self.proc_img = None
        self.blend_img = None

        self.tk_img1 = None
        self.tk_proc = None
        self.tk_img2 = None
        self.tk_blend = None

        container = tk.Frame(root, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=0)
        container.columnconfigure(2, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        self.canvas1 = tk.Canvas(container, bg="white", highlightthickness=1, highlightbackground="white")
        self.canvas1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        btn_box1 = tk.Frame(container, bg="#f0f0f0")
        btn_box1.grid(row=0, column=1, padx=10, pady=10)

        tk.Button(btn_box1, text="Открыть 1 фото", width=14, command=self.load_image1).pack(pady=4)
        tk.Button(btn_box1, text="Преобразовать", width=14, command=self.process_image).pack(pady=4)
        tk.Button(btn_box1, text="Сохранить", width=14, command=lambda: self.save_file(self.proc_img)).pack(pady=4)

        self.canvas_proc = tk.Canvas(container, bg="white", highlightthickness=1, highlightbackground="white")
        self.canvas_proc.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        self.canvas2 = tk.Canvas(container, bg="white", highlightthickness=1, highlightbackground="white")
        self.canvas2.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        btn_box2 = tk.Frame(container, bg="#f0f0f0")
        btn_box2.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(btn_box2, text="Открыть 2 фото", width=14, command=self.load_image2).pack(pady=4)
        tk.Button(btn_box2, text="Наложить", width=14, command=self.blend_images).pack(pady=4)
        tk.Button(btn_box2, text="Сохранить", width=14, command=lambda: self.save_file(self.blend_img)).pack(pady=4)

        self.canvas_blend = tk.Canvas(container, bg="white", highlightthickness=1, highlightbackground="white")
        self.canvas_blend.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

    def load_image1(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.bmp *.png *.jpg *.jpeg *.ppm")])
        if not path:
            return
        self.img1 = Image.open(path).convert("RGB")
        self.show_image(self.img1, self.canvas1, 1)

    def load_image2(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.bmp *.png *.jpg *.jpeg *.ppm")])
        if not path:
            return
        self.img2 = Image.open(path).convert("RGB")
        self.show_image(self.img2, self.canvas2, 2)

    def process_image(self):
        if self.img1 is None:
            messagebox.showwarning("Предупреждение", "Сначала откройте 1 фото!")
            return

        w, h = self.img1.size
        res = Image.new("RGB", (w, h))
        src = self.img1.load()
        dst = res.load()

        threshold = 0.5
        for y in range(h):
            for x in range(w):
                r, g, b = src[x, y]
                h_val, s_val, v_val = rgb_to_hsv(r, g, b)
                s_bin = 1.0 if s_val >= threshold else 0.0
                dst[x, y] = hsv_to_rgb(h_val, s_bin, v_val)

        self.proc_img = res
        self.show_image(self.proc_img, self.canvas_proc, 3)

    def blend_images(self):
        if self.img1 is None or self.img2 is None:
            messagebox.showwarning("Предупреждение", "Сначала откройте оба фото!")
            return

        w = min(self.img1.width, self.img2.width)
        h = min(self.img1.height, self.img2.height)

        res = Image.new("RGB", (w, h))
        p1 = self.img1.load()
        p2 = self.img2.load()
        dst = res.load()

        for y in range(h):
            for x in range(w):
                r1, g1, b1 = p1[x, y]
                r2, g2, b2 = p2[x, y]

                r_res = int(round(r1 + 2 * r2 - 255))
                g_res = int(round(g1 + 2 * g2 - 255))
                b_res = int(round(b1 + 2 * b2 - 255))

                r_res = max(0, min(255, r_res))
                g_res = max(0, min(255, g_res))
                b_res = max(0, min(255, b_res))

                dst[x, y] = (r_res, g_res, b_res)

        self.blend_img = res
        self.show_image(self.blend_img, self.canvas_blend, 4)

    def show_image(self, img, canvas, slot):
        c_w = canvas.winfo_width()
        c_h = canvas.winfo_height()
        if c_w <= 1 or c_h <= 1:
            c_w, c_h = 440, 270

        copy_img = img.copy()
        copy_img.thumbnail((c_w, c_h), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(copy_img)

        if slot == 1:
            self.tk_img1 = tk_img
        elif slot == 2:
            self.tk_img2 = tk_img
        elif slot == 3:
            self.tk_proc = tk_img
        elif slot == 4:
            self.tk_blend = tk_img

        canvas.delete("all")
        canvas.create_image(c_w // 2, c_h // 2, anchor="center", image=tk_img)

    def save_file(self, img):
        if img is None:
            messagebox.showwarning("Предупреждение", "Нет обработанного изображения для сохранения!")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".ppm",
            filetypes=[("PPM files", "*.ppm"), ("Bitmap (*.bmp)", "*.bmp"), ("PNG (*.png)", "*.png")]
        )
        if path:
            img.save(path)
            messagebox.showinfo("Сохранено", f"Файл сохранен: {path}")


if __name__ == "__main__":
    app_root = tk.Tk()
    App(app_root)
    app_root.mainloop()