from pico2d import *
#----------------------------------------------------------------
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.canvas_width = get_canvas_width()
        self.canvas_height = get_canvas_height()
        self.speed = 0.1

    def set_target(self, target_obj):
        self.target_x = target_obj.x - self.canvas_width // 2
        self.target_y = target_obj.y - self.canvas_height // 2

    def update(self):
        self.x += (self.target_x - self.x) * self.speed
        self.y += (self.target_y - self.y) * self.speed

    def apply(self, x, y):
        return x - self.x, y - self.y
#----------------------------------------------------------------
