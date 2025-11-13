"""
인벤토리 Scene - 플레이 화면 위에 오버레이로 표시
"""
from pico2d import *
import game_framework

def enter():
    """Scene 진입 시 호출"""
    pass

def exit():
    """Scene 종료 시 호출"""
    pass

def pause():
    """Scene이 일시정지될 때 호출"""
    pass

def resume():
    """Scene이 재개될 때 호출"""
    pass

def handle_events(event):
    """이벤트 처리"""
    if event.type == SDL_KEYDOWN:
        if event.key == SDLK_ESCAPE or event.key == SDLK_i:
            # ESC 또는 I 키를 누르면 인벤토리 닫기
            game_framework.pop_scene()

def update(delta_time):
    """업데이트"""
    pass

def draw():
    """렌더링 - 인벤토리 창"""
    # 캔버스 크기 가져오기
    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 인벤토리 창 배경 (중앙에 사각형)
    center_x = canvas_width // 2
    center_y = canvas_height // 2
    box_width = 400
    box_height = 400

    left = center_x - box_width // 2
    right = center_x + box_width // 2
    bottom = center_y - box_height // 2
    top = center_y + box_height // 2

    # 3중 사각형으로 테두리 효과
    draw_rectangle(left, bottom, right, top)
    draw_rectangle(left + 2, bottom + 2, right - 2, top - 2)
    draw_rectangle(left + 4, bottom + 4, right - 4, top - 4)
