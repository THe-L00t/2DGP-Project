from pico2d import *
from state_machine import StateMachine
import random
import math

#----------------------------------------------------------------
# Paddlefish - 순찰 및 공격 몬스터 (피격 시 캐릭터 추적)
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

# 애니메이션 속도 (초당 프레임)
IDLE_ANIMATION_SPEED = 6
RUN_ANIMATION_SPEED = 8
ATTACK_ANIMATION_SPEED = 8
CHASE_ANIMATION_SPEED = 9

# 충돌 박스 크기
COLLISION_HALF_WIDTH = 40
COLLISION_HALF_HEIGHT = 40

# 공격 박스 크기
ATTACK_RANGE = 65
ATTACK_HEIGHT = 35

# 공격 판정 프레임 (애니메이션의 어느 프레임에서 공격 판정이 나갈지)
ATTACK_HIT_FRAME_START = 3
ATTACK_HIT_FRAME_END = 4

# 이동 속도
PATROL_SPEED = 150      # 배회 속도
CHASE_SPEED = 250       # 추적 속도

# 상태 지속 시간
IDLE_DURATION = 2.0     # IDLE 상태 지속 시간
RUN_DURATION = 3.0      # RUN 상태 지속 시간
ATTACK_DURATION = 0.75  # 공격 애니메이션 시간 (6프레임 / 8fps)

# 추적 관련 설정
DETECTION_RANGE = 300   # 추적 범위 (이 거리 안에 캐릭터가 있으면 추적)
ATTACK_DETECTION_RANGE = 100  # 공격 범위 (이 거리 안에 들어오면 공격)
CHASE_DURATION = 5.0    # 피격 후 추적 지속 시간

# 공격 쿨다운
ATTACK_COOLDOWN = 2.0   # 공격 후 쿨다운 시간

# 체력 및 공격력
MAX_HP = 80
ATTACK_POWER = 12
# ============================================================

class PaddlefishIdle:
    """Paddlefish의 대기 상태"""
    def __init__(self, paddlefish):
        self.paddlefish = paddlefish
        self.animation_speed = IDLE_ANIMATION_SPEED
        self.idle_time = 0
        self.max_idle_time = IDLE_DURATION

    def enter(self, e):
        self.paddlefish.frame = 0
        self.paddlefish.dirx = 0
        self.paddlefish.diry = 0
        self.idle_time = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        self.paddlefish.frame = (self.paddlefish.frame + self.animation_speed * delta_time) % IDLE_FRAMES

        # 쿨다운 감소
        if self.paddlefish.attack_cooldown > 0:
            self.paddlefish.attack_cooldown -= delta_time
            if self.paddlefish.attack_cooldown <= 0:
                self.paddlefish.attack_cooldown = 0
                print(f"[DEBUG] Paddlefish 쿨다운 종료! 다시 공격 가능")

        # 추적 모드인지 체크
        if self.paddlefish.is_chasing:
            # 추적 시간 감소
            self.paddlefish.chase_time -= delta_time
            if self.paddlefish.chase_time <= 0:
                # 추적 종료
                self.paddlefish.is_chasing = False
                print(f"[DEBUG] Paddlefish 추적 종료")

            # 캐릭터 감지 및 상태 전환
            if self.paddlefish.check_character_in_range():
                distance = self.paddlefish.get_distance_to_character()

                # 쿨다운 중에는 상태 전환하지 않고 IDLE 유지
                if self.paddlefish.attack_cooldown > 0:
                    print(f"[DEBUG] Paddlefish 쿨다운 중... 남은 시간: {self.paddlefish.attack_cooldown:.2f}초")
                    return

                # 쿨다운이 끝났을 때만 상태 전환
                if distance < ATTACK_DETECTION_RANGE:  # 공격 범위
                    self.paddlefish.state_machine.cur_state = self.paddlefish.ATTACK
                    self.paddlefish.ATTACK.enter(('DETECT_CHARACTER', 0))
                    return
                elif distance < DETECTION_RANGE:  # 추적 범위
                    self.paddlefish.state_machine.cur_state = self.paddlefish.CHASE
                    self.paddlefish.CHASE.enter(('DETECT_CHARACTER', 0))
                    return

        # 대기 시간 체크 (추적 중이 아니고 쿨다운이 없을 때만)
        if not self.paddlefish.is_chasing and self.paddlefish.attack_cooldown <= 0:
            self.idle_time += delta_time
            if self.idle_time >= self.max_idle_time:
                # 무작위로 RUN 상태로 전환
                self.paddlefish.state_machine.cur_state = self.paddlefish.RUN
                self.paddlefish.RUN.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.paddlefish.x, self.paddlefish.y)
        else:
            screen_x, screen_y = self.paddlefish.x, self.paddlefish.y

        if self.paddlefish.face_dir == 1:
            self.paddlefish.imageI.clip_draw(int(self.paddlefish.frame) * PIXEL_WIDTH, 0, PIXEL_WIDTH, PIXEL_HEIGHT, screen_x, screen_y)
        else:
            self.paddlefish.imageI.clip_composite_draw(int(self.paddlefish.frame) * PIXEL_WIDTH, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 0, 'h', screen_x, screen_y, PIXEL_WIDTH, PIXEL_HEIGHT)

#----------------------------------------------------------------
class PaddlefishAttack:
    """Paddlefish의 공격 상태"""
    def __init__(self, paddlefish):
        self.paddlefish = paddlefish
        self.animation_speed = ATTACK_ANIMATION_SPEED
        self.attack_time = 0
        self.max_attack_time = ATTACK_DURATION

    def enter(self, e):
        self.paddlefish.frame = 0
        self.attack_time = 0
        self.paddlefish.dirx = 0
        self.paddlefish.diry = 0
        self.has_attacked = False  # 공격 판정을 한 번만 하기 위한 플래그
        print(f"[DEBUG] Paddlefish ATTACK 상태 진입 (frame: {self.paddlefish.frame})")

    def exit(self, e):
        # 공격 후 쿨다운 시작
        self.paddlefish.attack_cooldown = ATTACK_COOLDOWN
        print(f"[DEBUG] Paddlefish ATTACK 종료, {ATTACK_COOLDOWN}초 쿨다운 시작")

    def do(self, delta_time):
        # 공격 시간 증가
        self.attack_time += delta_time

        # 애니메이션 프레임 업데이트
        self.paddlefish.frame = (self.paddlefish.frame + self.animation_speed * delta_time)

        # 애니메이션이 끝까지 재생되도록 보장
        if self.paddlefish.frame >= ATTACK_FRAMES:
            self.paddlefish.frame = ATTACK_FRAMES - 0.01

        # 공격 시간이 끝났는지 체크 (애니메이션 완전 재생 보장)
        if self.attack_time >= self.max_attack_time:
            print(f"[DEBUG] Paddlefish 공격 애니메이션 종료 (최종 프레임: {self.paddlefish.frame:.2f})")
            # 한 번의 공격 후 무조건 IDLE로 전환
            self.paddlefish.state_machine.cur_state = self.paddlefish.IDLE
            self.paddlefish.IDLE.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.paddlefish.x, self.paddlefish.y)
        else:
            screen_x, screen_y = self.paddlefish.x, self.paddlefish.y

        if self.paddlefish.face_dir == 1:
            self.paddlefish.imageA.clip_draw(int(self.paddlefish.frame) * PIXEL_WIDTH, 0, PIXEL_WIDTH, PIXEL_HEIGHT, screen_x, screen_y)
        else:
            self.paddlefish.imageA.clip_composite_draw(int(self.paddlefish.frame) * PIXEL_WIDTH, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 0, 'h', screen_x, screen_y, PIXEL_WIDTH, PIXEL_HEIGHT)

#----------------------------------------------------------------
class PaddlefishRun:
    """Paddlefish의 배회 상태"""
    def __init__(self, paddlefish):
        self.paddlefish = paddlefish
        self.animation_speed = RUN_ANIMATION_SPEED
        self.move_speed = PATROL_SPEED
        self.run_time = 0
        self.max_run_time = RUN_DURATION

    def enter(self, e):
        self.paddlefish.frame = 0
        self.run_time = 0
        # 랜덤한 좌우 방향 선택
        directions = [-1, 1]
        self.paddlefish.dirx = random.choice(directions)
        self.paddlefish.face_dir = self.paddlefish.dirx

    def exit(self, e):
        pass

    def do(self, delta_time):
        self.paddlefish.frame = (self.paddlefish.frame + self.animation_speed * delta_time) % RUN_FRAMES

        # 추적 모드인지 체크
        if self.paddlefish.is_chasing:
            # 추적 시간 감소
            self.paddlefish.chase_time -= delta_time
            if self.paddlefish.chase_time <= 0:
                # 추적 종료
                self.paddlefish.is_chasing = False
                print(f"[DEBUG] Paddlefish 추적 종료")

            # 캐릭터 감지 및 상태 전환
            if self.paddlefish.check_character_in_range():
                distance = self.paddlefish.get_distance_to_character()

                # 쿨다운 중에는 IDLE로 전환 (쿨다운 대기)
                if self.paddlefish.attack_cooldown > 0:
                    self.paddlefish.state_machine.cur_state = self.paddlefish.IDLE
                    self.paddlefish.IDLE.enter(('COOLDOWN_WAIT', 0))
                    return

                # 쿨다운이 끝났을 때만 공격/추적
                if distance < ATTACK_DETECTION_RANGE:  # 공격 범위
                    self.paddlefish.state_machine.cur_state = self.paddlefish.ATTACK
                    self.paddlefish.ATTACK.enter(('DETECT_CHARACTER', 0))
                    return
                elif distance < DETECTION_RANGE:  # 추적 범위
                    self.paddlefish.state_machine.cur_state = self.paddlefish.CHASE
                    self.paddlefish.CHASE.enter(('DETECT_CHARACTER', 0))
                    return

        # 좌우 이동
        self.paddlefish.x += self.paddlefish.dirx * self.move_speed * delta_time

        # 이동 시간 체크
        self.run_time += delta_time
        if self.run_time >= self.max_run_time:
            # 이동 후 IDLE 상태로 전환
            self.paddlefish.state_machine.cur_state = self.paddlefish.IDLE
            self.paddlefish.IDLE.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.paddlefish.x, self.paddlefish.y)
        else:
            screen_x, screen_y = self.paddlefish.x, self.paddlefish.y

        if self.paddlefish.face_dir == 1:
            self.paddlefish.imageR.clip_draw(int(self.paddlefish.frame) * PIXEL_WIDTH, 0, PIXEL_WIDTH, PIXEL_HEIGHT, screen_x, screen_y)
        else:
            self.paddlefish.imageR.clip_composite_draw(int(self.paddlefish.frame) * PIXEL_WIDTH, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 0, 'h', screen_x, screen_y, PIXEL_WIDTH, PIXEL_HEIGHT)

#----------------------------------------------------------------
class PaddlefishChase:
    """Paddlefish의 캐릭터 추적 상태"""
    def __init__(self, paddlefish):
        self.paddlefish = paddlefish
        self.animation_speed = CHASE_ANIMATION_SPEED
        self.chase_speed = CHASE_SPEED

    def enter(self, e):
        self.paddlefish.frame = 0
        print(f"[DEBUG] Paddlefish CHASE 상태 진입")

    def exit(self, e):
        pass

    def do(self, delta_time):
        self.paddlefish.frame = (self.paddlefish.frame + self.animation_speed * delta_time) % RUN_FRAMES

        # 추적 시간 감소
        self.paddlefish.chase_time -= delta_time
        if self.paddlefish.chase_time <= 0:
            # 추적 종료
            self.paddlefish.is_chasing = False
            self.paddlefish.state_machine.cur_state = self.paddlefish.IDLE
            self.paddlefish.IDLE.enter(('CHASE_TIMEOUT', 0))
            print(f"[DEBUG] Paddlefish 추적 시간 초과, IDLE로 전환")
            return

        # 캐릭터가 있는지 체크
        if not self.paddlefish.check_character_in_range():
            # 캐릭터가 없으면 IDLE로 전환
            self.paddlefish.state_machine.cur_state = self.paddlefish.IDLE
            self.paddlefish.IDLE.enter(('LOSE_CHARACTER', 0))
            return

        # 쿨다운 중에는 IDLE로 전환 (쿨다운 대기)
        if self.paddlefish.attack_cooldown > 0:
            self.paddlefish.state_machine.cur_state = self.paddlefish.IDLE
            self.paddlefish.IDLE.enter(('COOLDOWN_WAIT', 0))
            return

        # 캐릭터까지의 거리 계산
        distance = self.paddlefish.get_distance_to_character()

        if distance < ATTACK_DETECTION_RANGE:  # 공격 범위 도달
            # 쿨다운이 끝났으므로 공격
            self.paddlefish.state_machine.cur_state = self.paddlefish.ATTACK
            self.paddlefish.ATTACK.enter(('REACH_CHARACTER', 0))
            return

        if distance >= DETECTION_RANGE:  # 추적 범위를 벗어남
            self.paddlefish.state_machine.cur_state = self.paddlefish.IDLE
            self.paddlefish.IDLE.enter(('LOSE_CHARACTER', 0))
            return

        # 캐릭터를 향해 이동
        target_x, target_y = self.paddlefish.get_character_position()
        dx = target_x - self.paddlefish.x
        dy = target_y - self.paddlefish.y

        # 방향 정규화
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            dx /= distance
            dy /= distance

            # 이동
            self.paddlefish.x += dx * self.chase_speed * delta_time
            self.paddlefish.y += dy * self.chase_speed * delta_time

            # 좌우 방향 설정
            if dx > 0:
                self.paddlefish.face_dir = 1
            elif dx < 0:
                self.paddlefish.face_dir = -1

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.paddlefish.x, self.paddlefish.y)
        else:
            screen_x, screen_y = self.paddlefish.x, self.paddlefish.y

        if self.paddlefish.face_dir == 1:
            self.paddlefish.imageR.clip_draw(int(self.paddlefish.frame) * PIXEL_WIDTH, 0, PIXEL_WIDTH, PIXEL_HEIGHT, screen_x, screen_y)
        else:
            self.paddlefish.imageR.clip_composite_draw(int(self.paddlefish.frame) * PIXEL_WIDTH, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 0, 'h', screen_x, screen_y, PIXEL_WIDTH, PIXEL_HEIGHT)

#----------------------------------------------------------------
class Paddlefish:
    """순찰 및 공격 몬스터 - IDLE, ATTACK, RUN, CHASE 상태를 가짐"""
    def __init__(self, x=400, y=300, target_character=None):
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
        self.attack_power = ATTACK_POWER

        # 생존 상태
        self.is_alive = True

        # 추적 상태
        self.is_chasing = False  # 피격 후 추적 모드인지 여부
        self.chase_time = 0  # 남은 추적 시간

        # 공격 쿨다운
        self.attack_cooldown = 0  # 0이면 공격 가능

        # 이미지 로드
        self.imageI = load_image('resource/PaddleFish_Idle.png')
        self.imageR = load_image('resource/PaddleFish_Run.png')
        self.imageA = load_image('resource/PaddleFish_Attack.png')

        # 상태 초기화
        self.IDLE = PaddlefishIdle(self)
        self.ATTACK = PaddlefishAttack(self)
        self.RUN = PaddlefishRun(self)
        self.CHASE = PaddlefishChase(self)

        # 상태 머신 초기화
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {},     # 배회 또는 추적 상태로 전환
                self.ATTACK: {},   # 공격 후 IDLE로 전환
                self.RUN: {},      # 배회 중 추적 모드 전환 가능
                self.CHASE: {}     # 추적 중 공격 또는 IDLE로 전환
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
        half_width = COLLISION_HALF_WIDTH
        half_height = COLLISION_HALF_HEIGHT
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height

    def get_attack_bb(self):
        """공격 충돌 박스 반환 (공격 중일 때만)"""
        # 공격 상태가 아니면 None 반환
        if self.state_machine.cur_state != self.ATTACK:
            return None

        # 공격 애니메이션의 특정 프레임에서만 공격 판정
        current_frame = int(self.frame)
        if not (ATTACK_HIT_FRAME_START <= current_frame <= ATTACK_HIT_FRAME_END):
            return None

        # 공격 판정 플래그 설정 (한 번만 데미지 처리하기 위함)
        attack_state = self.state_machine.cur_state
        if hasattr(attack_state, 'has_attacked'):
            if not attack_state.has_attacked:
                attack_state.has_attacked = True
                print(f"[DEBUG] Paddlefish 공격 판정 활성화! (프레임: {current_frame})")

        # 바라보는 방향에 따라 공격 박스 위치 설정
        if self.face_dir == 1:  # 오른쪽
            left = self.x
            right = self.x + ATTACK_RANGE
        else:  # 왼쪽
            left = self.x - ATTACK_RANGE
            right = self.x

        bottom = self.y - ATTACK_HEIGHT // 2
        top = self.y + ATTACK_HEIGHT // 2

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
        print(f"Paddlefish가 {damage} 데미지를 받음! (남은 HP: {self.hp}/{self.max_hp})")

        # 피격 시 추적 모드 활성화
        if not self.is_chasing:
            self.is_chasing = True
            self.chase_time = CHASE_DURATION
            print(f"[DEBUG] Paddlefish 피격! {CHASE_DURATION}초 동안 추적 모드 활성화")
        else:
            # 이미 추적 중이면 추적 시간 리셋
            self.chase_time = CHASE_DURATION
            print(f"[DEBUG] Paddlefish 추적 시간 리셋: {CHASE_DURATION}초")

        # 넉백 효과 (공격자 위치 기반)
        if attacker_x is not None:
            knockback_distance = 20
            if self.x > attacker_x:
                self.x += knockback_distance
                print(f"[DEBUG] Paddlefish 넉백: 오른쪽으로 {knockback_distance}px")
            else:
                self.x -= knockback_distance
                print(f"[DEBUG] Paddlefish 넉백: 왼쪽으로 {knockback_distance}px")

        if self.hp <= 0:
            print("Paddlefish 사망!")
            self.is_alive = False

#----------------------------------------------------------------
