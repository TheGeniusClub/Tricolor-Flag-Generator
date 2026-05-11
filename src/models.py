# data models

class Stripe:
    def __init__(self, color="#55CDFC", angle=0.0, width=1.0, height=0.2, x=0.5, y=0.5):
        self.color = color
        self.angle = angle
        self.width = width
        self.height = height
        self.x = x
        self.y = y


class Layer:
    def __init__(self, image, name="icon"):
        self.image = image
        self.name = name
        self.x = 0.5
        self.y = 0.5
        self.scale = 1.0
        self.visible = True
        self.drag_enabled = False
