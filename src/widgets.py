# custom widgets

import customtkinter as ctk
from tkinter import colorchooser
from .i18n import _


class ColorPickerRow(ctk.CTkFrame):
    def __init__(self, master, index, color, on_change, **kw):
        super().__init__(master, **kw)
        self.index = index
        self.on_change = on_change
        self.configure(fg_color="transparent")

        self.label = ctk.CTkLabel(self, text=_("stripe_n", n=index + 1), width=80)
        self.label.pack(side="left", padx=(0, 8))

        self.btn = ctk.CTkButton(
            self, text="", width=60, height=28,
            fg_color=color, hover_color=color,
            corner_radius=6, command=self.pick
        )
        self.btn.pack(side="left")

        self.hex_label = ctk.CTkLabel(self, text=color.upper(), width=70)
        self.hex_label.pack(side="left", padx=(8, 0))

    def pick(self):
        c = colorchooser.askcolor(color=self.hex_label.cget("text"))[1]
        if c:
            self.btn.configure(fg_color=c, hover_color=c)
            self.hex_label.configure(text=c.upper())
            self.on_change(self.index, "color", c)

    def set_color(self, c):
        self.btn.configure(fg_color=c, hover_color=c)
        self.hex_label.configure(text=c.upper())

    def refresh_text(self):
        self.label.configure(text=_("stripe_n", n=self.index + 1))


class StripeRow(ctk.CTkFrame):
    def __init__(self, master, stripe, index, on_change, on_remove, **kw):
        super().__init__(master, **kw)
        self.stripe = stripe
        self.index = index
        self.on_change = on_change
        self.on_remove = on_remove
        self.configure(fg_color="transparent")

        self.btn = ctk.CTkButton(
            self, text="", width=40, height=24,
            fg_color=stripe.color, hover_color=stripe.color,
            corner_radius=4, command=self.pick_color
        )
        self.btn.pack(side="left", padx=4)

        self.rm_btn = ctk.CTkButton(self, text="X", width=28, command=self.remove)
        self.rm_btn.pack(side="right")

        ctk.CTkLabel(self, text=_("angle"), width=40).pack(side="left", padx=(4, 0))
        self.angle_slider = ctk.CTkSlider(self, from_=-180, to=180, number_of_steps=36, width=60, command=self.on_angle)
        self.angle_slider.set(stripe.angle)
        self.angle_slider.pack(side="left", padx=2)
        self.angle_val = ctk.CTkLabel(self, text=f"{stripe.angle:.0f}", width=35)
        self.angle_val.pack(side="left")

        ctk.CTkLabel(self, text=_("w"), width=20).pack(side="left", padx=(4, 0))
        self.w_slider = ctk.CTkSlider(self, from_=0.05, to=2.0, number_of_steps=39, width=50, command=self.on_width)
        self.w_slider.set(stripe.width)
        self.w_slider.pack(side="left", padx=2)

        ctk.CTkLabel(self, text=_("h"), width=20).pack(side="left", padx=(4, 0))
        self.h_slider = ctk.CTkSlider(self, from_=0.05, to=2.0, number_of_steps=39, width=50, command=self.on_height)
        self.h_slider.set(stripe.height)
        self.h_slider.pack(side="left", padx=2)

    def pick_color(self):
        c = colorchooser.askcolor(color=self.stripe.color)[1]
        if c:
            self.stripe.color = c
            self.btn.configure(fg_color=c, hover_color=c)
            self.on_change()

    def on_angle(self, v):
        self.stripe.angle = float(v)
        self.angle_val.configure(text=f"{self.stripe.angle:.0f}")
        self.on_change()

    def on_width(self, v):
        self.stripe.width = float(v)
        self.on_change()

    def on_height(self, v):
        self.stripe.height = float(v)
        self.on_change()

    def remove(self):
        self.on_remove(self.index)


class LayerRow(ctk.CTkFrame):
    def __init__(self, master, layer, index, on_update, on_remove, **kw):
        super().__init__(master, **kw)
        self.layer = layer
        self.index = index
        self.on_update = on_update
        self.on_remove = on_remove
        self.configure(fg_color="transparent")

        # row 1
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x")

        self.vis_cb = ctk.CTkCheckBox(row1, text="", width=24, command=self.toggle_visible)
        self.vis_cb.select() if layer.visible else self.vis_cb.deselect()
        self.vis_cb.pack(side="left")

        self.drag_cb = ctk.CTkCheckBox(row1, text=_("drag"), width=50, command=self.toggle_drag)
        self.drag_cb.pack(side="left", padx=(4, 8))

        self.name_label = ctk.CTkLabel(row1, text=layer.name[:16], width=90)
        self.name_label.pack(side="left")

        self.rm_btn = ctk.CTkButton(row1, text="X", width=32, command=self.remove)
        self.rm_btn.pack(side="right")

        # row 2: params
        self.params_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.params_frame.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(self.params_frame, text=_("size"), width=35).pack(side="left")
        self.size_entry = ctk.CTkEntry(self.params_frame, width=55)
        self.size_entry.insert(0, str(int(layer.scale * 100)))
        self.size_entry.pack(side="left", padx=(0, 6))
        self.size_entry.bind("<Return>", lambda e: self.on_size_entry())
        self.size_entry.bind("<FocusOut>", lambda e: self.on_size_entry())

        ctk.CTkLabel(self.params_frame, text="X", width=15).pack(side="left")
        self.x_entry = ctk.CTkEntry(self.params_frame, width=55)
        self.x_entry.insert(0, f"{layer.x:.2f}")
        self.x_entry.pack(side="left", padx=(0, 6))
        self.x_entry.bind("<Return>", lambda e: self.on_xy_entry())
        self.x_entry.bind("<FocusOut>", lambda e: self.on_xy_entry())

        ctk.CTkLabel(self.params_frame, text="Y", width=15).pack(side="left")
        self.y_entry = ctk.CTkEntry(self.params_frame, width=55)
        self.y_entry.insert(0, f"{layer.y:.2f}")
        self.y_entry.pack(side="left", padx=(0, 6))
        self.y_entry.bind("<Return>", lambda e: self.on_xy_entry())
        self.y_entry.bind("<FocusOut>", lambda e: self.on_xy_entry())

        self.update_drag_state()

    def toggle_visible(self):
        self.layer.visible = bool(self.vis_cb.get())
        self.on_update()

    def toggle_drag(self):
        self.layer.drag_enabled = bool(self.drag_cb.get())
        self.update_drag_state()
        self.on_update()

    def update_drag_state(self):
        if self.layer.drag_enabled:
            self.params_frame.pack_forget()
        else:
            self.params_frame.pack(fill="x", pady=(4, 0))

    def on_size_entry(self):
        try:
            v = float(self.size_entry.get()) / 100
            self.layer.scale = max(0.001, v)
            self.on_update()
        except ValueError:
            pass

    def on_xy_entry(self):
        try:
            self.layer.x = float(self.x_entry.get())
            self.layer.y = float(self.y_entry.get())
            self.on_update()
        except ValueError:
            pass

    def remove(self):
        self.on_remove(self.index)
