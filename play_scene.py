"""
플레이 Scene - 실제 게임 플레이 화면
"""
from pico2d import *
import game_framework
import inventory_scene
import random
from warior import Warrior
from child import Child
from camera import Camera
from tile import TileMap
from map_data import load_map
from gnome import Gnome
from paddlefish import Paddlefish
from panda import Panda
from quest_manager import QuestManager, Quest

# Scene 변수
world = []
warrior = None
child = None
camera = None
tilemap = None
cur_character = 'warrior'
show_collision_box = False
quest_manager = None

# UI 이미지
warrior_ui = None
warrior_bar = None
child_ui = None
child_bar = None

# 보스 UI
panda_ui = None
panda_bar = None
boss_panda = None  # 현재 보스로 지정된 판다

# 배경음악
bgm = None

def spawn_monster_group(monster_class, center_x, center_y, count, radius=200, use_tile_coords=False):
    """
    특정 위치 주변에 몬스터 무리를 랜덤하게 생성

    Args:
        monster_class: 몬스터 클래스 (Gnome, Paddlefish, Panda)
        center_x: 중심 X 좌표 (픽셀) 또는 타일 인덱스
        center_y: 중심 Y 좌표 (픽셀) 또는 타일 인덱스
        count: 생성할 몬스터 수
        radius: 중심으로부터의 최대 거리 (기본 200px)
        use_tile_coords: True면 center_x, center_y를 타일 인덱스로 해석 (기본 False)

    Returns:
        list: 생성된 몬스터 객체 리스트
    """
    # 타일 인덱스를 픽셀 좌표로 변환
    if use_tile_coords:
        TILE_SIZE = 64
        # 타일 중심 좌표로 변환
        pixel_center_x = center_x * TILE_SIZE + TILE_SIZE // 2
        pixel_center_y = center_y * TILE_SIZE + TILE_SIZE // 2
    else:
        pixel_center_x = center_x
        pixel_center_y = center_y

    monsters = []
    for i in range(count):
        # 랜덤 오프셋 계산 (원형 분포)
        angle = random.uniform(0, 2 * 3.14159)  # 0 ~ 2π
        distance = random.uniform(0, radius)

        offset_x = distance * random.uniform(-1, 1)  # 더 자연스러운 분포
        offset_y = distance * random.uniform(-1, 1)

        # 몬스터 생성
        monster = monster_class(
            x=pixel_center_x + offset_x,
            y=pixel_center_y + offset_y
        )

        # 타겟 설정 (warrior를 기본 타겟으로)
        if hasattr(monster, 'set_target_character'):
            monster.set_target_character(warrior)

        monsters.append(monster)
        if use_tile_coords:
            print(f"[SPAWN] {monster_class.__name__} 생성 위치: 타일({center_x}, {center_y}) -> 픽셀({monster.x:.0f}, {monster.y:.0f})")
        else:
            print(f"[SPAWN] {monster_class.__name__} 생성 위치: ({monster.x:.0f}, {monster.y:.0f})")

    return monsters

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
    global world, warrior, child, camera, tilemap, gnome, paddlefish, panda, cur_character, show_collision_box, quest_manager
    global warrior_ui, warrior_bar, child_ui, child_bar, panda_ui, panda_bar, boss_panda, bgm

    cur_character = 'warrior'
    show_collision_box = False
    boss_panda = None  # 초기화

    # UI 이미지 로드
    warrior_ui = load_image('resource/warriorUI.png')
    warrior_bar = load_image('resource/warriorBar.png')
    child_ui = load_image('resource/childUI.png')
    child_bar = load_image('resource/childBar.png')

    # 보스 UI 이미지 로드
    panda_ui = load_image('resource/pandaUI.png')
    panda_bar = load_image('resource/warriorBar.png')  # warriorBar 재사용

    # 배경음악 로드 및 반복 재생
    bgm = load_music('resource/background.mp3')
    bgm.set_volume(32)  # 볼륨 설정 (0~128)
    bgm.repeat_play()   # 무한 반복 재생
    print("배경음악 재생 시작")

    # 타일맵 생성 (쿼터뷰 맵)
    print("=== 타일맵 로딩 중... ===")
    map_data = load_map('main')
    tilemap = TileMap(40, 40)
    tilemap.load_from_array(map_data)
    tilemap.debug_mode = False  # 기본 OFF (F3으로 토글)
    print("타일맵 로딩 완료!")

    # 캐릭터 생성 (타일 인덱스 3, 3에 배치)
    TILE_SIZE = 64
    spawn_tile_x = 3
    spawn_tile_y = 3
    spawn_x = spawn_tile_x * TILE_SIZE + TILE_SIZE // 2  # 타일 중심
    spawn_y = spawn_tile_y * TILE_SIZE + TILE_SIZE // 2  # 타일 중심

    warrior = Warrior()
    warrior.x = spawn_x
    warrior.y = spawn_y

    child = Child()
    child.x = spawn_x + 100
    child.y = spawn_y
    child.warrior = warrior  # Warrior 참조 설정

    print(f"캐릭터 생성: 타일({spawn_tile_x}, {spawn_tile_y}) -> 픽셀({spawn_x}, {spawn_y})")

    # 카메라 생성
    camera = Camera()
    camera.set_target(warrior)
    # 맵 크기 설정 (40x40 타일, 타일 크기 64x64)
    camera.set_map_bounds(40 * 64, 40 * 64)  # 2560 x 2560

    # ========================================
    # 몬스터 무리 생성 (타일 인덱스 기반)
    # ========================================
    # spawn_monster_group(몬스터클래스, 중심X, 중심Y, 수량, 반경, use_tile_coords=True)
    # 반경: 몬스터들이 중심으로부터 퍼질 범위 (픽셀 단위)

    print("=== 몬스터 생성 중... ===")

    # Gnome 무리 배치
    gnome_group1 = spawn_monster_group(Gnome, 17, 5, 1, radius=10, use_tile_coords=True)
    gnome_group2 = spawn_monster_group(Gnome, 20, 8, 5, radius=50, use_tile_coords=True)
    gnome_group3 = spawn_monster_group(Gnome, 35, 5, 5, radius=50, use_tile_coords=True)
    gnome_group4 = spawn_monster_group(Gnome, 29, 17, 5, radius=50, use_tile_coords=True)

    # Paddlefish 무리 배치
    paddlefish_group1 = spawn_monster_group(Paddlefish, 6, 12, 3, radius=30, use_tile_coords=True)
    paddlefish_group2 = spawn_monster_group(Paddlefish, 29, 17, 5, radius=70, use_tile_coords=True)
    paddlefish_group3 = spawn_monster_group(Paddlefish, 23, 30, 2, radius=20, use_tile_coords=True)
    paddlefish_group4 = spawn_monster_group(Paddlefish, 5, 34, 5, radius=70, use_tile_coords=True)

    # Panda 보스 배치
    panda_group1 = spawn_monster_group(Panda, 31, 36, 1, radius=10, use_tile_coords=True)

    # 모든 몬스터 리스트 합치기
    gnome_list = gnome_group1 + gnome_group2 + gnome_group3 + gnome_group4
    paddlefish_list = paddlefish_group1 + paddlefish_group2 + paddlefish_group3 + paddlefish_group4
    panda_list = panda_group1

    print(f"생성 완료: Gnome {len(gnome_list)}마리, Paddlefish {len(paddlefish_list)}마리, Panda {len(panda_list)}마리")

    # 월드에 추가
    world = []
    world.append(child)
    world.append(warrior)

    # 생성된 모든 몬스터를 월드에 추가
    world.extend(gnome_list)
    world.extend(paddlefish_list)
    world.extend(panda_list)

    # ========================================
    # 퀘스트 매니저 생성 및 초기 퀘스트 추가
    # ========================================
    # 주의: 퀘스트는 순서대로 진행됩니다!
    #       첫 번째 퀘스트부터 시작하여, 완료해야 다음 퀘스트가 활성화됩니다.
    #
    # 퀘스트 추가 방법:
    #   quest_manager.add_quest(Quest(
    #       quest_id="고유ID",           # 퀘스트 고유 식별자 (중복되면 안됨)
    #       title="퀘스트 제목",          # UI에 표시될 제목
    #       description="퀘스트 설명",    # 퀘스트 상세 설명
    #       target_monster="몬스터이름",  # "Gnome", "Paddlefish", "Panda" 중 하나
    #       target_count=처치수           # 처치해야 할 몬스터 수
    #   ))
    #
    # ========================================

    quest_manager = QuestManager()

    # 퀘스트 1: 놈 처치 (첫 번째 퀘스트 - 자동으로 활성화됨)
    quest_manager.add_quest(Quest(
        quest_id="kill_gnome_2",
        title="노움 처치",
        description="노움을 잡아 판다의 단서를 찾자",
        target_monster="Gnome",
        target_count=2
    ))
    # 퀘스트 2: 놈 사냥 (퀘스트 1 완료 후 활성화)
    quest_manager.add_quest(Quest(
        quest_id="kill_gnome_7",
        title="노움 사냥",
        description="정말 모든 노움이 판다를 모를까?",
        target_monster="Gnome",
        target_count=7
    ))
    # 퀘스트 3: 패들피쉬 처치 (퀘스트 2 완료 후 활성화)
    quest_manager.add_quest(Quest(
        quest_id="kill_paddlefish_3",
        title="패들피쉬 처치",
        description="노움은 아무것도 모른다. 패들피쉬를 잡아 단서를 찾자",
        target_monster="Paddlefish",
        target_count=3
    ))
    # 퀘스트 4: 패들피쉬 소탕 (퀘스트 3 완료 후 활성화)
    quest_manager.add_quest(Quest(
        quest_id="kill_paddlefish_10",
        title="패들피쉬 소탕",
        description="패들피쉬는 무언가를 알고 있다. 소탕하자",
        target_monster="Paddlefish",
        target_count=10
    ))
    # 퀘스트 5: 판다 도전 (퀘스트 4 완료 후 활성화)
    quest_manager.add_quest(Quest(
        quest_id="kill_panda_1",
        title="보스:판다 도전",
        description="드디어 판다의 위치를 알아냈다. 판다를 처치하라!",
        target_monster="Panda",
        target_count=1
    ))

    # ========================================
    # 여기에 새로운 퀘스트를 추가하세요!
    # ========================================
    # 예시:
    # quest_manager.add_quest(Quest(
    #     quest_id="kill_gnome_20",
    #     title="놈 대량 사냥",
    #     description="놈 20마리를 처치하세요",
    #     target_monster="Gnome",
    #     target_count=20
    # ))
    # ========================================

def exit():
    """Scene 종료 시 호출"""
    global world, warrior, child, camera, tilemap
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
        elif event.key == SDLK_9:
            # F3키: 타일맵 디버그 모드 토글
            if tilemap:
                tilemap.toggle_debug_mode()
        elif event.key == SDLK_i:
            # I 키를 누르면 퀘스트 목록 열기
            inventory_scene.quest_manager = quest_manager
            game_framework.push_scene(inventory_scene)
        elif event.key == SDLK_f:
            # F 키로 캐릭터 전환
            if cur_character == 'warrior':
                warrior.keys = {'left': False, 'right': False, 'up': False, 'down': False}
                warrior.state_machine.cur_state = warrior.IDLE
                warrior.IDLE.enter(('STOP', 0))
                cur_character = 'child'
                camera.set_target(child)
                # 모든 몬스터들의 추적 대상 변경
                for obj in world:
                    if hasattr(obj, 'set_target_character'):
                        obj.set_target_character(child)
            else:
                child.keys = {'left': False, 'right': False, 'up': False, 'down': False}
                child.state_machine.cur_state = child.IDLE
                child.IDLE.enter(('STOP', 0))
                cur_character = 'warrior'
                camera.set_target(warrior)
                # 모든 몬스터들의 추적 대상 변경
                for obj in world:
                    if hasattr(obj, 'set_target_character'):
                        obj.set_target_character(warrior)
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

                # Panda가 가드 중이면 공격자를 넉백시킴 (데미지 없음)
                if target_class == 'Panda' and hasattr(target, 'is_guarding') and target.is_guarding():
                    print(f"[DEBUG] *** Panda 가드 성공! {attacker_class} 넉백!")
                    # 공격자를 넉백시킴
                    knockback_distance = 50  # 판다의 가드 넉백은 더 강함
                    if attacker.x > target.x:  # 공격자가 오른쪽에 있으면 오른쪽으로 밀림
                        attacker.x += knockback_distance
                        print(f"[DEBUG] {attacker_class} 넉백: 오른쪽으로 {knockback_distance}px")
                    else:  # 공격자가 왼쪽에 있으면 왼쪽으로 밀림
                        attacker.x -= knockback_distance
                        print(f"[DEBUG] {attacker_class} 넉백: 왼쪽으로 {knockback_distance}px")
                    attacker.hit_targets.add(target_id)
                    continue  # 데미지 처리 없이 넘어감

                # Panda를 공격하면 보스 체력바 활성화
                if target_class == 'Panda' and attacker_class in ['Warrior', 'Child']:
                    global boss_panda
                    boss_panda = target
                    print(f"[BOSS] 판다 보스 체력바 활성화!")

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
    global world, quest_manager, boss_panda

    # 사망한 객체들을 찾아서 제거
    dead_objects = [obj for obj in world if hasattr(obj, 'is_alive') and not obj.is_alive]

    for obj in dead_objects:
        # 몬스터 처치 시 퀘스트 매니저에 알림
        monster_name = obj.__class__.__name__
        if quest_manager and monster_name in ['Gnome', 'Paddlefish', 'Panda']:
            quest_manager.on_monster_killed(monster_name)

        # 보스 판다가 죽으면 체력바 비활성화
        if obj == boss_panda:
            boss_panda = None
            print("[BOSS] 판다 보스 처치! 체력바 비활성화")

        world.remove(obj)
        print(f"{obj.__class__.__name__}이(가) 월드에서 제거되었습니다.")

def update(delta_time):
    """업데이트"""
    global camera, tilemap, cur_character

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

    # Child Power가 0 이하가 되면 강제로 Warrior로 전환
    if cur_character == 'child' and child.hp <= 0:
        print("[AUTO SWITCH] Child Power 소진! Warrior로 강제 전환")
        # Child 키 입력 초기화
        child.keys = {'left': False, 'right': False, 'up': False, 'down': False}
        child.state_machine.cur_state = child.IDLE
        child.IDLE.enter(('STOP', 0))
        # Warrior로 전환
        cur_character = 'warrior'
        camera.set_target(warrior)
        # 모든 몬스터들의 추적 대상 변경
        for obj in world:
            if hasattr(obj, 'set_target_character'):
                obj.set_target_character(warrior)

    # 카메라 타겟 설정
    if cur_character == 'warrior':
        camera.set_target(warrior)
    elif cur_character == 'child':
        camera.set_target(child)

    camera.update(delta_time)

def draw_ui():
    """HP/Power UI 그리기 (좌측 하단)"""
    # Warrior HP UI (좌측 하단)
    ui_x = 120  # UI 중심 X 좌표
    ui_y = 90   # UI 중심 Y 좌표

    # Bar 크기 (실제 이미지 크기에 맞게 조정 필요)
    bar_width = 200   # Bar 이미지의 전체 너비
    bar_height = 30   # Bar 이미지의 높이

    # Warrior HP Bar (뒤에 그리기)
    if warrior and warrior_bar:
        hp_ratio = warrior.hp / warrior.max_hp
        bar_draw_width = int(bar_width * hp_ratio)  # 체력 비율에 따른 너비

        # clip_draw(sx, sy, w, h, x, y, w, h)
        # Bar를 왼쪽부터 체력 비율만큼만 그리기
        if bar_draw_width > 0:
            warrior_bar.clip_draw(
                0, 0, bar_draw_width, bar_height,  # 소스 영역
                ui_x - (bar_width - bar_draw_width) // 2, ui_y,  # 중심 좌표 조정
                bar_draw_width, bar_height  # 그릴 크기
            )

    # Warrior UI (앞에 그리기)
    if warrior_ui:
        warrior_ui.draw(ui_x, ui_y, 240, 70)

    # Child Power UI (Warrior UI 아래)
    child_ui_y = ui_y - 60  # Warrior UI 아래 70px

    # Child Power Bar (뒤에 그리기)
    if child and child_bar:
        # Child는 Power를 표시 (hp 사용)
        power_ratio = child.hp / child.max_hp
        bar_draw_width = int(bar_width * power_ratio)

        if bar_draw_width > 0:
            child_bar.clip_draw(
                0, 0, bar_draw_width, bar_height,
                ui_x - (bar_width - bar_draw_width) // 2, child_ui_y,
                bar_draw_width, bar_height
            )

    # Child UI (앞에 그리기)
    if child_ui:
        child_ui.draw(ui_x, child_ui_y, 240, 70)

def draw_boss_ui():
    """보스 (판다) 체력바 그리기 (화면 상단 중앙)"""
    if not boss_panda or not boss_panda.is_alive:
        return

    # 화면 크기
    canvas_width = get_canvas_width()
    boss_ui_x = canvas_width // 2  # 화면 중앙
    boss_ui_y = 550  # 화면 상단

    # 보스 Bar 크기 (더 크게)
    boss_bar_width = 400
    boss_bar_height = 40

    # Boss HP Bar (뒤에 그리기)
    if panda_bar:
        hp_ratio = boss_panda.hp / boss_panda.max_hp
        bar_draw_width = int(boss_bar_width * hp_ratio)

        if bar_draw_width > 0:
            panda_bar.clip_draw(
                0, 0, 200, 30,  # 소스 영역
                boss_ui_x - (boss_bar_width - bar_draw_width) // 2, boss_ui_y,  # 중심 좌표 조정
                bar_draw_width, boss_bar_height  # 그릴 크기
            )

    # Boss UI (앞에 그리기)
    if panda_ui:
        panda_ui.draw(boss_ui_x, boss_ui_y, 480, 120)  # 더 크게 표시

def draw():
    """렌더링"""

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

    # UI 그리기 (좌측 하단)
    draw_ui()

    # 보스 UI 그리기 (화면 상단)
    draw_boss_ui()

