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
        self.lerp_speed = 5.0  # 초당 보간 속도

    def set_target(self, target_obj):
        self.target_x = target_obj.x - self.canvas_width // 2
        self.target_y = target_obj.y - self.canvas_height // 2

    def update(self, delta_time):
        # lerp를 deltaTime과 함께 사용: lerp_factor = 1 - exp(-speed * dt)
        # 또는 단순히: lerp_factor = speed * dt (작은 값일 때 근사)
        lerp_factor = 1.0 - pow(0.5, self.lerp_speed * delta_time)

        self.x += (self.target_x - self.x) * lerp_factor
        self.y += (self.target_y - self.y) * lerp_factor

    def apply(self, x, y):
        return x - self.x, y - self.y
#----------------------------------------------------------------
