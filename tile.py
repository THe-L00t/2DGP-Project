from pico2d import *
#----------------------------------------------------------------
# 타일 타입 상수 - 세분화된 시스템
#----------------------------------------------------------------
# 배경/환경
TILE_WATER = 0          # 바다 (빈 공간, 배경)

# 바닥 타입
TILE_FLOOR_CENTER = 1   # 바닥 중앙부 (평평한 바닥)
TILE_FLOOR_EDGE_LEFT = 2    # 바닥 왼쪽 가장자리 (절벽)
TILE_FLOOR_EDGE_RIGHT = 3   # 바닥 오른쪽 가장자리 (절벽)
TILE_FLOOR_EDGE_TOP = 4     # 바닥 위쪽 가장자리
TILE_FLOOR_EDGE_BOTTOM = 5  # 바닥 아래쪽 가장자리

# 경사로
TILE_SLOPE_UP_RIGHT = 6     # 오른쪽으로 올라가는 슬로프 (/)
TILE_SLOPE_UP_LEFT = 7      # 왼쪽으로 올라가는 슬로프 (\)

# 벽
TILE_WALL = 8           # 벽 (통과 불가)

#----------------------------------------------------------------
# 하위 호환성을 위한 별칭 (기존 코드 지원)
TILE_EMPTY = TILE_WATER
TILE_FLOOR = TILE_FLOOR_CENTER
TILE_LADDER = TILE_SLOPE_UP_RIGHT  # 사다리 -> 슬로프로 변경
#----------------------------------------------------------------

class Tile:
    TILE_SIZE = 64  #타일 한 블럭의 크기 (픽셀)

    def __init__(self, tile_type, grid_x, grid_y, floor_level=0):
        self.tile_type = tile_type
        self.grid_x = grid_x  #그리드 좌표 (타일 단위)
        self.grid_y = grid_y
        self.floor_level = floor_level  #층 레벨
        self.image = None

        # 애니메이션 지원
        self.is_animated = False
        self.animation_frames = []  # 애니메이션 프레임 이미지 리스트
        self.frame_count = 0
        self.current_frame = 0
        self.frame_time = 0.0
        self.frame_duration = 0.1  # 프레임당 지속 시간 (초)

    def set_image(self, image_path):
        """단일 이미지 설정"""
        self.image = load_image(image_path)
        self.is_animated = False

    def set_animated_image(self, image_path, frame_count, frame_width=64, frame_duration=0.1):
        """애니메이션 스프라이트 시트 설정"""
        self.image = load_image(image_path)
        self.is_animated = True
        self.frame_count = frame_count
        self.frame_width = frame_width
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.frame_time = 0.0

    def update(self, delta_time):
        """애니메이션 업데이트"""
        if self.is_animated and self.frame_count > 0:
            self.frame_time += delta_time
            if self.frame_time >= self.frame_duration:
                self.frame_time = 0.0
                self.current_frame = (self.current_frame + 1) % self.frame_count

    def get_world_pos(self):
        """그리드 좌표를 월드 좌표로 변환"""
        world_x = self.grid_x * Tile.TILE_SIZE + Tile.TILE_SIZE // 2
        world_y = self.grid_y * Tile.TILE_SIZE + Tile.TILE_SIZE // 2
        return world_x, world_y

    def draw(self, camera):
        if not self.image:
            return

        world_x, world_y = self.get_world_pos()
        screen_x, screen_y = camera.apply(world_x, world_y)

        if self.is_animated and self.frame_count > 0:
            # 애니메이션 프레임 그리기
            frame_x = int(self.current_frame) * self.frame_width
            self.image.clip_draw(frame_x, 0, self.frame_width, Tile.TILE_SIZE,
                               screen_x, screen_y, Tile.TILE_SIZE, Tile.TILE_SIZE)
        else:
            # 단일 이미지 그리기
            self.image.draw(screen_x, screen_y, Tile.TILE_SIZE, Tile.TILE_SIZE)

    def is_passable(self):
        """캐릭터가 통과할 수 있는지"""
        # 벽과 물은 통과 불가
        return self.tile_type not in [TILE_WALL, TILE_WATER]

    def is_floor(self):
        """바닥 타일인지 (모든 바닥 타입 포함)"""
        return self.tile_type in [
            TILE_FLOOR_CENTER,
            TILE_FLOOR_EDGE_LEFT,
            TILE_FLOOR_EDGE_RIGHT,
            TILE_FLOOR_EDGE_TOP,
            TILE_FLOOR_EDGE_BOTTOM
        ]

    def is_floor_center(self):
        """중앙 바닥인지"""
        return self.tile_type == TILE_FLOOR_CENTER

    def is_floor_edge(self):
        """가장자리 바닥(절벽)인지"""
        return self.tile_type in [
            TILE_FLOOR_EDGE_LEFT,
            TILE_FLOOR_EDGE_RIGHT,
            TILE_FLOOR_EDGE_TOP,
            TILE_FLOOR_EDGE_BOTTOM
        ]

    def is_slope(self):
        """슬로프인지"""
        return self.tile_type in [TILE_SLOPE_UP_RIGHT, TILE_SLOPE_UP_LEFT]

    def is_water(self):
        """물(바다)인지"""
        return self.tile_type == TILE_WATER

    def get_slope_direction(self):
        """슬로프 방향 반환 (1: 오른쪽 위, -1: 왼쪽 위, 0: 슬로프 아님)"""
        if self.tile_type == TILE_SLOPE_UP_RIGHT:
            return 1
        elif self.tile_type == TILE_SLOPE_UP_LEFT:
            return -1
        return 0

    def get_bb(self):
        """타일의 바운딩 박스 반환"""
        world_x, world_y = self.get_world_pos()
        half_size = Tile.TILE_SIZE // 2
        return world_x - half_size, world_y - half_size, world_x + half_size, world_y + half_size

    def get_type_name(self):
        """타일 타입을 문자열로 반환 (디버깅용)"""
        type_names = {
            TILE_WATER: "WATER",
            TILE_FLOOR_CENTER: "FLOOR_CENTER",
            TILE_FLOOR_EDGE_LEFT: "FLOOR_EDGE_LEFT",
            TILE_FLOOR_EDGE_RIGHT: "FLOOR_EDGE_RIGHT",
            TILE_FLOOR_EDGE_TOP: "FLOOR_EDGE_TOP",
            TILE_FLOOR_EDGE_BOTTOM: "FLOOR_EDGE_BOTTOM",
            TILE_SLOPE_UP_RIGHT: "SLOPE_UP_RIGHT",
            TILE_SLOPE_UP_LEFT: "SLOPE_UP_LEFT",
            TILE_WALL: "WALL"
        }
        return type_names.get(self.tile_type, f"UNKNOWN({self.tile_type})")
#----------------------------------------------------------------
