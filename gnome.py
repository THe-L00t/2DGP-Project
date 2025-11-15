from pico2d import *
from state_machine import StateMachine
import random
import math

#----------------------------------------------------------------
# Gnome - 무작위 이동 및 공격 몬스터 (캐릭터 추적 AI)
#----------------------------------------------------------------

# ============================================================
# 전역 설정 - 여기서 일괄 수정
# ============================================================
PIXEL_WIDTH = 192   # 스프라이트 가로 픽셀 크기
PIXEL_HEIGHT = 192  # 스프라이트 세로 픽셀 크기

# 애니메이션 프레임 수
IDLE_FRAMES = 8
ATTACK_FRAMES = 6
RUN_FRAMES = 6

# 충돌 박스 크기
COLLISION_HALF_WIDTH = 45
COLLISION_HALF_HEIGHT = 45

# 공격 박스 크기
ATTACK_RANGE = 70
ATTACK_HEIGHT = 40

# 캐릭터 감지 범위
DETECTION_RANGE = 300  # 추적 범위
ATTACK_DETECTION_RANGE = 100  # 공격 범위

# 이동 속도
MOVE_SPEED = 200
CHASE_SPEED = 250

# 체력
MAX_HP = 100
# ============================================================

class GnomeIdle:
    """Gnome의 대기 상태"""
    def __init__(self, gnome):
        self.gnome = gnome
        self.animation_speed = 7  # 초당 프레임 수
        self.idle_time = 0
        self.max_idle_time = 1.0  # 1초 대기 후 이동

    def enter(self, e):
        self.gnome.frame = 0
        self.gnome.dirx = 0
        self.gnome.diry = 0
        self.idle_time = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        self.gnome.frame = (self.gnome.frame + self.animation_speed * delta_time) % IDLE_FRAMES

        # 쿨다운 감소
        if self.gnome.attack_cooldown > 0:
            self.gnome.attack_cooldown -= delta_time
            if self.gnome.attack_cooldown <= 0:
                self.gnome.attack_cooldown = 0
                print(f"[DEBUG] Gnome 쿨다운 종료! 다시 공격 가능")

        # 캐릭터 감지 및 상태 전환
        if self.gnome.check_character_in_range():
            distance = self.gnome.get_distance_to_character()

            # 쿨다운 중에는 상태 전환하지 않고 IDLE 유지
            if self.gnome.attack_cooldown > 0:
                print(f"[DEBUG] 쿨다운 중... 남은 시간: {self.gnome.attack_cooldown:.2f}초")
                return

            # 쿨다운이 끝났을 때만 상태 전환
            if distance < ATTACK_DETECTION_RANGE:  # 공격 범위
                self.gnome.state_machine.cur_state = self.gnome.ATTACK
                self.gnome.ATTACK.enter(('DETECT_CHARACTER', 0))
                return
            elif distance < DETECTION_RANGE:  # 추적 범위
                self.gnome.state_machine.cur_state = self.gnome.CHASE
                self.gnome.CHASE.enter(('DETECT_CHARACTER', 0))
                return

        # 대기 시간 체크 (쿨다운 중에는 배회하지 않음)
        if self.gnome.attack_cooldown <= 0:
            self.idle_time += delta_time
            if self.idle_time >= self.max_idle_time:
                # 무작위로 RUN 상태로 전환
                self.gnome.state_machine.cur_state = self.gnome.RUN
                self.gnome.RUN.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.gnome.x, self.gnome.y)
        else:
            screen_x, screen_y = self.gnome.x, self.gnome.y

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.gnome.face_dir == 1:
            self.gnome.imageI.clip_draw(int(self.gnome.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.gnome.imageI.clip_composite_draw(int(self.gnome.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class GnomeAttack:
    """Gnome의 공격 상태"""
    def __init__(self, gnome):
        self.gnome = gnome
        self.animation_speed = 8  # 초당 프레임 수 (느리게 조정)
        self.attack_time = 0
        self.max_attack_time = 0.75  # 0.75초 공격 애니메이션 (6프레임 / 8fps = 0.75초)

    def enter(self, e):
        self.gnome.frame = 0
        self.attack_time = 0
        self.gnome.dirx = 0
        self.gnome.diry = 0
        self.has_attacked = False  # 공격 판정을 한 번만 하기 위한 플래그
        print(f"[DEBUG] Gnome ATTACK 상태 진입 (frame: {self.gnome.frame})")

    def exit(self, e):
        # 공격 후 쿨다운 시작
        self.gnome.attack_cooldown = 2.0  # 2초 쿨다운
        print(f"[DEBUG] Gnome ATTACK 종료, 2초 쿨다운 시작")

    def do(self, delta_time):
        # 공격 시간 증가
        self.attack_time += delta_time

        # 애니메이션 프레임 업데이트 (6프레임, 애니메이션 속도 8fps)
        self.gnome.frame = (self.gnome.frame + self.animation_speed * delta_time)

        # 애니메이션이 끝까지 재생되도록 보장 (프레임이 6을 넘지 않도록)
        if self.gnome.frame >= ATTACK_FRAMES:
            self.gnome.frame = ATTACK_FRAMES - 0.01  # 마지막 프레임에 고정

        # 공격 시간이 끝났는지 체크 (애니메이션 완전 재생 보장)
        if self.attack_time >= self.max_attack_time:
            print(f"[DEBUG] Gnome 공격 애니메이션 종료 (최종 프레임: {self.gnome.frame:.2f})")
            # 한 번의 공격 후 무조건 IDLE로 전환 (2초 쿨다운)
            self.gnome.state_machine.cur_state = self.gnome.IDLE
            self.gnome.IDLE.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.gnome.x, self.gnome.y)
        else:
            screen_x, screen_y = self.gnome.x, self.gnome.y

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.gnome.face_dir == 1:
            self.gnome.imageA.clip_draw(int(self.gnome.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.gnome.imageA.clip_composite_draw(int(self.gnome.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class GnomeRun:
    """Gnome의 이동 상태"""
    def __init__(self, gnome):
        self.gnome = gnome
        self.animation_speed = 9  # 초당 프레임 수
        self.move_speed = 200  # 초당 픽셀 수
        self.run_time = 0
        self.max_run_time = 2.0  # 2초 이동 후 다른 상태로 전환

    def enter(self, e):
        self.gnome.frame = 0
        self.run_time = 0

        # 상하좌우 무작위 방향 선택 (8방향)
        directions = [
            (1, 0),    # 우
            (-1, 0),   # 좌
            (0, 1),    # 상
            (0, -1),   # 하
            (1, 1),    # 우상
            (1, -1),   # 우하
            (-1, 1),   # 좌상
            (-1, -1)   # 좌하
        ]
        chosen_dir = random.choice(directions)
        self.gnome.dirx = chosen_dir[0]
        self.gnome.diry = chosen_dir[1]

        # 좌우 방향만 face_dir에 반영
        if self.gnome.dirx != 0:
            self.gnome.face_dir = self.gnome.dirx

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.gnome.frame = (self.gnome.frame + self.animation_speed * delta_time) % 6

        # 캐릭터 감지 및 상태 전환
        if self.gnome.check_character_in_range():
            distance = self.gnome.get_distance_to_character()

            # 쿨다운 중에는 IDLE로 전환 (쿨다운 대기)
            if self.gnome.attack_cooldown > 0:
                self.gnome.state_machine.cur_state = self.gnome.IDLE
                self.gnome.IDLE.enter(('COOLDOWN_WAIT', 0))
                return

            # 쿨다운이 끝났을 때만 공격/추적
            if distance < ATTACK_DETECTION_RANGE:  # 공격 범위
                self.gnome.state_machine.cur_state = self.gnome.ATTACK
                self.gnome.ATTACK.enter(('DETECT_CHARACTER', 0))
                return
            elif distance < DETECTION_RANGE:  # 추적 범위
                self.gnome.state_machine.cur_state = self.gnome.CHASE
                self.gnome.CHASE.enter(('DETECT_CHARACTER', 0))
                return

        # 대각선 이동 시 속도 보정 (√2로 나눔)
        if self.gnome.dirx != 0 and self.gnome.diry != 0:
            normalized_speed = self.move_speed / 1.414
        else:
            normalized_speed = self.move_speed

        # 무작위 방향으로 이동
        self.gnome.x += self.gnome.dirx * normalized_speed * delta_time
        self.gnome.y += self.gnome.diry * normalized_speed * delta_time

        # 이동 시간 체크
        self.run_time += delta_time
        if self.run_time >= self.max_run_time:
            # 이동 후 IDLE 상태로 전환
            self.gnome.state_machine.cur_state = self.gnome.IDLE
            self.gnome.IDLE.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.gnome.x, self.gnome.y)
        else:
            screen_x, screen_y = self.gnome.x, self.gnome.y

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.gnome.face_dir == 1:
            self.gnome.imageR.clip_draw(int(self.gnome.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.gnome.imageR.clip_composite_draw(int(self.gnome.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class GnomeChase:
    """Gnome의 캐릭터 추적 상태"""
    def __init__(self, gnome):
        self.gnome = gnome
        self.animation_speed = 9  # 초당 프레임 수
        self.chase_speed = 250  # 추적 속도 (일반 이동보다 빠름)

    def enter(self, e):
        self.gnome.frame = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.gnome.frame = (self.gnome.frame + self.animation_speed * delta_time) % 6

        # 캐릭터가 있는지 체크
        if not self.gnome.check_character_in_range():
            # 캐릭터가 없으면 IDLE로 전환
            self.gnome.state_machine.cur_state = self.gnome.IDLE
            self.gnome.IDLE.enter(('LOSE_CHARACTER', 0))
            return

        # 쿨다운 중에는 IDLE로 전환 (쿨다운 대기)
        if self.gnome.attack_cooldown > 0:
            self.gnome.state_machine.cur_state = self.gnome.IDLE
            self.gnome.IDLE.enter(('COOLDOWN_WAIT', 0))
            return

        # 캐릭터까지의 거리 계산
        distance = self.gnome.get_distance_to_character()

        # ============================================================
        # TODO: 공격 범위를 조정하세요 (현재: 100픽셀)
        # ============================================================
        if distance < 100:  # 공격 범위 도달
            # 쿨다운이 끝났으므로 공격
            self.gnome.state_machine.cur_state = self.gnome.ATTACK
            self.gnome.ATTACK.enter(('REACH_CHARACTER', 0))
            return

        # ============================================================
        # TODO: 추적 범위를 조정하세요 (현재: 300픽셀)
        # ============================================================
        if distance >= 300:  # 추적 범위를 벗어남
            self.gnome.state_machine.cur_state = self.gnome.IDLE
            self.gnome.IDLE.enter(('LOSE_CHARACTER', 0))
            return

        # 캐릭터를 향해 이동
        target_x, target_y = self.gnome.get_character_position()
        dx = target_x - self.gnome.x
        dy = target_y - self.gnome.y

        # 방향 정규화
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            dx /= distance
            dy /= distance

            # 이동
            self.gnome.x += dx * self.chase_speed * delta_time
            self.gnome.y += dy * self.chase_speed * delta_time

            # 좌우 방향 설정
            if dx > 0:
                self.gnome.face_dir = 1
            elif dx < 0:
                self.gnome.face_dir = -1

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.gnome.x, self.gnome.y)
        else:
            screen_x, screen_y = self.gnome.x, self.gnome.y

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.gnome.face_dir == 1:
            self.gnome.imageR.clip_draw(int(self.gnome.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.gnome.imageR.clip_composite_draw(int(self.gnome.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class Gnome:
    """무작위 배회 및 공격 몬스터 - IDLE, ATTACK, RUN, CHASE 상태를 가짐"""
    def __init__(self, x=600, y=350, target_character=None):
        self.x, self.y = x, y
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = 1
        self.target_character = target_character  # 추적할 캐릭터

        # 체력
        self.hp = MAX_HP
        self.max_hp = MAX_HP

        # 공격력
        self.attack_power = 15  # Gnome의 공격력

        # 공격 쿨다운
        self.attack_cooldown = 0  # 0이면 공격 가능

        # 생존 상태
        self.is_alive = True

        # TODO: 이미지 파일 경로를 실제 파일로 변경하세요
        self.imageI = load_image('resource/Gnome_Idle.png')    # 대기 애니메이션
        self.imageR = load_image('resource/Gnome_Run.png')     # 달리기 애니메이션
        self.imageA = load_image('resource/Gnome_Attack.png')  # 공격 애니메이션

        # 상태 초기화
        self.IDLE = GnomeIdle(self)
        self.ATTACK = GnomeAttack(self)
        self.RUN = GnomeRun(self)
        self.CHASE = GnomeChase(self)

        # 상태 머신 초기화
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {},     # 캐릭터 감지 시 CHASE 또는 ATTACK으로 전환
                self.ATTACK: {},   # 공격 후 CHASE 또는 IDLE로 전환
                self.RUN: {},      # 배회 중 캐릭터 감지 시 CHASE로 전환
                self.CHASE: {}     # 추적 중 공격 범위 도달 시 ATTACK으로 전환
            }
        )

    def set_target_character(self, character):
        """추적할 캐릭터 설정"""
        self.target_character = character

    def check_character_in_range(self):
        """캐릭터가 범위 내에 있는지 체크"""
        if self.target_character is None:
            return False
        return True

    def get_distance_to_character(self):
        """캐릭터까지의 거리 계산"""
        if self.target_character is None:
            return float('inf')

        dx = self.target_character.x - self.x
        dy = self.target_character.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def get_character_position(self):
        """캐릭터의 위치 반환"""
        if self.target_character is None:
            return self.x, self.y
        return self.target_character.x, self.target_character.y

    def update(self, delta_time):
        self.state_machine.update(delta_time)

    def draw(self, camera=None):
        self.state_machine.draw(camera)

    def handle_event(self, event):
        # AI 몬스터는 플레이어 입력을 받지 않음
        pass

    def get_bb(self):
        """충돌 박스"""
        # TODO: 히트박스 크기를 몬스터에 맞게 조정하세요
        half_width = 45
        half_height = 45
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height

    def get_attack_bb(self):
        """공격 충돌 박스 반환 (공격 중일 때만)"""
        # 공격 상태가 아니면 None 반환
        if self.state_machine.cur_state != self.ATTACK:
            return None

        # 공격 애니메이션의 특정 프레임에서만 공격 판정 (프레임 3~4, 중후반부)
        current_frame = int(self.frame)
        if not (3 <= current_frame <= 4):
            return None

        # 공격 판정 플래그 설정 (한 번만 데미지 처리하기 위함)
        attack_state = self.state_machine.cur_state
        if hasattr(attack_state, 'has_attacked'):
            if not attack_state.has_attacked:
                attack_state.has_attacked = True
                print(f"[DEBUG] Gnome 공격 판정 활성화! (프레임: {current_frame})")

        # TODO: 공격 범위를 조정하세요
        attack_range = 70  # 공격 범위
        attack_height = 40 # 공격 박스 높이

        # 바라보는 방향에 따라 공격 박스 위치 설정
        if self.face_dir == 1:  # 오른쪽
            left = self.x
            right = self.x + attack_range
        else:  # 왼쪽
            left = self.x - attack_range
            right = self.x

        bottom = self.y - attack_height // 2
        top = self.y + attack_height // 2

        return left, bottom, right, top

    def get_current_attack_power(self):
        """현재 공격력 반환 (공격 중일 때만)"""
        if self.state_machine.cur_state == self.ATTACK:
            return self.attack_power
        return 0

    def take_damage(self, damage, attacker_x=None):
        """데미지를 받음 (넉백 포함)"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"Gnome이 {damage} 데미지를 받음! (남은 HP: {self.hp}/{self.max_hp})")

        # 넉백 효과 (공격자 위치 기반)
        if attacker_x is not None:
            knockback_distance = 20  # 밀려나는 거리
            if self.x > attacker_x:  # 공격자가 왼쪽에 있으면 오른쪽으로 밀림
                self.x += knockback_distance
                print(f"[DEBUG] Gnome 넉백: 오른쪽으로 {knockback_distance}px")
            else:  # 공격자가 오른쪽에 있으면 왼쪽으로 밀림
                self.x -= knockback_distance
                print(f"[DEBUG] Gnome 넉백: 왼쪽으로 {knockback_distance}px")

        if self.hp <= 0:
            print("Gnome 사망!")
            self.is_alive = False

#----------------------------------------------------------------
