"""
인벤토리 Scene - 플레이 화면 위에 오버레이로 표시
"""
from pico2d import *
import game_framework

# Scene 변수
font = None
items = []  # 인벤토리 아이템 목록

def enter():
    """Scene 진입 시 호출"""
    global font, items
    font = load_font('ENCR10B.TTF', 30)

    # TODO: 실제 인벤토리 아이템 로드
    # 임시 아이템 목록
    items = [
        "Sword",
        "Shield",
        "Health Potion x3",
        "Magic Scroll",
        "Gold: 150"
    ]

def exit():
    """Scene 종료 시 호출"""
    global font
    # 리소스 해제는 pico2d가 자동으로 처리

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
    """렌더링 - 반투명 배경과 인벤토리 UI"""
    # 반투명 검은색 배경 (사각형으로 표현)
    # pico2d는 투명도를 직접 지원하지 않으므로 검은 사각형으로 처리

    # 인벤토리 창 배경 (중앙에 큰 사각형)
    draw_rectangle(200, 150, 600, 550)
    draw_rectangle(202, 152, 598, 548)
    draw_rectangle(204, 154, 596, 546)

    # 타이틀
    if font:
        font.draw(300, 500, 'INVENTORY', (255, 255, 255))

    # 아이템 목록
    y_pos = 450
    for i, item in enumerate(items):
        if font:
            font.draw(250, y_pos - i * 40, f"{i+1}. {item}", (200, 200, 200))

    # 안내 메시지
    if font:
        small_font = load_font('ENCR10B.TTF', 20)
        small_font.draw(220, 180, 'Press I or ESC to close', (150, 150, 150))
