# core flag generation logic

import math
from PIL import Image
from .models import Stripe

DEFAULT_COLORS = ["#55CDFC", "#F7A8B8", "#FFFFFF", "#F7A8B8", "#55CDFC"]


def hex_to_rgb(color):
    return (
        int(color[1:3], 16),
        int(color[3:5], 16),
        int(color[5:7], 16),
    )


class FlagGenerator:
    def __init__(self):
        self.width = 800
        self.height = 500
        n = len(DEFAULT_COLORS)
        self.stripes = []
        for i, c in enumerate(DEFAULT_COLORS):
            stripe = Stripe(c)
            stripe.y = (i + 0.5) / n
            stripe.height = 1.0 / n
            self.stripes.append(stripe)
        self.layers = []

    def generate(self):
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

        for stripe in self.stripes:
            sw = int(self.width * stripe.width)
            sh = int(self.height * stripe.height)
            band = Image.new("RGBA", (sw, sh), hex_to_rgb(stripe.color) + (255,))
            if abs(stripe.angle) > 0.01:
                band = band.rotate(-stripe.angle, expand=True, resample=Image.Resampling.BICUBIC)
            bw, bh = band.size
            cx = int(self.width * stripe.x)
            cy = int(self.height * stripe.y)
            x0 = cx - bw // 2
            y0 = cy - bh // 2
            img.paste(band, (x0, y0), band)

        for layer in self.layers:
            if not layer.visible:
                continue
            icon = layer.image.copy()
            target = int(min(self.width, self.height) * 0.25 * layer.scale)
            icon.thumbnail((target, target), Image.Resampling.LANCZOS)
            iw, ih = icon.size
            cx = int(self.width * layer.x)
            cy = int(self.height * layer.y)
            x0 = cx - iw // 2
            y0 = cy - ih // 2
            img.paste(icon, (x0, y0), icon)

        return img

    def export_with_crop(self, target_w, target_h, crop_center=True):
        img = self.generate()
        iw, ih = img.size
        if iw == 0 or ih == 0:
            return img

        # calculate crop box to match target aspect
        target_ratio = target_w / target_h
        current_ratio = iw / ih

        if current_ratio > target_ratio:
            # image is wider, crop width
            new_w = int(ih * target_ratio)
            new_h = ih
        else:
            new_w = iw
            new_h = int(iw / target_ratio)

        if crop_center:
            left = (iw - new_w) // 2
            top = (ih - new_h) // 2
        else:
            left = 0
            top = 0

        right = left + new_w
        bottom = top + new_h

        cropped = img.crop((left, top, right, bottom))
        return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
