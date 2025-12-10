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

        # 맵 경계 (기본값, set_map_bounds로 설정 가능)
        self.map_width = None
        self.map_height = None

    def set_map_bounds(self, map_width, map_height):
        """맵 크기 설정 (픽셀 단위)"""
        self.map_width = map_width
        self.map_height = map_height

    def set_target(self, target_obj):
        self.target_x = target_obj.x - self.canvas_width // 2
        self.target_y = target_obj.y - self.canvas_height // 2

    def update(self, delta_time):
        # lerp를 deltaTime과 함께 사용: lerp_factor = 1 - exp(-speed * dt)
        # 또는 단순히: lerp_factor = speed * dt (작은 값일 때 근사)
        lerp_factor = 1.0 - pow(0.5, self.lerp_speed * delta_time)

        self.x += (self.target_x - self.x) * lerp_factor
        self.y += (self.target_y - self.y) * lerp_factor

        # 맵 경계 제한
        if self.map_width is not None and self.map_height is not None:
            # 카메라가 맵 밖을 보지 못하도록 제한
            # 최소값: 0 (맵의 왼쪽/아래)
            # 최대값: 맵 크기 - 화면 크기 (맵의 오른쪽/위)
            min_x = 0
            max_x = self.map_width - self.canvas_width
            min_y = 0
            max_y = self.map_height - self.canvas_height

            # 맵이 화면보다 작은 경우 중앙 정렬
            if max_x < 0:
                self.x = (self.map_width - self.canvas_width) // 2
            else:
                self.x = max(min_x, min(self.x, max_x))

            if max_y < 0:
                self.y = (self.map_height - self.canvas_height) // 2
            else:
                self.y = max(min_y, min(self.y, max_y))

    def apply(self, x, y):
        return x - self.x, y - self.y
#----------------------------------------------------------------
