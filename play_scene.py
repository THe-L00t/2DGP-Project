"""
플레이 Scene - 실제 게임 플레이 화면
"""
from pico2d import *
import game_framework
import inventory_scene
from warior import Warrior
from child import Child
from camera import Camera
from tile import TileMap
from map_data import load_map
from gnome import Gnome
from paddlefish import Paddlefish
from panda import Panda

# Scene 변수
world = []
warrior = None
child = None
camera = None
tilemap = None
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
    global world, warrior, child, camera, tilemap, gnome, paddlefish, panda, cur_character, show_collision_box

    cur_character = 'warrior'
    show_collision_box = False

    # 타일맵 생성 (쿼터뷰 맵)
    print("=== 타일맵 로딩 중... ===")
    map_data = load_map('stairs')
    tilemap = TileMap(30, 20)
    tilemap.load_from_array(map_data)
    tilemap.debug_mode = False  # 기본 OFF (F3으로 토글)
    print("타일맵 로딩 완료!")

    # 캐릭터 생성 (맵 중앙에 배치)
    spawn_x = 15 * 64  # 15번째 타일 (중앙)
    spawn_y = 10 * 64  # 10번째 타일

    warrior = Warrior()
    warrior.x = spawn_x
    warrior.y = spawn_y

    child = Child()
    child.x = spawn_x + 100
    child.y = spawn_y

    # 카메라 생성
    camera = Camera()
    camera.set_target(warrior)

    # 몬스터 생성 (맵 곳곳에 배치)
    gnome = Gnome(x=spawn_x + 300, y=spawn_y + 100)
    gnome.set_target_character(warrior)

    paddlefish = Paddlefish(x=spawn_x - 200, y=spawn_y - 150)
    paddlefish.set_target_character(warrior)

    panda = Panda(x=spawn_x + 150, y=spawn_y + 200)

    # 월드에 추가
    world = []
    world.append(child)
    world.append(warrior)
    world.append(gnome)
    world.append(paddlefish)
    world.append(panda)

def exit():
    """Scene 종료 시 호출"""
    global world, warrior, child, camera, tilemap, gnome, paddlefish, panda
    # 리소스 해제는 pico2d가 자동으로 처리

def pause():
    """Scene이 일시정지될 때 호출 (인벤토리 열릴 때)"""
    pass

def resume():
    """Scene이 재개될 때 호출 (인벤토리 닫힐 때)"""
    pass

def handle_events(event):
    """이벤트 처리"""
    global cur_character, camera, show_collision_box, tilemap

    if event.type == SDL_KEYDOWN:
        if event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.key == SDLK_0:
            show_collision_box = not show_collision_box
            print(f"충돌 박스 표시: {'ON' if show_collision_box else 'OFF'}")
        elif event.key == SDLK_F3:
            # F3키: 타일맵 디버그 모드 토글
            if tilemap:
                tilemap.toggle_debug_mode()
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
                # 몬스터들의 추적 대상 변경
                gnome.set_target_character(child)
                paddlefish.set_target_character(child)
            else:
                child.keys = {'left': False, 'right': False, 'up': False, 'down': False}
                child.state_machine.cur_state = child.IDLE
                child.IDLE.enter(('STOP', 0))
                cur_character = 'warrior'
                camera.set_target(warrior)
                # 몬스터들의 추적 대상 변경
                gnome.set_target_character(warrior)
                paddlefish.set_target_character(warrior)
        else:
            # 현재 캐릭터에게 이벤트 전달
            if cur_character == 'warrior':
                warrior.handle_event(event)
            elif cur_character == 'child':
                child.handle_event(event)

    else:
        # 기타 이벤트도 현재 캐릭터에게 전달
        if cur_character == 'warrior':
            warrior.handle_event(event)
        elif cur_character == 'child':
            child.handle_event(event)

def screen_to_world(screen_x, screen_y):
    """스크린 좌표를 월드 좌표로 변환"""
    world_x = camera.x + screen_x
    world_y = camera.y + screen_y
    return world_x, world_y

def check_attack_collisions():
    """공격 충돌 체크 및 데미지 처리"""
    # 모든 오브젝트의 공격 박스를 체크
    for attacker in world:
        attack_bb = attacker.get_attack_bb()

        # 공격 중이 아니면 hit_targets 초기화하고 스킵
        if not attack_bb:
            if hasattr(attacker, 'hit_targets'):
                attacker.hit_targets.clear()
            continue

        # 공격력 가져오기
        attack_power = attacker.get_current_attack_power()
        if attack_power <= 0:
            print(f"[DEBUG] {attacker.__class__.__name__} 공격 중이지만 공격력이 0")
            continue

        print(f"[DEBUG] {attacker.__class__.__name__} 공격 중! 공격력: {attack_power}, 공격 박스: {attack_bb}")

        # hit_targets 초기화 (처음 공격할 때)
        if not hasattr(attacker, 'hit_targets'):
            attacker.hit_targets = set()
            print(f"[DEBUG] {attacker.__class__.__name__} hit_targets 초기화")

        # 다른 오브젝트와의 충돌 체크
        for target in world:
            if attacker == target:
                continue  # 자기 자신은 제외

            # 몬스터끼리는 공격하지 않음
            attacker_class = attacker.__class__.__name__
            target_class = target.__class__.__name__

            # 몬스터 클래스 리스트
            monster_classes = ['Gnome', 'Paddlefish', 'Panda']

            # 공격자와 타겟이 모두 몬스터면 스킵
            if attacker_class in monster_classes and target_class in monster_classes:
                continue

            # 타겟의 히트박스와 공격 박스 충돌 체크
            target_bb = target.get_bb()

            if collide_bb(attack_bb, target_bb):
                # 이번 공격에서 이미 맞았으면 스킵
                target_id = id(target)
                if target_id in attacker.hit_targets:
                    print(f"[DEBUG] {target.__class__.__name__}은(는) 이미 이번 공격에 맞음 (스킵)")
                    continue

                # 데미지 적용 (넉백을 위해 공격자의 x 좌표 전달)
                print(f"[DEBUG] *** 충돌 감지! {attacker.__class__.__name__} -> {target.__class__.__name__}")
                print(f"[DEBUG]     공격 박스: {attack_bb}")
                print(f"[DEBUG]     타겟 박스: {target_bb}")
                target.take_damage(attack_power, attacker.x)
                attacker.hit_targets.add(target_id)

def collide_bb(bb1, bb2):
    """두 바운딩 박스가 충돌하는지 확인"""
    left1, bottom1, right1, top1 = bb1
    left2, bottom2, right2, top2 = bb2

    # AABB 충돌 검사
    if left1 > right2: return False
    if right1 < left2: return False
    if bottom1 > top2: return False
    if top1 < bottom2: return False

    return True

def remove_dead_objects():
    """체력이 0이 된 객체들을 제거"""
    global world

    # 사망한 객체들을 찾아서 제거
    dead_objects = [obj for obj in world if hasattr(obj, 'is_alive') and not obj.is_alive]

    for obj in dead_objects:
        world.remove(obj)
        print(f"{obj.__class__.__name__}이(가) 월드에서 제거되었습니다.")

def update(delta_time):
    """업데이트"""
    global camera, tilemap

    # 타일맵 업데이트
    if tilemap:
        tilemap.update(delta_time)

    # 오브젝트 업데이트 (타일맵 충돌 포함)
    for obj in world:
        # 이동 전 위치 저장
        old_x, old_y = obj.x, obj.y

        # 오브젝트 업데이트
        obj.update(delta_time)

        # 타일맵 충돌 체크 (바운딩 박스가 있는 객체만)
        if tilemap and hasattr(obj, 'get_bb'):
            bb = obj.get_bb()
            if bb:
                obj_width = bb[2] - bb[0]
                obj_height = bb[3] - bb[1]

                # 충돌 시 슬라이딩 처리
                if tilemap.check_collision(obj.x, obj.y, obj_width, obj_height):
                    can_move_x = not tilemap.check_collision(obj.x, old_y, obj_width, obj_height)
                    can_move_y = not tilemap.check_collision(old_x, obj.y, obj_width, obj_height)

                    if not can_move_x:
                        obj.x = old_x
                    if not can_move_y:
                        obj.y = old_y

    # 공격 충돌 체크
    check_attack_collisions()

    # 사망한 객체 제거
    remove_dead_objects()

    # 카메라 타겟 설정
    if cur_character == 'warrior':
        camera.set_target(warrior)
    elif cur_character == 'child':
        camera.set_target(child)

    camera.update(delta_time)

def draw():
    """렌더링"""
    clear_canvas()

    # 타일맵 그리기
    if tilemap:
        tilemap.draw(camera)

    # 오브젝트 그리기
    for obj in world:
        obj.draw(camera)

    # 타일맵 디버그 (충돌박스) - F3으로 토글
    if tilemap and tilemap.debug_mode:
        tilemap.draw_debug(camera)

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
