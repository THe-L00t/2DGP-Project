from pico2d import *
#----------------------------------------------------------------
# 타일 타입 상수
TILE_EMPTY = 0
TILE_FLOOR = 1
TILE_WALL = 2
TILE_LADDER = 3
#----------------------------------------------------------------
class Tile:
    TILE_SIZE = 64  #타일 한 블럭의 크기 (픽셀)

    def __init__(self, tile_type, grid_x, grid_y, floor_level=0):
        self.tile_type = tile_type
        self.grid_x = grid_x  #그리드 좌표 (타일 단위)
        self.grid_y = grid_y
        self.floor_level = floor_level  #층 레벨 (바닥만 해당)
        self.image = None

    def set_image(self, image_path):
        self.image = load_image(image_path)

    def get_world_pos(self):
        #그리드 좌표를 월드 좌표로 변환
        world_x = self.grid_x * Tile.TILE_SIZE + Tile.TILE_SIZE // 2
        world_y = self.grid_y * Tile.TILE_SIZE + Tile.TILE_SIZE // 2
        return world_x, world_y

    def draw(self, camera):
        if self.image:
            world_x, world_y = self.get_world_pos()
            screen_x, screen_y = camera.apply(world_x, world_y)
            self.image.draw(screen_x, screen_y, Tile.TILE_SIZE, Tile.TILE_SIZE)

    def is_passable(self):
        return self.tile_type != TILE_WALL

    def is_floor(self):
        return self.tile_type == TILE_FLOOR

    def is_ladder(self):
        return self.tile_type == TILE_LADDER
#----------------------------------------------------------------
