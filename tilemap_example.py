"""
타일맵 사용 예시 (쿼터뷰 게임용)
"""
from tile import TileMap, TileType

# 예시 1: 쿼터뷰용 작은 방 맵
def create_example_map_1():
    """쿼터뷰 방 예시 (벽으로 둘러싸인 공간)"""
    # 2차원 배열로 맵 정의
    # 0: 빈 공간 (이동 가능), 1~10: 각 타일 타입
    tile_data = [
        # 위에서부터 아래로 (화면 상단이 첫 줄)
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # 상단 벽
        [4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4],  # 벽 + 바닥
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 9, 9, 9, 9, 0, 0, 0, 0, 1, 4],  # 중앙 장식
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4],  # 벽 + 바닥
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # 하단 벽
    ]

    tilemap = TileMap(15, 10)
    tilemap.load_from_array(tile_data)
    return tilemap


# 예시 2: 쿼터뷰용 복잡한 맵 (장애물이 있는 필드)
def create_example_map_2():
    """쿼터뷰 필드 예시 (20x15 타일)"""
    tile_data = [
        # 20칸 x 15칸 - 상단이 뒤쪽(위), 하단이 앞쪽(아래)
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # 상단 벽
        [4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4],
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 5, 5, 0, 0, 0, 1, 4],  # 벽 장애물
        [4, 1, 0, 0, 5, 5, 0, 0, 0, 9, 9, 0, 0, 5, 5, 0, 0, 0, 1, 4],  # 벽 + 장식
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 0, 0, 6, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 1, 4],  # 중앙 벽
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 1, 4],  # 장식
        [4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4],
        [4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4],
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # 하단 벽
    ]

    tilemap = TileMap(20, 15)
    tilemap.load_from_array(tile_data)
    return tilemap


# 예시 3: 쿼터뷰용 던전 복도
def create_example_map_3():
    """쿼터뷰 던전 복도 예시 (개별 타일 설정)"""
    tilemap = TileMap(25, 12)

    # 상하단 벽 (WALL_1)
    for x in range(25):
        tilemap.set_tile(x, 0, TileType.WALL_1)    # 하단 벽
        tilemap.set_tile(x, 11, TileType.WALL_1)   # 상단 벽

    # 좌우 벽 (WALL_1)
    for y in range(12):
        tilemap.set_tile(0, y, TileType.WALL_1)    # 좌측 벽
        tilemap.set_tile(24, y, TileType.WALL_1)   # 우측 벽

    # 내부 바닥 (GROUND_1)
    for y in range(1, 11):
        for x in range(1, 24):
            tilemap.set_tile(x, y, TileType.GROUND_1)

    # 중앙 장애물 배치 (WALL_2)
    for x in range(10, 15):
        tilemap.set_tile(x, 5, TileType.WALL_2)
        tilemap.set_tile(x, 6, TileType.WALL_2)

    # 장식 배치 (DECORATION_1)
    tilemap.set_tile(5, 3, TileType.DECORATION_1)
    tilemap.set_tile(19, 8, TileType.DECORATION_1)

    return tilemap


# 타일 타입 설명
"""
타일 타입 목록:
- TileType.EMPTY (0): 빈 공간 (투명, 충돌 없음)
- TileType.GROUND_1 (1): 지면 타입 1 (충돌 있음)
- TileType.GROUND_2 (2): 지면 타입 2 (충돌 있음)
- TileType.GROUND_3 (3): 지면 타입 3 (충돌 있음)
- TileType.WALL_1 (4): 벽 타입 1 (충돌 있음)
- TileType.WALL_2 (5): 벽 타입 2 (충돌 있음)
- TileType.WALL_3 (6): 벽 타입 3 (충돌 있음)
- TileType.PLATFORM_1 (7): 플랫폼 타입 1 (충돌 있음)
- TileType.PLATFORM_2 (8): 플랫폼 타입 2 (충돌 있음)
- TileType.DECORATION_1 (9): 장식 타입 1 (충돌 없음)
- TileType.DECORATION_2 (10): 장식 타입 2 (충돌 없음)
"""

# 사용 방법
"""
1. 타일맵 생성:
   tilemap = TileMap(width, height)

2. 2차원 배열에서 로드:
   tile_data = [[1, 1, 1], [0, 0, 0], [2, 2, 2]]
   tilemap.load_from_array(tile_data)

3. 개별 타일 설정:
   tilemap.set_tile(x, y, TileType.GROUND_1)

4. 그리기 (play_scene.py 등에서):
   tilemap.draw(camera)
   tilemap.draw_debug(camera)  # 디버그 모드일 때

5. 충돌 체크:
   is_colliding = tilemap.check_collision(player.x, player.y, player.width, player.height)
   colliding_tiles = tilemap.get_colliding_tiles(player.x, player.y, player.width, player.height)

6. 디버그 모드 토글:
   tilemap.toggle_debug_mode()
"""