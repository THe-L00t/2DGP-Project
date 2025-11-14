"""
배경 이미지 기반 맵 시스템
- 배경 이미지를 통째로 로드
- 충돌 블럭을 JSON으로 관리
- 실시간 충돌 블럭 에디팅 기능
"""
from pico2d import *
import json

class CollisionBlock:
    """충돌 블럭 (사각형 영역)"""
    def __init__(self, x, y, width, height):
        self.x = x  # 중심 x 좌표
        self.y = y  # 중심 y 좌표
        self.width = width
        self.height = height

    def get_bb(self):
        """바운딩 박스 반환"""
        left = self.x - self.width / 2
        right = self.x + self.width / 2
        bottom = self.y - self.height / 2
        top = self.y + self.height / 2
        return left, bottom, right, top

    def contains_point(self, px, py):
        """점이 블럭 안에 있는지 확인"""
        left, bottom, right, top = self.get_bb()
        return left <= px <= right and bottom <= py <= top

    def draw(self, camera, color=(255, 0, 0), alpha=0.3):
        """충돌 블럭 그리기"""
        left, bottom, right, top = self.get_bb()
        screen_left, screen_bottom = camera.apply(left, bottom)
        screen_right, screen_top = camera.apply(right, top)

        # 반투명 사각형 (내부)
        set_color(*color)
        draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)

    def to_dict(self):
        """딕셔너리로 변환 (저장용)"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

    @staticmethod
    def from_dict(data):
        """딕셔너리에서 생성 (로드용)"""
        return CollisionBlock(
            data['x'],
            data['y'],
            data['width'],
            data['height']
        )


class BackgroundMap:
    """배경 이미지 기반 맵 시스템"""

    def __init__(self, background_image_path=None):
        self.background_image = None
        self.bg_width = 0
        self.bg_height = 0

        if background_image_path:
            self.load_background(background_image_path)

        # 충돌 블럭 리스트
        self.collision_blocks = []

        # 에디터 모드 관련
        self.editor_mode = False
        self.selected_block = None
        self.dragging = False
        self.drag_start_pos = None
        self.creating_block = False
        self.create_start_pos = None
        self.resize_mode = None  # None, 'left', 'right', 'top', 'bottom'
        self.resize_start_pos = None
        self.resize_start_size = None

    def load_background(self, image_path):
        """배경 이미지 로드"""
        self.background_image = load_image(image_path)
        self.bg_width = self.background_image.w
        self.bg_height = self.background_image.h
        print(f"배경 이미지 로드: {image_path} ({self.bg_width}x{self.bg_height})")

    def add_collision_block(self, x, y, width, height):
        """충돌 블럭 추가"""
        block = CollisionBlock(x, y, width, height)
        self.collision_blocks.append(block)
        return block

    def remove_collision_block(self, block):
        """충돌 블럭 제거"""
        if block in self.collision_blocks:
            self.collision_blocks.remove(block)

    def get_block_at_point(self, world_x, world_y):
        """특정 월드 좌표에 있는 블럭 찾기 (뒤에서부터 검색)"""
        for block in reversed(self.collision_blocks):
            if block.contains_point(world_x, world_y):
                return block
        return None

    def check_collision(self, x, y, width, height):
        """특정 영역과 충돌하는 블럭이 있는지 확인"""
        left = x - width / 2
        right = x + width / 2
        bottom = y - height / 2
        top = y + height / 2

        for block in self.collision_blocks:
            bl, bb, br, bt = block.get_bb()

            # AABB 충돌 검사
            if left < br and right > bl and bottom < bt and top > bb:
                return True

        return False

    def get_colliding_blocks(self, x, y, width, height):
        """특정 영역과 충돌하는 모든 블럭 반환"""
        left = x - width / 2
        right = x + width / 2
        bottom = y - height / 2
        top = y + height / 2

        colliding = []
        for block in self.collision_blocks:
            bl, bb, br, bt = block.get_bb()

            # AABB 충돌 검사
            if left < br and right > bl and bottom < bt and top > bb:
                colliding.append(block)

        return colliding

    def save_collision_data(self, filename):
        """충돌 블럭 데이터를 JSON 파일로 저장"""
        data = {
            'blocks': [block.to_dict() for block in self.collision_blocks]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"충돌 데이터 저장 완료: {filename} ({len(self.collision_blocks)}개 블럭)")

    def load_collision_data(self, filename):
        """JSON 파일에서 충돌 블럭 데이터 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.collision_blocks.clear()
            for block_data in data.get('blocks', []):
                block = CollisionBlock.from_dict(block_data)
                self.collision_blocks.append(block)

            print(f"충돌 데이터 로드 완료: {filename} ({len(self.collision_blocks)}개 블럭)")
        except FileNotFoundError:
            print(f"충돌 데이터 파일이 없습니다: {filename}")
        except Exception as e:
            print(f"충돌 데이터 로드 실패: {e}")

    def update(self, delta_time):
        """업데이트 (필요시 애니메이션 등)"""
        pass

    def draw(self, camera):
        """배경 이미지 그리기"""
        if not self.background_image:
            return

        # 배경 이미지를 화면 중앙에 그리기
        # 카메라의 중심점을 기준으로 배경 위치 계산
        bg_center_x = self.bg_width / 2
        bg_center_y = self.bg_height / 2

        screen_x, screen_y = camera.apply(bg_center_x, bg_center_y)

        self.background_image.draw(screen_x, screen_y, self.bg_width, self.bg_height)

    def draw_collision_blocks(self, camera, show_all=True):
        """충돌 블럭 그리기"""
        for block in self.collision_blocks:
            # 선택된 블럭은 다른 색으로 표시
            if block == self.selected_block:
                block.draw(camera, color=(0, 255, 0), alpha=0.5)
            else:
                block.draw(camera, color=(255, 0, 0), alpha=0.3)

    # ==================== 에디터 모드 기능 ====================

    def toggle_editor_mode(self):
        """에디터 모드 토글"""
        self.editor_mode = not self.editor_mode
        if not self.editor_mode:
            self.selected_block = None
            self.dragging = False
            self.creating_block = False
        print(f"충돌 블럭 에디터: {'ON' if self.editor_mode else 'OFF'}")
        return self.editor_mode

    def editor_handle_mouse_down(self, world_x, world_y, button):
        """마우스 다운 이벤트 처리 (에디터 모드)"""
        if not self.editor_mode:
            return

        if button == SDL_BUTTON_LEFT:
            # 기존 블럭 선택 또는 새 블럭 생성 시작
            clicked_block = self.get_block_at_point(world_x, world_y)

            if clicked_block:
                # 기존 블럭 선택 및 드래그 시작
                self.selected_block = clicked_block
                self.dragging = True
                self.drag_start_pos = (world_x, world_y)
            else:
                # 새 블럭 생성 시작
                self.creating_block = True
                self.create_start_pos = (world_x, world_y)
                self.selected_block = None

        elif button == SDL_BUTTON_RIGHT:
            # 블럭 삭제
            clicked_block = self.get_block_at_point(world_x, world_y)
            if clicked_block:
                self.remove_collision_block(clicked_block)
                if self.selected_block == clicked_block:
                    self.selected_block = None
                print(f"블럭 삭제됨 (남은 블럭: {len(self.collision_blocks)}개)")

    def editor_handle_mouse_up(self, world_x, world_y, button):
        """마우스 업 이벤트 처리 (에디터 모드)"""
        if not self.editor_mode:
            return

        if button == SDL_BUTTON_LEFT:
            if self.creating_block and self.create_start_pos:
                # 새 블럭 생성 완료
                start_x, start_y = self.create_start_pos

                # 중심점과 크기 계산
                center_x = (start_x + world_x) / 2
                center_y = (start_y + world_y) / 2
                width = abs(world_x - start_x)
                height = abs(world_y - start_y)

                # 최소 크기 제한
                if width > 10 and height > 10:
                    new_block = self.add_collision_block(center_x, center_y, width, height)
                    self.selected_block = new_block
                    print(f"새 블럭 생성: ({center_x:.0f}, {center_y:.0f}) [{width:.0f}x{height:.0f}]")

                self.creating_block = False
                self.create_start_pos = None

            self.dragging = False
            self.drag_start_pos = None

    def editor_handle_mouse_motion(self, world_x, world_y):
        """마우스 이동 이벤트 처리 (에디터 모드)"""
        if not self.editor_mode:
            return

        if self.dragging and self.selected_block and self.drag_start_pos:
            # 블럭 이동
            dx = world_x - self.drag_start_pos[0]
            dy = world_y - self.drag_start_pos[1]

            self.selected_block.x += dx
            self.selected_block.y += dy

            self.drag_start_pos = (world_x, world_y)

    def editor_handle_key(self, key):
        """키 입력 처리 (에디터 모드)"""
        if not self.editor_mode:
            return

        # 선택된 블럭 크기 조절 (화살표 키)
        if self.selected_block:
            if key == SDLK_LEFT:
                self.selected_block.width = max(10, self.selected_block.width - 10)
            elif key == SDLK_RIGHT:
                self.selected_block.width += 10
            elif key == SDLK_UP:
                self.selected_block.height += 10
            elif key == SDLK_DOWN:
                self.selected_block.height = max(10, self.selected_block.height - 10)
            elif key == SDLK_DELETE or key == SDLK_BACKSPACE:
                # 선택된 블럭 삭제
                self.remove_collision_block(self.selected_block)
                print(f"블럭 삭제됨 (남은 블럭: {len(self.collision_blocks)}개)")
                self.selected_block = None

    def draw_editor_ui(self, camera):
        """에디터 UI 그리기"""
        if not self.editor_mode:
            return

        # 블럭 생성 중 미리보기
        if self.creating_block and self.create_start_pos:
            from pico2d import get_events, SDL_MOUSEMOTION
            events = get_events()
            for event in events:
                if event.type == SDL_MOUSEMOTION:
                    # 현재 마우스 위치를 월드 좌표로 변환하여 미리보기
                    # (이 부분은 play_scene에서 처리하는 것이 더 적절)
                    pass

        # 에디터 모드 표시 (화면 상단)
        # TODO: UI 텍스트 추가 (pico2d 폰트 필요)
