"""
타일 기반 맵 시스템
- 18종류의 타일 타입 지원
- 각 타일은 개별 PNG 이미지 사용
- 2차원 배열 기반 맵 구성
"""
from pico2d import *

class TileType:
    """타일 타입 정의"""
    # 바다
    OCEAN = 0               # 일반 바다

    # 타일맵 (9개)
    TOP_LEFT = 1            # 좌상단
    TOP = 2                 # 상단
    TOP_RIGHT = 3           # 우상단
    LEFT = 4                # 좌단
    CENTER = 5              # 중앙
    RIGHT = 6               # 우단
    BOTTOM_LEFT = 7         # 좌하단
    BOTTOM = 8              # 하단
    BOTTOM_RIGHT = 9        # 우하단

    # 계단
    STAIR_UP_RIGHT = 10     # 우상향 계단
    STAIR_UP_LEFT = 11      # 좌상향 계단

    # 바다 관련 (스프라이트)
    WAVE_LEFT = 12          # 파도 좌측
    WAVE_CENTER = 13        # 파도 중앙
    WAVE_RIGHT = 14         # 파도 우측
    CLIFF_LEFT = 15         # 절벽 좌측
    CLIFF_CENTER = 16       # 절벽 중앙
    CLIFF_RIGHT = 17        # 절벽 우측

class Tile:
    """개별 타일 클래스"""

    # 타일 크기 (픽셀)
    TILE_SIZE = 64

    # 타일 이미지 딕셔너리 (타입별로 개별 이미지 저장)
    tile_images = {}

    # 타일 타입별 이미지 파일 매핑
    TILE_IMAGE_FILES = {
        TileType.OCEAN: 'resource/tile_0.png',
        TileType.TOP_LEFT: 'resource/tile_1.png',
        TileType.TOP: 'resource/tile_2.png',
        TileType.TOP_RIGHT: 'resource/tile_3.png',
        TileType.LEFT: 'resource/tile_4.png',
        TileType.CENTER: 'resource/tile_5.png',
        TileType.RIGHT: 'resource/tile_6.png',
        TileType.BOTTOM_LEFT: 'resource/tile_7.png',
        TileType.BOTTOM: 'resource/tile_8.png',
        TileType.BOTTOM_RIGHT: 'resource/tile_9.png',
        TileType.STAIR_UP_RIGHT: ['resource/tile_1001.png', 'resource/tile_1002.png'],  # [상단, 하단]
        TileType.STAIR_UP_LEFT: ['resource/tile_1101.png', 'resource/tile_1102.png'],   # [상단, 하단]
        TileType.WAVE_LEFT: 'resource/tile_12.png',
        TileType.WAVE_CENTER: 'resource/tile_13.png',
        TileType.WAVE_RIGHT: 'resource/tile_14.png',
        TileType.CLIFF_LEFT: 'resource/tile_15.png',
        TileType.CLIFF_CENTER: 'resource/tile_16.png',
        TileType.CLIFF_RIGHT: 'resource/tile_17.png',
    }

    # 계단 타일 타입 목록 (다층 구조)
    STAIR_TILES = [TileType.STAIR_UP_RIGHT, TileType.STAIR_UP_LEFT]

    # 타일 타입별 충돌 가능 여부
    COLLISION_MAP = {
        TileType.OCEAN: False,          # 충돌 없음
        TileType.TOP_LEFT: True,
        TileType.TOP: True,
        TileType.TOP_RIGHT: True,
        TileType.LEFT: True,
        TileType.CENTER: False,         # 충돌 없음 (이동 가능 영역)
        TileType.RIGHT: True,
        TileType.BOTTOM_LEFT: True,
        TileType.BOTTOM: True,
        TileType.BOTTOM_RIGHT: True,
        TileType.STAIR_UP_RIGHT: True,
        TileType.STAIR_UP_LEFT: True,
        TileType.WAVE_LEFT: False,      # 충돌 없음 (장식)
        TileType.WAVE_CENTER: False,    # 충돌 없음 (장식)
        TileType.WAVE_RIGHT: False,     # 충돌 없음 (장식)
        TileType.CLIFF_LEFT: True,
        TileType.CLIFF_CENTER: True,
        TileType.CLIFF_RIGHT: True,
    }

    # 타일 타입별 커스텀 충돌박스 (상대 좌표: left, bottom, right, top)
    # None이면 충돌 없음
    # 단일 박스: (0, 0, 64, 64) 또는 [(0, 0, 64, 64)]
    # 여러 박스: [(0, 0, 32, 64), (32, 0, 64, 32)] - 리스트로 여러 개
    COLLISION_BOXES = {
        TileType.OCEAN: None,                      # 충돌 없음
        TileType.TOP_LEFT: [(0, 0, 20, 64),(0, 44, 64, 64)],      # L자 (좌측+상단)
        TileType.TOP: [(0, 44, 64, 64)],           # 상단만
        TileType.TOP_RIGHT: [(44, 0, 64, 64),(0, 44, 64, 64)],    # ┘자 (우측+상단)
        TileType.LEFT: [(0, 0, 20, 64)],           # 좌측만
        TileType.CENTER: None,                     # 충돌 없음 (이동 가능 영역)
        TileType.RIGHT: [(44, 0, 64, 64)],         # 우측만
        TileType.BOTTOM_LEFT: [(0, 0, 20, 64),(0, 0, 64, 20)],    # └자 (좌측+하단)
        TileType.BOTTOM: [(0, 0, 64, 20)],         # 하단만
        TileType.BOTTOM_RIGHT: [(44, 0, 64, 64),(0, 0, 64, 20)],  # ┌자 (우측+하단)
        TileType.STAIR_UP_RIGHT: [(20, 0, 64, 32)], # 우측 하단 (올라갈 수 있게)
        TileType.STAIR_UP_LEFT: [(0, 0, 44, 32)],   # 좌측 하단 (올라갈 수 있게)
        TileType.WAVE_LEFT: None,                  # 장식
        TileType.WAVE_CENTER: None,
        TileType.WAVE_RIGHT: None,
        TileType.CLIFF_LEFT: [(0, 0, 64, 64)],
        TileType.CLIFF_CENTER: [(0, 0, 64, 64)],
        TileType.CLIFF_RIGHT: [(0, 0, 64, 64)],
    }

    @classmethod
    def load_all_tiles(cls):
        """모든 타일 이미지 미리 로드"""
        if cls.tile_images:
            return  # 이미 로드됨

        print("타일 이미지 로딩 시작...")
        for tile_type, image_path in cls.TILE_IMAGE_FILES.items():
            try:
                # 계단 타일은 2개 이미지 (리스트)
                if isinstance(image_path, list):
                    images = []
                    for path in image_path:
                        images.append(load_image(path))
                        print(f"  - {path} 로드 완료")
                    cls.tile_images[tile_type] = images
                else:
                    # 일반 타일은 1개 이미지
                    cls.tile_images[tile_type] = load_image(image_path)
                    print(f"  - {image_path} 로드 완료")
            except:
                print(f"  - {image_path} 로드 실패")
                cls.tile_images[tile_type] = None
        print(f"타일 이미지 로딩 완료: {len(cls.tile_images)}개 타입")

    @classmethod
    def load_tile_image(cls, tile_type):
        """특정 타일 타입의 이미지 로드 (지연 로딩)"""
        if tile_type in cls.tile_images:
            return cls.tile_images[tile_type]

        image_path = cls.TILE_IMAGE_FILES.get(tile_type)
        if image_path:
            try:
                # 계단 타일은 2개 이미지 (리스트)
                if isinstance(image_path, list):
                    images = []
                    for path in image_path:
                        images.append(load_image(path))
                        print(f"타일 이미지 로드: {path}")
                    cls.tile_images[tile_type] = images
                    return cls.tile_images[tile_type]
                else:
                    # 일반 타일은 1개 이미지
                    cls.tile_images[tile_type] = load_image(image_path)
                    print(f"타일 이미지 로드: {image_path}")
                    return cls.tile_images[tile_type]
            except:
                print(f"타일 이미지 로드 실패: {image_path}")
                cls.tile_images[tile_type] = None
                return None
        return None

    def __init__(self, tile_type, grid_x, grid_y):
        """
        타일 생성
        tile_type: TileType 상수 (0~17)
        grid_x, grid_y: 타일맵 그리드 좌표 (0부터 시작)
        """
        self.tile_type = tile_type
        self.grid_x = grid_x
        self.grid_y = grid_y

        # 월드 좌표 계산 (왼쪽 아래 기준)
        self.x = grid_x * Tile.TILE_SIZE
        self.y = grid_y * Tile.TILE_SIZE

        # 해당 타입의 이미지 로드 (아직 로드되지 않았다면)
        if tile_type not in Tile.tile_images:
            Tile.load_tile_image(tile_type)

    def is_collidable(self):
        """이 타일이 충돌 가능한지 반환"""
        return Tile.COLLISION_MAP.get(self.tile_type, False)

    def get_bb(self):
        """바운딩 박스 리스트 반환 - 여러 개 가능"""
        if not self.is_collidable():
            return []

        # 커스텀 충돌박스가 설정되어 있으면 사용
        collision_boxes = Tile.COLLISION_BOXES.get(self.tile_type)
        if collision_boxes:
            result = []
            for box in collision_boxes:
                # 상대 좌표를 절대 좌표로 변환
                rel_left, rel_bottom, rel_right, rel_top = box
                result.append((
                    self.x + rel_left,
                    self.y + rel_bottom,
                    self.x + rel_right,
                    self.y + rel_top
                ))
            return result

        # 커스텀 충돌박스가 없으면 전체 타일 크기 사용
        return [(
            self.x,
            self.y,
            self.x + Tile.TILE_SIZE,
            self.y + Tile.TILE_SIZE
        )]

    def draw(self, camera):
        """타일 그리기 (하단 이미지만, 계단은 하단 부분만)"""
        # 해당 타일의 이미지 가져오기
        image = Tile.tile_images.get(self.tile_type)
        if image is None:
            return  # 이미지가 없으면 그리지 않음

        # 화면 좌표로 변환 (타일의 중심)
        screen_x, screen_y = camera.apply(
            self.x + Tile.TILE_SIZE // 2,
            self.y + Tile.TILE_SIZE // 2
        )

        # 계단 타일 - 하단 이미지만 그리기
        if self.tile_type in Tile.STAIR_TILES:
            if isinstance(image, list) and len(image) == 2:
                # 하단 이미지 (1002/1102) - 타일 기준 위치에 그리기
                bottom_image = image[1]
                bottom_image.draw(screen_x, screen_y, Tile.TILE_SIZE, Tile.TILE_SIZE)
        else:
            # 일반 타일 이미지 그리기 (중심 기준)
            image.draw(screen_x, screen_y, Tile.TILE_SIZE, Tile.TILE_SIZE)

    def draw_top(self, camera):
        """계단 타일의 상단 이미지 그리기 (일반 타일 위에 겹쳐짐)"""
        if self.tile_type not in Tile.STAIR_TILES:
            return  # 계단 타일이 아니면 스킵

        image = Tile.tile_images.get(self.tile_type)
        if image is None or not isinstance(image, list) or len(image) != 2:
            return

        # 상단 이미지 (1001/1101) - 한 타일 위에 겹쳐서 그리기
        top_image = image[0]
        screen_x_top, screen_y_top = camera.apply(
            self.x + Tile.TILE_SIZE // 2,
            self.y + Tile.TILE_SIZE + Tile.TILE_SIZE // 2  # 한 타일 위
        )
        top_image.draw(screen_x_top, screen_y_top, Tile.TILE_SIZE, Tile.TILE_SIZE)

    def draw_debug(self, camera):
        """디버그용 충돌박스만 그리기"""
        # 충돌박스만 표시 (충돌 가능한 타일만)
        if self.is_collidable():
            bbs = self.get_bb()
            for bb in bbs:
                left, bottom, right, top = bb
                screen_left, screen_bottom = camera.apply(left, bottom)
                screen_right, screen_top = camera.apply(right, top)

                # 2중 사각형으로 충돌박스 강조
                draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)
                draw_rectangle(screen_left+1, screen_bottom+1, screen_right-1, screen_top-1)


class TileMap:
    """타일 맵 관리 클래스"""

    def __init__(self, width, height):
        """
        타일맵 생성
        width: 맵 가로 타일 개수
        height: 맵 세로 타일 개수
        """
        self.width = width
        self.height = height

        # 모든 타일 이미지 미리 로드
        Tile.load_all_tiles()

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
        tile_array: 2차원 리스트 (숫자 0~17)
        예: [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
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
                if 0 <= tile_type <= 17:
                    self.set_tile(x, y, tile_type)

        print(f"타일맵 로드 완료: {width}x{height} 타일")

    def check_collision(self, x, y, width, height):
        """
        특정 영역과 충돌하는 타일이 있는지 확인

        Args:
            x, y: 객체의 중심 좌표
            width, height: 객체의 크기

        Returns:
            bool: 충돌 여부
        """
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
                    # 타일의 모든 충돌박스 가져오기
                    bbs = tile.get_bb()
                    for bb in bbs:
                        tl, tb, tr, tt = bb
                        # AABB 충돌 검사
                        if left < tr and right > tl and bottom < tt and top > tb:
                            return True

        return False

    def get_colliding_tiles(self, x, y, width, height):
        """
        특정 영역과 충돌하는 모든 타일 반환

        Args:
            x, y: 객체의 중심 좌표
            width, height: 객체의 크기

        Returns:
            list: 충돌하는 타일 리스트
        """
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
                    # 타일의 모든 충돌박스 가져오기
                    bbs = tile.get_bb()
                    for bb in bbs:
                        tl, tb, tr, tt = bb
                        # AABB 충돌 검사
                        if left < tr and right > tl and bottom < tt and top > tb:
                            colliding.append(tile)
                            break  # 같은 타일 중복 추가 방지

        return colliding

    def update(self, delta_time):
        """업데이트 (필요시 애니메이션 등)"""
        pass

    def draw(self, camera):
        """타일맵 전체 그리기"""
        # 1단계: 모든 타일의 기본 이미지 그리기 (계단은 하단 부분만)
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.draw(camera)

        # 2단계: 계단 타일의 상단 이미지 그리기 (위 타일에 겹쳐짐)
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.draw_top(camera)

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
