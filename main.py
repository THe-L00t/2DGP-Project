from pico2d import *
from warior import Warrior
from child import Child
from camera import Camera
from tilemap import TileMap
from gnome import Gnome
from paddlefish import Paddlefish
from panda import Panda
import time
#----------------------------------------------------------------
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
#----------------------------------------------------------------
def handle_events():
    global running, cur_character, camera, show_collision_box

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_0:
            show_collision_box = not show_collision_box
            print(f"충돌 박스 표시: {'ON' if show_collision_box else 'OFF'}")
        elif event.type == SDL_KEYDOWN and event.key == SDLK_f:
            if cur_character == 'warrior':
                # 전사를 정지시키고 Idle 상태로 전환
                warrior.keys = {'left': False, 'right': False, 'up': False, 'down': False}
                warrior.state_machine.cur_state = warrior.IDLE
                warrior.IDLE.enter(('STOP', 0))
                # 아이로 전환
                cur_character = 'child'
                camera.set_target(child)
            else:
                # 아이를 정지시키고 Idle 상태로 전환
                child.keys = {'left': False, 'right': False, 'up': False, 'down': False}
                child.state_machine.cur_state = child.IDLE
                child.IDLE.enter(('STOP', 0))
                # 전사로 전환
                cur_character = 'warrior'
                camera.set_target(warrior)
        else:
            if cur_character == 'warrior':
                warrior.handle_event(event)
            elif cur_character == 'child':
                child.handle_event(event)


#----------------------------------------------------------------
def init_world():
    global world
    global warrior
    global child
    global cur_character
    global camera
    global tilemap
    global gnome
    global paddlefish
    global panda
    global show_collision_box

    cur_character = 'warrior'
    show_collision_box = False  # 충돌 박스 표시 초기값
    warrior = Warrior()
    child = Child()
    camera = Camera()
    camera.set_target(warrior)
    tilemap = TileMap()
    tilemap.load_from_file('maps/test_map.json')

    # 몬스터 생성 (화면 중앙 근처에 배치)
    gnome = Gnome(x=600, y=400)
    gnome.set_target_character(warrior)  # Gnome이 warrior를 추적하도록 설정
    paddlefish = Paddlefish(x=800, y=400)
    panda = Panda(x=1000, y=400)

    world = []

    world.append(child)
    world.append(warrior)
    world.append(gnome)
    world.append(paddlefish)
    world.append(panda)


#----------------------------------------------------------------
def update_world(delta_time):
    tilemap.update(delta_time)
    for object in world:
        object.update(delta_time)

    if cur_character == 'warrior':
        camera.set_target(warrior)
    elif cur_character == 'child':
        camera.set_target(child)

    camera.update(delta_time)
#----------------------------------------------------------------
def render_world():
    clear_canvas()
    tilemap.draw(camera)
    for object in world:
        object.draw(camera)

    # 충돌 박스 그리기 (디버그용 - 0키로 토글)
    if show_collision_box:
        for object in world:
            # 일반 충돌 박스 (빨간색)
            left, bottom, right, top = object.get_bb()
            screen_left, screen_bottom = camera.apply(left, bottom)
            screen_right, screen_top = camera.apply(right, top)
            draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)

            # 공격 충돌 박스 (노란색 - 2개의 사각형으로 구분)
            attack_bb = object.get_attack_bb()
            if attack_bb:
                left, bottom, right, top = attack_bb
                screen_left, screen_bottom = camera.apply(left, bottom)
                screen_right, screen_top = camera.apply(right, top)
                # 공격 박스는 2중 사각형으로 표시
                draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)
                draw_rectangle(screen_left+1, screen_bottom+1, screen_right-1, screen_top-1)

    update_canvas()
#----------------------------------------------------------------
running = True
open_canvas()
init_world()

# deltaTime 계산을 위한 변수
previous_time = time.time()
frame_time = 0.016  # 목표 프레임 시간 (60 FPS)

while running:
    # deltaTime 계산
    current_time = time.time()
    delta_time = current_time - previous_time
    previous_time = current_time

    handle_events()
    update_world(delta_time)
    render_world()
    delay(frame_time)

close_canvas()