"""
게임 프레임워크 - Scene 관리 시스템
"""
from pico2d import *
import time

# 전역 변수
running = True
stack = []
delta_time = 0.0
frame_time = 1.0 / 60  # 60 FPS

def change_scene(scene):
    """현재 scene을 새로운 scene으로 교체"""
    global stack
    if stack:
        stack[-1].exit()
        stack.pop()
    stack.append(scene)
    scene.enter()

def push_scene(scene):
    """현재 scene 위에 새로운 scene을 추가 (오버레이)"""
    global stack
    if stack:
        stack[-1].pause()
    stack.append(scene)
    scene.enter()

def pop_scene():
    """현재 scene을 제거하고 이전 scene으로 복귀"""
    global stack
    if stack:
        stack[-1].exit()
        stack.pop()
    if stack:
        stack[-1].resume()

def quit():
    """게임 종료"""
    global running
    running = False

def run(start_scene):
    """게임 메인 루프 실행"""
    global running, stack, delta_time

    open_canvas()

    # 시작 scene 설정
    stack = [start_scene]
    start_scene.enter()

    previous_time = time.time()

    while running:
        # Delta time 계산
        current_time = time.time()
        delta_time = current_time - previous_time
        previous_time = current_time

        # 이벤트 처리
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                running = False
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                # ESC 키 처리는 각 scene에서 결정
                pass

            # 현재 scene에 이벤트 전달
            if stack:
                stack[-1].handle_events(event)

        # 업데이트
        if stack:
            stack[-1].update(delta_time)

        # 렌더링
        clear_canvas()

        # 모든 scene을 렌더링 (아래부터 위로)
        for scene in stack:
            scene.draw()

        update_canvas()
        delay(frame_time)

    # 종료 처리
    while stack:
        stack[-1].exit()
        stack.pop()

    close_canvas()
