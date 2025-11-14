"""
플레이 Scene - 실제 게임 플레이 화면
"""
from pico2d import *
import game_framework
import inventory_scene
from warior import Warrior
from child import Child
from camera import Camera
from background_map import BackgroundMap
from gnome import Gnome
from paddlefish import Paddlefish
from panda import Panda

# Scene 변수
world = []
warrior = None
child = None
camera = None
background_map = None
gnome = None
paddlefish = None
panda = None
cur_character = 'warrior'
show_collision_box = False

def collide(a, b):
    """두 객체의 바운딩 박스가 충돌하는지 확인"""
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    # AABB 충돌 검사
    if left_a > right_b: return False
    if right_a < left_b: return False
    if bottom_a > top_b: return False
    if top_a < bottom_b: return False

    return True

def enter():
    """Scene 진입 시 호출"""
    global world, warrior, child, camera, background_map, gnome, paddlefish, panda, cur_character, show_collision_box

    cur_character = 'warrior'
    show_collision_box = False

    # 캐릭터 생성
    warrior = Warrior()
    child = Child()

    # 카메라 생성
    camera = Camera()
    camera.set_target(warrior)

    # 배경 맵 생성
    background_map = BackgroundMap()
    # background_map.load_background('resource/your_background_image.png')  # 배경 이미지 경로 설정
    background_map.load_collision_data('maps/collision_data.json')

    # 몬스터 생성
    gnome = Gnome(x=600, y=400)
    gnome.set_target_character(warrior)
    paddlefish = Paddlefish(x=800, y=400)
    panda = Panda(x=1000, y=400)

    # 월드에 추가
    world = []
    world.append(child)
    world.append(warrior)
    world.append(gnome)
    world.append(paddlefish)
    world.append(panda)

def exit():
    """Scene 종료 시 호출"""
    global world, warrior, child, camera, background_map, gnome, paddlefish, panda
    # 리소스 해제는 pico2d가 자동으로 처리

def pause():
    """Scene이 일시정지될 때 호출 (인벤토리 열릴 때)"""
    pass

def resume():
    """Scene이 재개될 때 호출 (인벤토리 닫힐 때)"""
    pass

def handle_events(event):
    """이벤트 처리"""
    global cur_character, camera, show_collision_box, background_map

    if event.type == SDL_KEYDOWN:
        if event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.key == SDLK_0:
            show_collision_box = not show_collision_box
            print(f"충돌 박스 표시: {'ON' if show_collision_box else 'OFF'}")
        elif event.key == SDLK_9:
            # 9키: 충돌 블럭 에디터 모드 토글
            if background_map:
                background_map.toggle_editor_mode()
        elif event.key == SDLK_8:
            # 8키: 충돌 데이터 저장
            if background_map:
                background_map.save_collision_data('maps/collision_data.json')
        elif event.key == SDLK_i:
            # I 키를 누르면 인벤토리 열기
            game_framework.push_scene(inventory_scene)
        elif event.key == SDLK_f:
            # F 키로 캐릭터 전환
            if cur_character == 'warrior':
                warrior.keys = {'left': False, 'right': False, 'up': False, 'down': False}
                warrior.state_machine.cur_state = warrior.IDLE
                warrior.IDLE.enter(('STOP', 0))
                cur_character = 'child'
                camera.set_target(child)
            else:
                child.keys = {'left': False, 'right': False, 'up': False, 'down': False}
                child.state_machine.cur_state = child.IDLE
                child.IDLE.enter(('STOP', 0))
                cur_character = 'warrior'
                camera.set_target(warrior)
        else:
            # 에디터 모드가 아닐 때만 캐릭터에게 이벤트 전달
            if not (background_map and background_map.editor_mode):
                # 현재 캐릭터에게 이벤트 전달
                if cur_character == 'warrior':
                    warrior.handle_event(event)
                elif cur_character == 'child':
                    child.handle_event(event)
            else:
                # 에디터 모드일 때 키 입력 처리
                if background_map:
                    background_map.editor_handle_key(event.key)

    elif event.type == SDL_MOUSEBUTTONDOWN:
        # 마우스 클릭 이벤트 (에디터 모드)
        if background_map and background_map.editor_mode:
            mouse_x, mouse_y = event.x, get_canvas_height() - event.y
            world_x, world_y = screen_to_world(mouse_x, mouse_y)
            background_map.editor_handle_mouse_down(world_x, world_y, event.button)

    elif event.type == SDL_MOUSEBUTTONUP:
        # 마우스 릴리즈 이벤트 (에디터 모드)
        if background_map and background_map.editor_mode:
            mouse_x, mouse_y = event.x, get_canvas_height() - event.y
            world_x, world_y = screen_to_world(mouse_x, mouse_y)
            background_map.editor_handle_mouse_up(world_x, world_y, event.button)

    elif event.type == SDL_MOUSEMOTION:
        # 마우스 이동 이벤트 (에디터 모드)
        if background_map and background_map.editor_mode:
            mouse_x, mouse_y = event.x, get_canvas_height() - event.y
            world_x, world_y = screen_to_world(mouse_x, mouse_y)
            background_map.editor_handle_mouse_motion(world_x, world_y)

    else:
        # 기타 이벤트도 현재 캐릭터에게 전달
        if not (background_map and background_map.editor_mode):
            if cur_character == 'warrior':
                warrior.handle_event(event)
            elif cur_character == 'child':
                child.handle_event(event)

def screen_to_world(screen_x, screen_y):
    """스크린 좌표를 월드 좌표로 변환"""
    world_x = camera.x + screen_x
    world_y = camera.y + screen_y
    return world_x, world_y

def update(delta_time):
    """업데이트"""
    global camera, background_map

    # 맵 업데이트
    if background_map:
        background_map.update(delta_time)

    # 에디터 모드가 아닐 때만 오브젝트 업데이트
    if not (background_map and background_map.editor_mode):
        for obj in world:
            obj.update(delta_time)

    # 카메라 타겟 설정
    if cur_character == 'warrior':
        camera.set_target(warrior)
    elif cur_character == 'child':
        camera.set_target(child)

    camera.update(delta_time)

def draw():
    """렌더링"""
    # 배경 맵 그리기
    if background_map:
        background_map.draw(camera)

    # 오브젝트 그리기
    for obj in world:
        obj.draw(camera)

    # 충돌 박스 그리기 (디버그용 - 0키로 토글)
    if show_collision_box:
        for obj in world:
            # 일반 충돌 박스 (빨간색)
            left, bottom, right, top = obj.get_bb()
            screen_left, screen_bottom = camera.apply(left, bottom)
            screen_right, screen_top = camera.apply(right, top)
            draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)

            # 공격 충돌 박스 (2중 사각형)
            attack_bb = obj.get_attack_bb()
            if attack_bb:
                left, bottom, right, top = attack_bb
                screen_left, screen_bottom = camera.apply(left, bottom)
                screen_right, screen_top = camera.apply(right, top)
                # 공격 박스는 2중 사각형으로 표시
                draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)
                draw_rectangle(screen_left+1, screen_bottom+1, screen_right-1, screen_top-1)

    # 충돌 블럭 그리기
    if background_map:
        # 에디터 모드이거나 충돌 박스 표시가 켜져있으면 그리기
        if background_map.editor_mode or show_collision_box:
            background_map.draw_collision_blocks(camera)

        # 에디터 UI 그리기
        if background_map.editor_mode:
            background_map.draw_editor_ui(camera)
