# main application ui

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import os

from .i18n import _, register_language, set_language, on_change, get_languages
from .core import FlagGenerator, DEFAULT_COLORS
from .models import Layer, Stripe
from .widgets import ColorPickerRow, LayerRow, StripeRow


register_language("en", "English", {
    "title": "Tricolor Flag Generator",
    "preview": "Preview",
    "size": "Canvas Size",
    "width": "Width",
    "height": "Height",
    "colors": "Colors",
    "stripes": "Stripes",
    "add_stripe": "Add Stripe",
    "reset_colors": "Reset Colors",
    "layers": "Image Layers",
    "add_layer": "Add Image",
    "drag": "Drag",
    "angle": "Angle",
    "w": "W",
    "h": "H",
    "export": "Export",
    "export_crop": "Export with Crop",
    "crop_ratio": "Crop Ratio",
    "custom": "Custom",
    "stripe_n": "Stripe {n}",
    "ready": "Ready",
    "icon_loaded": "Layer added: {name}",
    "icon_cleared": "Layer removed",
    "saved": "Saved: {name}",
    "language": "Language",
    "theme": "Theme",
    "dark": "Dark",
    "light": "Light",
    "no_image": "No image selected",
    "export_size": "Export Size",
    "export_width": "Export W",
    "export_height": "Export H",
    "all_images": "All Images",
    "webp": "WebP",
    "tiff": "TIFF",
    "bmp": "BMP",
    "ico": "ICO",
    "jpg": "JPEG",
})

register_language("zh", "中文", {
    "title": "三色旗生成器",
    "preview": "预览",
    "size": "画布尺寸",
    "width": "宽度",
    "height": "高度",
    "colors": "颜色",
    "stripes": "条纹",
    "add_stripe": "添加条纹",
    "reset_colors": "重置颜色",
    "layers": "图像图层",
    "add_layer": "添加图像",
    "drag": "拖动",
    "angle": "角度",
    "w": "宽",
    "h": "高",
    "export": "导出",
    "export_crop": "裁剪导出",
    "crop_ratio": "裁剪比例",
    "custom": "自定义",
    "stripe_n": "条纹 {n}",
    "ready": "就绪",
    "icon_loaded": "已添加图层: {name}",
    "icon_cleared": "图层已移除",
    "saved": "已保存: {name}",
    "language": "语言",
    "theme": "主题",
    "dark": "深色",
    "light": "浅色",
    "no_image": "未选择图像",
    "export_size": "导出尺寸",
    "export_width": "导出宽度",
    "export_height": "导出高度",
    "all_images": "所有图像",
    "webp": "WebP",
    "tiff": "TIFF",
    "bmp": "BMP",
    "ico": "ICO",
    "jpg": "JPEG",
})


class App:
    def __init__(self, root):
        self.root = root
        self.root.title(_("title"))
        self.root.geometry("1300x900")
        self.root.minsize(900, 600)

        self.generator = FlagGenerator()
        self.preview_tk = None
        self.color_rows = []
        self.layer_rows = []
        self.stripe_rows = []

        self._drag_layer_idx = None
        self._drag_start = None

        self.build_ui()
        on_change(self.refresh_ui_text)
        self.update_preview()

    def build_ui(self):
        self.top_bar = ctk.CTkFrame(self.root, height=48, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)

        ctk.CTkLabel(self.top_bar, text=_("title"), font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=16)

        self.lang_menu = ctk.CTkOptionMenu(
            self.top_bar, width=120,
            values=[v for _, v in get_languages()],
            command=self.switch_language
        )
        self.lang_menu.pack(side="right", padx=8)
        self.lang_label = ctk.CTkLabel(self.top_bar, text=_("language") + ":")
        self.lang_label.pack(side="right")

        self.theme_menu = ctk.CTkOptionMenu(
            self.top_bar, width=100,
            values=[_("dark"), _("light")],
            command=self.switch_theme
        )
        self.theme_menu.pack(side="right", padx=16)
        self.theme_label = ctk.CTkLabel(self.top_bar, text=_("theme") + ":")
        self.theme_label.pack(side="right")

        self.main = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=12, pady=12)

        # controls (right, pack first) with both scroll directions
        self.ctrl_panel = ctk.CTkFrame(self.main, width=420, corner_radius=12)
        self.ctrl_panel.pack(side="right", fill="y")
        self.ctrl_panel.pack_propagate(False)

        # horizontal scrollbar at bottom
        self.h_scroll = tk.Scrollbar(self.ctrl_panel, orient="horizontal", command=self._on_hscroll)
        self.h_scroll.pack(side="bottom", fill="x")

        # vertical scrollbar at right
        self.v_scroll = tk.Scrollbar(self.ctrl_panel, orient="vertical")
        self.v_scroll.pack(side="right", fill="y")

        # canvas in the middle
        self.ctrl_canvas = tk.Canvas(
            self.ctrl_panel,
            highlightthickness=0,
            bg="#2b2b2b",
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
        )
        self.ctrl_canvas.pack(side="left", fill="both", expand=True)
        self.v_scroll.configure(command=self.ctrl_canvas.yview)

        self.ctrl_inner = ctk.CTkFrame(self.ctrl_canvas, fg_color="transparent", corner_radius=0)
        self.inner_id = self.ctrl_canvas.create_window((0, 0), window=self.ctrl_inner, anchor="nw", width=400)

        def _on_configure(event):
            self.ctrl_canvas.configure(scrollregion=self.ctrl_canvas.bbox("all"))
        self.ctrl_inner.bind("<Configure>", _on_configure)

        self.build_controls()

        # preview (left)
        self.preview_card = ctk.CTkFrame(self.main, corner_radius=12)
        self.preview_card.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.preview_title = ctk.CTkLabel(self.preview_card, text=_("preview"), font=ctk.CTkFont(size=14, weight="bold"))
        self.preview_title.pack(anchor="w", padx=16, pady=(12, 8))

        self.canvas = ctk.CTkCanvas(self.preview_card, highlightthickness=0, bg="#1a1a1a")
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.canvas.bind("<Configure>", lambda e: self.update_preview())
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)

    def build_controls(self):
        for w in self.ctrl_inner.winfo_children():
            w.destroy()
        self.color_rows.clear()
        self.layer_rows.clear()
        self.stripe_rows.clear()

        # size
        size_card = ctk.CTkFrame(self.ctrl_inner, corner_radius=10)
        size_card.pack(fill="x", pady=(0, 10), padx=2)
        ctk.CTkLabel(size_card, text=_("size"), font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(10, 8))

        row1 = ctk.CTkFrame(size_card, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(row1, text=_("width") + ":", width=70).pack(side="left")
        self.w_entry = ctk.CTkEntry(row1, width=90)
        self.w_entry.insert(0, str(self.generator.width))
        self.w_entry.pack(side="left")
        self.w_entry.bind("<Return>", lambda e: self.on_size_change())
        self.w_entry.bind("<FocusOut>", lambda e: self.on_size_change())

        row2 = ctk.CTkFrame(size_card, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(row2, text=_("height") + ":", width=70).pack(side="left")
        self.h_entry = ctk.CTkEntry(row2, width=90)
        self.h_entry.insert(0, str(self.generator.height))
        self.h_entry.pack(side="left")
        self.h_entry.bind("<Return>", lambda e: self.on_size_change())
        self.h_entry.bind("<FocusOut>", lambda e: self.on_size_change())

        # export size
        ctk.CTkLabel(size_card, text=_("export_size"), font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))
        ex_row = ctk.CTkFrame(size_card, fg_color="transparent")
        ex_row.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(ex_row, text=_("export_width") + ":", width=80).pack(side="left")
        self.ex_w_entry = ctk.CTkEntry(ex_row, width=70)
        self.ex_w_entry.insert(0, str(self.generator.width))
        self.ex_w_entry.pack(side="left")
        ctk.CTkLabel(ex_row, text=_("export_height") + ":", width=80).pack(side="left", padx=(8, 0))
        self.ex_h_entry = ctk.CTkEntry(ex_row, width=70)
        self.ex_h_entry.insert(0, str(self.generator.height))
        self.ex_h_entry.pack(side="left")

        ctk.CTkButton(size_card, text=_("export"), command=self.export).pack(fill="x", padx=12, pady=(10, 6))

        # crop export
        crop_frame = ctk.CTkFrame(size_card, fg_color="transparent")
        crop_frame.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(crop_frame, text=_("crop_ratio") + ":").pack(side="left")
        self.ratio_var = ctk.StringVar(value="original")
        self.ratio_menu = ctk.CTkOptionMenu(crop_frame, values=["original", "16:9", "4:3", "1:1", _("custom")], variable=self.ratio_var, width=120)
        self.ratio_menu.pack(side="left", padx=4)
        ctk.CTkButton(size_card, text=_("export_crop"), command=self.export_crop).pack(fill="x", padx=12, pady=(0, 12))

        # stripes
        stripe_card = ctk.CTkFrame(self.ctrl_inner, corner_radius=10)
        stripe_card.pack(fill="x", pady=(0, 10), padx=2)
        ctk.CTkLabel(stripe_card, text=_("stripes"), font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(10, 8))

        ctk.CTkButton(stripe_card, text=_("add_stripe"), command=self.add_stripe).pack(fill="x", padx=12, pady=(0, 8))

        self.stripes_container = ctk.CTkFrame(stripe_card, fg_color="transparent")
        self.stripes_container.pack(fill="x", padx=12, pady=(0, 12))

        for i, stripe in enumerate(self.generator.stripes):
            row = StripeRow(self.stripes_container, stripe, i, self.update_preview, self.remove_stripe)
            row.pack(fill="x", pady=3)
            self.stripe_rows.append(row)

        # colors shortcut
        color_card = ctk.CTkFrame(self.ctrl_inner, corner_radius=10)
        color_card.pack(fill="x", pady=(0, 10), padx=2)
        ctk.CTkLabel(color_card, text=_("colors"), font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(10, 8))

        for i, stripe in enumerate(self.generator.stripes):
            row = ColorPickerRow(color_card, i, stripe.color, self.on_color_change)
            row.pack(fill="x", padx=12, pady=3)
            self.color_rows.append(row)

        ctk.CTkButton(color_card, text=_("reset_colors"), command=self.reset_colors).pack(fill="x", padx=12, pady=(8, 12))

        # layers
        layer_card = ctk.CTkFrame(self.ctrl_inner, corner_radius=10)
        layer_card.pack(fill="x", pady=(0, 10), padx=2)
        ctk.CTkLabel(layer_card, text=_("layers"), font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(10, 8))

        ctk.CTkButton(layer_card, text=_("add_layer"), command=self.add_layer).pack(fill="x", padx=12, pady=(0, 8))

        self.layers_container = ctk.CTkFrame(layer_card, fg_color="transparent")
        self.layers_container.pack(fill="x", padx=12, pady=(0, 12))

        self.refresh_layer_list()

        # status
        self.status_label = ctk.CTkLabel(self.ctrl_inner, text=_("ready"), text_color=("gray50", "gray60"))
        self.status_label.pack(anchor="w", padx=4, pady=(0, 20))

    def refresh_layer_list(self):
        for w in self.layers_container.winfo_children():
            w.destroy()
        self.layer_rows.clear()
        for idx, layer in enumerate(self.generator.layers):
            row = LayerRow(self.layers_container, layer, idx, self.update_preview, self.remove_layer)
            row.pack(fill="x", pady=3)
            self.layer_rows.append(row)

    def add_stripe(self):
        n = len(self.generator.stripes) + 1
        stripe = Stripe("#55CDFC")
        stripe.y = (n - 0.5) / n
        stripe.height = 1.0 / n
        # redistribute existing stripes
        for i, s in enumerate(self.generator.stripes):
            s.y = (i + 0.5) / n
            s.height = 1.0 / n
        self.generator.stripes.append(stripe)
        self.build_controls()
        self.update_preview()

    def remove_stripe(self, idx):
        if len(self.generator.stripes) > 1 and 0 <= idx < len(self.generator.stripes):
            self.generator.stripes.pop(idx)
            self.build_controls()
            self.update_preview()

    def on_color_change(self, idx, field, color):
        if 0 <= idx < len(self.generator.stripes):
            self.generator.stripes[idx].color = color
            self.update_preview()

    def reset_colors(self):
        for i, c in enumerate(DEFAULT_COLORS):
            if i < len(self.generator.stripes):
                self.generator.stripes[i].color = c
        self.build_controls()
        self.update_preview()

    def add_layer(self):
        path = filedialog.askopenfilename(
            filetypes=[
                (_("all_images"), "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp;*.tiff;*.tif;*.ico"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("GIF", "*.gif"),
                ("WebP", "*.webp"),
                ("TIFF", "*.tiff;*.tif"),
                ("BMP", "*.bmp"),
                ("ICO", "*.ico"),
            ]
        )
        if path:
            try:
                img = Image.open(path).convert("RGBA")
                layer = Layer(img, os.path.basename(path))
                self.generator.layers.append(layer)
                self.status_label.configure(text=_("icon_loaded", name=layer.name))
                self.refresh_layer_list()
                self.update_preview()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def remove_layer(self, idx):
        if 0 <= idx < len(self.generator.layers):
            self.generator.layers.pop(idx)
            self.status_label.configure(text=_("icon_cleared"))
            self.refresh_layer_list()
            self.update_preview()

    def _on_hscroll(self, *args):
        self.ctrl_canvas.xview(*args)

    def on_drag_start(self, event):
        self._drag_layer_idx = None
        self._drag_start = (event.x, event.y)
        for idx in reversed(range(len(self.generator.layers))):
            layer = self.generator.layers[idx]
            if not layer.visible or not layer.drag_enabled:
                continue
            self._drag_layer_idx = idx
            break

    def on_drag_move(self, event):
        if self._drag_layer_idx is None:
            return
        layer = self.generator.layers[self._drag_layer_idx]
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        self._drag_start = (event.x, event.y)
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw > 0 and ch > 0:
            layer.x += dx / cw
            layer.y += dy / ch
            self.update_preview()

    def on_drag_end(self, event):
        self._drag_layer_idx = None
        self._drag_start = None

    def apply_size(self):
        try:
            w = int(self.w_entry.get())
            h = int(self.h_entry.get())
            if w >= 50 and h >= 50:
                self.generator.width = w
                self.generator.height = h
        except ValueError:
            pass

    def on_size_change(self):
        self.apply_size()
        self.update_preview()

    def update_preview(self):
        self.apply_size()
        img = self.generator.generate()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 20 or ch < 20:
            cw, ch = 600, 400
        preview = img.copy()
        preview.thumbnail((cw - 24, ch - 24), Image.Resampling.LANCZOS)
        self.preview_tk = ImageTk.PhotoImage(preview)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.preview_tk)

    def export(self):
        self.apply_size()
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("WebP", "*.webp"),
                ("TIFF", "*.tiff;*.tif"),
                ("BMP", "*.bmp"),
                ("ICO", "*.ico"),
            ]
        )
        if path:
            try:
                img = self.generator.generate()
                # resize if export size differs
                try:
                    ew = int(self.ex_w_entry.get())
                    eh = int(self.ex_h_entry.get())
                    if ew >= 1 and eh >= 1 and (ew != self.generator.width or eh != self.generator.height):
                        img = img.resize((ew, eh), Image.Resampling.LANCZOS)
                except ValueError:
                    pass
                img.save(path)
                self.status_label.configure(text=_("saved", name=os.path.basename(path)))
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_crop(self):
        self.apply_size()
        ratio_str = self.ratio_var.get()
        if ratio_str == "original":
            self.export()
            return

        if ratio_str == _("custom"):
            dialog = ctk.CTkInputDialog(text="Enter ratio like 16:9 or 2.35", title="Custom Ratio")
            val = dialog.get_input()
            if not val:
                return
            try:
                if ":" in val:
                    a, b = val.split(":")
                    ratio = float(a) / float(b)
                else:
                    ratio = float(val)
            except ValueError:
                messagebox.showerror("Error", "Invalid ratio")
                return
        elif ":" in ratio_str:
            a, b = ratio_str.split(":")
            ratio = float(a) / float(b)
        else:
            ratio = 1.0

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("WebP", "*.webp"),
                ("TIFF", "*.tiff;*.tif"),
                ("BMP", "*.bmp"),
                ("ICO", "*.ico"),
            ]
        )
        if path:
            try:
                # compute export size based on current canvas size
                iw = self.generator.width
                ih = self.generator.height
                if ratio > (iw / ih):
                    ew = iw
                    eh = int(iw / ratio)
                else:
                    ew = int(ih * ratio)
                    eh = ih
                img = self.generator.export_with_crop(ew, eh)
                # resize if export size differs
                try:
                    ex_w = int(self.ex_w_entry.get())
                    ex_h = int(self.ex_h_entry.get())
                    if ex_w >= 1 and ex_h >= 1 and (ex_w != ew or ex_h != eh):
                        img = img.resize((ex_w, ex_h), Image.Resampling.LANCZOS)
                except ValueError:
                    pass
                img.save(path)
                self.status_label.configure(text=_("saved", name=os.path.basename(path)))
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def switch_language(self, name):
        for code, n in get_languages():
            if n == name:
                set_language(code)
                break

    def switch_theme(self, mode):
        ctk.set_appearance_mode("dark" if mode == _("dark") else "light")

    def refresh_ui_text(self):
        self.root.title(_("title"))
        self.preview_title.configure(text=_("preview"))
        self.status_label.configure(text=_("ready"))
        self.lang_label.configure(text=_("language") + ":")
        self.theme_label.configure(text=_("theme") + ":")
        self.theme_menu.configure(values=[_("dark"), _("light")])
        self.ratio_menu.configure(values=["original", "16:9", "4:3", "1:1", _("custom")])
        self.build_controls()


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    App(root)
    root.mainloop()
