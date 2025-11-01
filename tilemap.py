from pico2d import *
from tile import Tile, TILE_EMPTY, TILE_FLOOR, TILE_WALL, TILE_LADDER
import json
#----------------------------------------------------------------
class TileMap:
    def __init__(self, chunk_width=800, chunk_height=600):
        self.tiles = {}  #{(grid_x, grid_y): Tile}
        self.chunk_width = chunk_width
        self.chunk_height = chunk_height
        self.tile_size = Tile.TILE_SIZE

        #청크 계산용
        self.tiles_per_chunk_x = chunk_width // self.tile_size + 2  #여유분
        self.tiles_per_chunk_y = chunk_height // self.tile_size + 2

    def add_tile(self, tile_type, grid_x, grid_y, floor_level=0):
        tile = Tile(tile_type, grid_x, grid_y, floor_level)
        self.tiles[(grid_x, grid_y)] = tile
        return tile

    def get_tile(self, grid_x, grid_y):
        return self.tiles.get((grid_x, grid_y))

    def remove_tile(self, grid_x, grid_y):
        if (grid_x, grid_y) in self.tiles:
            del self.tiles[(grid_x, grid_y)]

    def get_visible_tiles(self, camera):
        #카메라 기준으로 보이는 타일만 반환 (청크 최적화)
        visible_tiles = []

        #카메라 영역 계산
        cam_left = camera.x
        cam_right = camera.x + self.chunk_width
        cam_bottom = camera.y
        cam_top = camera.y + self.chunk_height

        #그리드 범위 계산
        grid_left = int(cam_left // self.tile_size) - 1
        grid_right = int(cam_right // self.tile_size) + 1
        grid_bottom = int(cam_bottom // self.tile_size) - 1
        grid_top = int(cam_top // self.tile_size) + 1

        #해당 범위의 타일만 수집
        for (gx, gy), tile in self.tiles.items():
            if grid_left <= gx <= grid_right and grid_bottom <= gy <= grid_top:
                visible_tiles.append(tile)

        return visible_tiles

    def draw(self, camera):
        visible_tiles = self.get_visible_tiles(camera)
        for tile in visible_tiles:
            tile.draw(camera)

    def save_to_file(self, filename):
        #맵 데이터를 JSON 파일로 저장
        data = {
            'tiles': []
        }
        for (gx, gy), tile in self.tiles.items():
            tile_data = {
                'type': tile.tile_type,
                'grid_x': gx,
                'grid_y': gy,
                'floor_level': tile.floor_level
            }
            data['tiles'].append(tile_data)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename):
        #JSON 파일에서 맵 데이터 로드
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.tiles.clear()
        for tile_data in data['tiles']:
            self.add_tile(
                tile_data['type'],
                tile_data['grid_x'],
                tile_data['grid_y'],
                tile_data.get('floor_level', 0)
            )

    def load_from_text(self, text_map, floor_level=0):
        #텍스트 기반 맵 로드 (간단한 맵 작성용)
        lines = text_map.strip().split('\n')
        for y, line in enumerate(reversed(lines)):  #아래에서 위로
            for x, char in enumerate(line):
                tile_type = self._char_to_tile_type(char)
                if tile_type != TILE_EMPTY:
                    self.add_tile(tile_type, x, y, floor_level)

    def _char_to_tile_type(self, char):
        char_map = {
            '.': TILE_EMPTY,
            '#': TILE_WALL,
            '=': TILE_FLOOR,
            'H': TILE_LADDER
        }
        return char_map.get(char, TILE_EMPTY)
#----------------------------------------------------------------
