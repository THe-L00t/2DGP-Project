"""
타이틀 Scene - 게임 시작 화면
"""
from pico2d import *
import game_framework
import play_scene

# Scene 변수
image = None

def enter():
    """Scene 진입 시 호출"""
    global image
    # TODO: 타이틀 배경 이미지 로드
    image = load_image('resource/title.png')
    pass

def exit():
    """Scene 종료 시 호출"""
    global image
    # 리소스 해제는 pico2d가 자동으로 처리
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
        if event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.key == SDLK_SPACE or event.key == SDLK_RETURN:
            # Space 또는 Enter 키를 누르면 게임 시작
            game_framework.change_scene(play_scene)

def update(delta_time):
    """업데이트"""
    pass

def draw():
    """렌더링"""
    # 타이틀 배경 이미지를 창 크기에 맞게 그리기
    if image:
        # 캔버스 크기 가져오기
        canvas_width = get_canvas_width()
        canvas_height = get_canvas_height()

        # 이미지를 캔버스 크기에 맞게 늘려서 그리기
        image.draw(canvas_width // 2, canvas_height // 2, canvas_width, canvas_height)
