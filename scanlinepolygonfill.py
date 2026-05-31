import tkinter as tk
POLYGON = [
    (155, 85), (200, 160), (105, 220), (165, 245), 
    (145, 310), (220, 270), (265, 345), (310, 275), 
    (380, 355), (415, 270), (500, 310), (510, 250),  
    (620, 285), (590, 200), (660, 115), (565, 140),  
    (510, 50), (430, 130), (345, 30), (310, 130), 
    (235, 55), (240, 145),
]

def build_edge_table(polygon):
    et = {}
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if y1 == y2:
            continue
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        slope_inv = (x2 - x1) / (y2 - y1)
        entry = {"y_max": y2, "x": float(x1), "slope_inv": slope_inv}
        et.setdefault(y1, []).append(entry)
    return et

def scan_line_fill(polygon):
    et  = build_edge_table(polygon)
    ael = []
    result = {}
    y_min = min(p[1] for p in polygon)
    y_max = max(p[1] for p in polygon)
    for y in range(y_min, y_max + 1):
        if y in et:
            ael.extend([dict(e) for e in et[y]])
        ael = [e for e in ael if e["y_max"] > y]
        ael.sort(key=lambda e: e["x"])
        spans = []
        for i in range(0, len(ael) - 1, 2):
            spans.append((round(ael[i]["x"]), round(ael[i + 1]["x"])))
        if spans:
            result[y] = spans
        for e in ael:
            e["x"] += e["slope_inv"]
    return result

class App:
    def __init__(self, root):
        self.root = root
        root.title("Scan Line Polygon Fill")

        self.canvas = tk.Canvas(root, width=780, height=420, bg="#1a1a2e")
        self.canvas.pack(padx=10, pady=8)

        info = tk.Frame(root, bg="#111")
        info.pack(fill="x", padx=10)
        self.lbl_y   = tk.Label(info, text="Scan line  y = -",
                                fg="#aaa", bg="#111", font=("Courier", 11))
        self.lbl_y.pack(side="left", padx=8, pady=4)
        self.lbl_ael = tk.Label(info, text="AEL = 0 sisi  |  interseksi = 0",
                                fg="#aaa", bg="#111", font=("Courier", 11))
        self.lbl_ael.pack(side="left", padx=8)

        f = tk.Frame(root)
        f.pack(pady=6)
        tk.Button(f, text="Animasi",   width=12, command=self.start_anim).grid(row=0, column=0, padx=4)
        tk.Button(f, text="Langsung",  width=12, command=self.draw_all).grid(row=0, column=1, padx=4)
        tk.Button(f, text="Reset",     width=12, command=self.reset).grid(row=0, column=2, padx=4)
        tk.Label(f, text="Delay (ms):").grid(row=0, column=3, padx=(12, 2))
        self.speed = tk.IntVar(value=15)
        tk.Scale(f, from_=1, to=80, orient="horizontal",
                 variable=self.speed, length=110).grid(row=0, column=4)

        self.spans   = {}
        self.running = False
        self._draw_outline()

    def _draw_outline(self):
        flat = [v for pt in POLYGON for v in pt]
        self.canvas.create_polygon(*flat, outline="#7de0ff", fill="", width=2)
        for i, (x, y) in enumerate(POLYGON):
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="#7de0ff", outline="")

    def reset(self):
        self.running = False
        self.spans   = {}
        self.canvas.delete("all")
        self._draw_outline()
        self.lbl_y.config(text="Scan line  y = -")
        self.lbl_ael.config(text="AEL = 0 sisi  |  interseksi = 0")

    def _color(self, y, y_min, y_max):
        t = (y - y_min) / max(y_max - y_min, 1)
        r = int(180 + t * 60)
        g = int(160 - t * 80)
        b = 60
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_all(self):
        self.reset()
        self.spans = scan_line_fill(POLYGON)
        y_min = min(p[1] for p in POLYGON)
        y_max = max(p[1] for p in POLYGON)
        for y in range(y_min, y_max + 1):
            if y in self.spans:
                c = self._color(y, y_min, y_max)
                for xs, xe in self.spans[y]:
                    self.canvas.create_line(xs, y, xe, y, fill=c, width=1)
        flat = [v for pt in POLYGON for v in pt]
        self.canvas.create_polygon(*flat, outline="#7de0ff", fill="", width=2)
        self.lbl_y.config(text="Selesai")
        self.lbl_ael.config(text=f"Total scan lines: {y_max - y_min + 1}")

    def start_anim(self):
        if self.running:
            return
        self.reset()
        self.spans     = scan_line_fill(POLYGON)
        self._et       = build_edge_table(POLYGON)
        self._ael_info = []
        self._y_min    = min(p[1] for p in POLYGON)
        self._y_max    = max(p[1] for p in POLYGON)
        self._cur_y    = self._y_min
        self.running   = True
        self._step()

    def _step(self):
        if not self.running:
            return
        y = self._cur_y
        if y > self._y_max:
            self.running = False
            flat = [v for pt in POLYGON for v in pt]
            self.canvas.create_polygon(*flat, outline="#7de0ff", fill="", width=2)
            self.lbl_y.config(text=f"Selesai  (y_max = {self._y_max})")
            return

        if y in self._et:
            self._ael_info.extend(self._et[y])
        self._ael_info = [e for e in self._ael_info if e["y_max"] > y]

        if y in self.spans:
            c = self._color(y, self._y_min, self._y_max)
            for xs, xe in self.spans[y]:
                self.canvas.create_line(xs, y, xe, y, fill=c, width=1)

        sl = self.canvas.create_line(0, y, 780, y, fill="#ff4444", width=1, dash=(4, 3))
        dots = []
        palette = ["#4cffb3", "#ff6bca"]
        if y in self.spans:
            for xs, xe in self.spans[y]:
                for j, ix in enumerate([xs, xe]):
                    d = self.canvas.create_oval(ix-4, y-4, ix+4, y+4,
                                                fill=palette[j % 2], outline="white")
                    dots.append(d)

        n_int = sum(2 for _ in self.spans.get(y, []))
        self.lbl_y.config(text=f"Scan line  y = {y}")
        self.lbl_ael.config(text=f"AEL = {len(self._ael_info)} sisi  |  interseksi = {n_int}")

        self._cur_y += 1

        def next_step():
            self.canvas.delete(sl)
            for d in dots:
                self.canvas.delete(d)
            self._step()

        self.root.after(self.speed.get(), next_step)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()