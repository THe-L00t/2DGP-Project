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
    # image = load_image('resource/title_background.png')
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
    # TODO: 타이틀 배경 이미지 그리기
    if image:
        image.draw(400, 300)  # 화면 중앙에 그리기 (화면 크기에 맞게 조정 필요)
