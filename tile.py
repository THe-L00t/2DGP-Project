"""
타일 기반 맵 시스템
- 11종류의 타일 타입 지원
- 2차원 배열 기반 맵 구성
"""
from pico2d import *

class TileType:
    """타일 타입 정의"""
    EMPTY = 0           # 빈 공간 (투명)
    GROUND_1 = 1        # 지면 타입 1
    GROUND_2 = 2        # 지면 타입 2
    GROUND_3 = 3        # 지면 타입 3
    WALL_1 = 4          # 벽 타입 1
    WALL_2 = 5          # 벽 타입 2
    WALL_3 = 6          # 벽 타입 3
    PLATFORM_1 = 7      # 플랫폼 타입 1
    PLATFORM_2 = 8      # 플랫폼 타입 2
    DECORATION_1 = 9    # 장식 타입 1
    DECORATION_2 = 10   # 장식 타입 2

class Tile:
    """개별 타일 클래스"""

    # 타일 크기 (픽셀)
    TILE_SIZE = 32

    # 타일 이미지 (클래스 변수, 한 번만 로드)
    tilemap_image = None

    # 타일 타입별 충돌 가능 여부
    COLLISION_MAP = {
        TileType.EMPTY: False,
        TileType.GROUND_1: True,
        TileType.GROUND_2: True,
        TileType.GROUND_3: True,
        TileType.WALL_1: True,
        TileType.WALL_2: True,
        TileType.WALL_3: True,
        TileType.PLATFORM_1: True,
        TileType.PLATFORM_2: True,
        TileType.DECORATION_1: False,
        TileType.DECORATION_2: False,
    }

    # 타일 타입별 타일맵 좌표 (x, y) - 나중에 실제 타일맵에 맞게 수정 필요
    TILE_COORDS = {
        TileType.EMPTY: None,           # 그리지 않음
        TileType.GROUND_1: (0, 0),      # 타일맵 (0, 0) 위치
        TileType.GROUND_2: (1, 0),      # 타일맵 (1, 0) 위치
        TileType.GROUND_3: (2, 0),
        TileType.WALL_1: (0, 1),
        TileType.WALL_2: (1, 1),
        TileType.WALL_3: (2, 1),
        TileType.PLATFORM_1: (0, 2),
        TileType.PLATFORM_2: (1, 2),
        TileType.DECORATION_1: (2, 2),
        TileType.DECORATION_2: (3, 2),
    }

    @classmethod
    def load_tilemap(cls, tilemap_path='resource/Tilemap_color1.png'):
        """타일맵 이미지 로드 (전체 클래스에서 공유)"""
        if cls.tilemap_image is None:
            cls.tilemap_image = load_image(tilemap_path)
            print(f"타일맵 이미지 로드: {tilemap_path}")

    def __init__(self, tile_type, grid_x, grid_y):
        """
        타일 생성
        tile_type: TileType 상수 (0~10)
        grid_x, grid_y: 타일맵 그리드 좌표 (0부터 시작)
        """
        self.tile_type = tile_type
        self.grid_x = grid_x
        self.grid_y = grid_y

        # 월드 좌표 계산 (왼쪽 아래 기준)
        self.x = grid_x * Tile.TILE_SIZE
        self.y = grid_y * Tile.TILE_SIZE

    def is_collidable(self):
        """이 타일이 충돌 가능한지 반환"""
        return Tile.COLLISION_MAP.get(self.tile_type, False)

    def get_bb(self):
        """바운딩 박스 반환 (left, bottom, right, top)"""
        return (
            self.x,
            self.y,
            self.x + Tile.TILE_SIZE,
            self.y + Tile.TILE_SIZE
        )

    def draw(self, camera):
        """타일 그리기"""
        if self.tile_type == TileType.EMPTY:
            return  # 빈 타일은 그리지 않음

        if Tile.tilemap_image is None:
            return  # 타일맵 이미지가 로드되지 않음

        # 타일맵에서 해당 타일의 좌표 가져오기
        coords = Tile.TILE_COORDS.get(self.tile_type)
        if coords is None:
            return

        tile_x, tile_y = coords

        # 화면 좌표로 변환
        screen_x, screen_y = camera.apply(
            self.x + Tile.TILE_SIZE // 2,
            self.y + Tile.TILE_SIZE // 2
        )

        # 타일맵에서 해당 타일 영역만 클리핑하여 그리기
        Tile.tilemap_image.clip_draw(
            tile_x * Tile.TILE_SIZE,  # 소스 x
            tile_y * Tile.TILE_SIZE,  # 소스 y
            Tile.TILE_SIZE,           # 소스 너비
            Tile.TILE_SIZE,           # 소스 높이
            screen_x,                 # 화면 x (중심)
            screen_y,                 # 화면 y (중심)
            Tile.TILE_SIZE,           # 그릴 너비
            Tile.TILE_SIZE            # 그릴 높이
        )

    def draw_debug(self, camera):
        """디버그용 타일 경계선 그리기"""
        if self.tile_type == TileType.EMPTY:
            return

        left, bottom, right, top = self.get_bb()
        screen_left, screen_bottom = camera.apply(left, bottom)
        screen_right, screen_top = camera.apply(right, top)

        # 충돌 가능한 타일은 빨간색, 아니면 회색
        if self.is_collidable():
            set_color(255, 0, 0)  # 빨간색
        else:
            set_color(128, 128, 128)  # 회색

        # 경계선 그리기
        draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)


class TileMap:
    """타일 맵 관리 클래스"""

    def __init__(self, width, height, tilemap_path='resource/Tilemap_color1.png'):
        """
        타일맵 생성
        width: 맵 가로 타일 개수
        height: 맵 세로 타일 개수
        tilemap_path: 타일맵 이미지 경로
        """
        self.width = width
        self.height = height

        # 타일맵 이미지 로드
        Tile.load_tilemap(tilemap_path)

        # 타일 배열 초기화 (2차원 배열)
        self.tiles = [[None for _ in range(width)] for _ in range(height)]

        # 디버그 모드
        self.debug_mode = False

        print(f"타일맵 생성: {width}x{height} 타일")

    def set_tile(self, grid_x, grid_y, tile_type):
        """특정 위치에 타일 설정"""
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.tiles[grid_y][grid_x] = Tile(tile_type, grid_x, grid_y)

    def get_tile(self, grid_x, grid_y):
        """특정 위치의 타일 반환"""
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.tiles[grid_y][grid_x]
        return None

    def load_from_array(self, tile_array):
        """
        2차원 배열에서 타일맵 로드
        tile_array: 2차원 리스트 (숫자 0~10)
        예: [[1, 1, 1], [0, 0, 0], [1, 1, 1]]
        """
        height = len(tile_array)
        width = len(tile_array[0]) if height > 0 else 0

        # 크기 조정
        self.height = height
        self.width = width
        self.tiles = [[None for _ in range(width)] for _ in range(height)]

        # 배열을 아래에서 위로 순회 (y=0이 아래)
        for y in range(height):
            for x in range(width):
                tile_type = tile_array[height - 1 - y][x]  # 배열은 위에서 아래로, 월드는 아래에서 위로
                if 0 <= tile_type <= 10:
                    self.set_tile(x, y, tile_type)

        print(f"타일맵 로드 완료: {width}x{height} 타일")

    def check_collision(self, x, y, width, height):
        """특정 영역과 충돌하는 타일이 있는지 확인"""
        # 영역이 걸치는 타일 범위 계산
        left = x - width / 2
        right = x + width / 2
        bottom = y - height / 2
        top = y + height / 2

        # 타일 그리드 좌표로 변환
        tile_left = int(left / Tile.TILE_SIZE)
        tile_right = int(right / Tile.TILE_SIZE)
        tile_bottom = int(bottom / Tile.TILE_SIZE)
        tile_top = int(top / Tile.TILE_SIZE)

        # 범위 내 타일 검사
        for ty in range(tile_bottom, tile_top + 1):
            for tx in range(tile_left, tile_right + 1):
                tile = self.get_tile(tx, ty)
                if tile and tile.is_collidable():
                    # AABB 충돌 검사
                    tl, tb, tr, tt = tile.get_bb()
                    if left < tr and right > tl and bottom < tt and top > tb:
                        return True

        return False

    def get_colliding_tiles(self, x, y, width, height):
        """특정 영역과 충돌하는 모든 타일 반환"""
        colliding = []

        # 영역이 걸치는 타일 범위 계산
        left = x - width / 2
        right = x + width / 2
        bottom = y - height / 2
        top = y + height / 2

        # 타일 그리드 좌표로 변환
        tile_left = int(left / Tile.TILE_SIZE)
        tile_right = int(right / Tile.TILE_SIZE)
        tile_bottom = int(bottom / Tile.TILE_SIZE)
        tile_top = int(top / Tile.TILE_SIZE)

        # 범위 내 타일 검사
        for ty in range(tile_bottom, tile_top + 1):
            for tx in range(tile_left, tile_right + 1):
                tile = self.get_tile(tx, ty)
                if tile and tile.is_collidable():
                    # AABB 충돌 검사
                    tl, tb, tr, tt = tile.get_bb()
                    if left < tr and right > tl and bottom < tt and top > tb:
                        colliding.append(tile)

        return colliding

    def update(self, delta_time):
        """업데이트 (필요시 애니메이션 등)"""
        pass

    def draw(self, camera):
        """타일맵 전체 그리기"""
        # 카메라 영역에 보이는 타일만 그리기 (최적화)
        # 일단 전체 타일 그리기
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.draw(camera)

    def draw_debug(self, camera):
        """디버그 모드: 타일 경계선 그리기"""
        if not self.debug_mode:
            return

        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.draw_debug(camera)

    def toggle_debug_mode(self):
        """디버그 모드 토글"""
        self.debug_mode = not self.debug_mode
        print(f"타일맵 디버그 모드: {'ON' if self.debug_mode else 'OFF'}")
        return self.debug_mode