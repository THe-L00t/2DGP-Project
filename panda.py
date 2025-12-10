from pico2d import *
from state_machine import StateMachine
import random
import math

#----------------------------------------------------------------
# Panda - 원형 궤도 순찰 및 공격/방어 몬스터
#----------------------------------------------------------------

# ============================================================
# 전역 설정 - 여기서 일괄 수정
# ============================================================
PIXEL_WIDTH = 192   # 스프라이트 가로 픽셀 크기
PIXEL_HEIGHT = 192  # 스프라이트 세로 픽셀 크기

# 애니메이션 프레임 수
IDLE_FRAMES = 6
ATTACK_FRAMES = 6
GUARD_FRAMES = 4
RUN_FRAMES = 8

# 충돌 박스 크기
COLLISION_HALF_WIDTH = 35
COLLISION_HALF_HEIGHT = 35

# 공격 박스 크기
ATTACK_RANGE = 100
ATTACK_HEIGHT = 80

# 이동 속도
ROTATION_SPEED = 2.0
CIRCLE_RADIUS = 100

# 체력
MAX_HP = 1000
# ============================================================

class PandaIdle:
    """Panda의 대기 상태"""
    def __init__(self, panda):
        self.panda = panda
        self.animation_speed = 5  # 초당 프레임 수
        self.idle_time = 0
        self.max_idle_time = 1.5  # 1.5초 대기 후 다른 상태로 전환

    def enter(self, e):
        self.panda.frame = 0
        self.idle_time = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.panda.frame = (self.panda.frame + self.animation_speed * delta_time) % 10

        # 대기 시간 체크
        self.idle_time += delta_time
        if self.idle_time >= self.max_idle_time:
            # 무작위로 RUN, ATTACK, GUARD 상태로 전환
            next_state = random.choice([self.panda.RUN, self.panda.ATTACK, self.panda.GUARD])
            self.panda.state_machine.cur_state = next_state
            next_state.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.panda.x, self.panda.y)
        else:
            screen_x, screen_y = self.panda.x, self.panda.y

        # 피격 효과 적용
        self.panda.apply_hit_effect(self.panda.imageI)

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.panda.face_dir == 1:
            self.panda.imageI.clip_draw(int(self.panda.frame) * 256, 0, 256, 256, screen_x, screen_y, 400, 400 )
        else:
            self.panda.imageI.clip_composite_draw(int(self.panda.frame) * 256, 0, 256, 256, 0, 'h', screen_x, screen_y, 400, 400)

        # 투명도 원상복구
        self.panda.imageI.opacify(1.0)

#----------------------------------------------------------------
class PandaAttack:
    """Panda의 공격 상태"""
    def __init__(self, panda):
        self.panda = panda
        self.animation_speed = 10  # 초당 프레임 수
        self.attack_time = 0
        self.max_attack_time = 1.5  # 1.5초 공격 후 다른 상태로 전환

    def enter(self, e):
        self.panda.frame = 0
        self.attack_time = 0

        # 타겟 캐릭터를 향해 얼굴 방향 설정
        if self.panda.target_character:
            dx = self.panda.target_character.x - self.panda.x
            if dx > 0:
                self.panda.face_dir = 1  # 오른쪽
            elif dx < 0:
                self.panda.face_dir = -1  # 왼쪽
            print(f"[DEBUG] Panda ATTACK 상태 진입 (face_dir: {self.panda.face_dir})")

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.panda.frame = (self.panda.frame + self.animation_speed * delta_time) % 13

        # 공격 시간 체크
        self.attack_time += delta_time
        if self.attack_time >= self.max_attack_time:
            # 공격 후 IDLE, RUN, GUARD 상태로 전환
            next_state = random.choice([self.panda.IDLE, self.panda.RUN, self.panda.GUARD])
            self.panda.state_machine.cur_state = next_state
            next_state.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.panda.x, self.panda.y)
        else:
            screen_x, screen_y = self.panda.x, self.panda.y

        # 피격 효과 적용
        self.panda.apply_hit_effect(self.panda.imageA)

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.panda.face_dir == 1:
            self.panda.imageA.clip_draw(int(self.panda.frame) * 256, 0, 256, 256, screen_x, screen_y, 400,400)
        else:
            self.panda.imageA.clip_composite_draw(int(self.panda.frame) * 256, 0, 256, 256, 0, 'h', screen_x, screen_y, 400, 400)

        # 투명도 원상복구
        self.panda.imageA.opacify(1.0)

#----------------------------------------------------------------
class PandaGuard:
    """Panda의 방어 상태"""
    def __init__(self, panda):
        self.panda = panda
        self.animation_speed = 5  # 초당 프레임 수
        self.guard_time = 0
        self.max_guard_time = 2.0  # 2초 방어 후 다른 상태로 전환

    def enter(self, e):
        self.panda.frame = 0
        self.guard_time = 0

        # 타겟 캐릭터를 향해 얼굴 방향 설정
        if self.panda.target_character:
            dx = self.panda.target_character.x - self.panda.x
            if dx > 0:
                self.panda.face_dir = 1  # 오른쪽
            elif dx < 0:
                self.panda.face_dir = -1  # 왼쪽
            print(f"[DEBUG] Panda GUARD 상태 진입 (face_dir: {self.panda.face_dir})")

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.panda.frame = (self.panda.frame + self.animation_speed * delta_time) % 8

        # 방어 시간 체크
        self.guard_time += delta_time
        if self.guard_time >= self.max_guard_time:
            # 방어 후 IDLE, RUN, ATTACK 상태로 전환
            next_state = random.choice([self.panda.IDLE, self.panda.RUN, self.panda.ATTACK])
            self.panda.state_machine.cur_state = next_state
            next_state.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.panda.x, self.panda.y)
        else:
            screen_x, screen_y = self.panda.x, self.panda.y

        # 피격 효과 적용
        self.panda.apply_hit_effect(self.panda.imageG)

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.panda.face_dir == 1:
            self.panda.imageG.clip_draw(int(self.panda.frame) * 256, 0, 256, 256, screen_x, screen_y,400,400)
        else:
            self.panda.imageG.clip_composite_draw(int(self.panda.frame) * 256, 0, 256, 256, 0, 'h', screen_x, screen_y, 400, 400)

        # 투명도 원상복구
        self.panda.imageG.opacify(1.0)

#----------------------------------------------------------------
class PandaRun:
    """Panda의 이동 상태"""
    def __init__(self, panda):
        self.panda = panda
        self.animation_speed = 10  # 초당 프레임 수
        self.rotation_speed = 2.0  # 회전 속도 (라디안/초)
        self.circle_radius = 100  # 원형 궤도 반지름
        self.angle = 0  # 현재 각도
        self.run_time = 0
        self.max_run_time = 5.0  # 5초 원형 이동 후 다른 상태로 전환

    def enter(self, e):
        self.panda.frame = 0
        self.run_time = 0
        self.angle = 0
        # 시작 위치를 중심점으로 저장
        self.center_x = self.panda.x
        self.center_y = self.panda.y

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.panda.frame = (self.panda.frame + self.animation_speed * delta_time) % 6

        # 원형 궤도 이동
        self.angle += self.rotation_speed * delta_time
        self.panda.x = self.center_x + math.cos(self.angle) * self.circle_radius
        self.panda.y = self.center_y + math.sin(self.angle) * self.circle_radius

        # 이동 방향에 따라 캐릭터 방향 전환
        if math.cos(self.angle) > 0:
            self.panda.face_dir = 1
        else:
            self.panda.face_dir = -1

        # 이동 시간 체크
        self.run_time += delta_time
        if self.run_time >= self.max_run_time:
            # 이동 후 IDLE, ATTACK, GUARD 상태로 전환
            next_state = random.choice([self.panda.IDLE, self.panda.ATTACK, self.panda.GUARD])
            self.panda.state_machine.cur_state = next_state
            next_state.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.panda.x, self.panda.y)
        else:
            screen_x, screen_y = self.panda.x, self.panda.y

        # 피격 효과 적용
        self.panda.apply_hit_effect(self.panda.imageR)

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.panda.face_dir == 1:
            self.panda.imageR.clip_draw(int(self.panda.frame) * 256, 0, 256, 256, screen_x, screen_y, 400,400)
        else:
            self.panda.imageR.clip_composite_draw(int(self.panda.frame) * 256, 0, 256, 256, 0, 'h', screen_x, screen_y, 400, 400)

        # 투명도 원상복구
        self.panda.imageR.opacify(1.0)

#----------------------------------------------------------------
class Panda:
    """원형 궤도 순찰 및 공격/방어 몬스터 - IDLE, ATTACK, GUARD, RUN 상태를 가짐"""
    def __init__(self, x=500, y=400):
        self.x, self.y = x, y
        self.frame = 0
        self.face_dir = 1

        # 체력
        self.hp = MAX_HP
        self.max_hp = MAX_HP

        # 공격력
        self.attack_power = 20  # Panda의 공격력 (가장 강함)

        # 생존 상태
        self.is_alive = True

        # 피격 이펙트
        self.hit_effect_time = 0.0  # 피격 효과 남은 시간

        # 타겟 캐릭터 (play_scene에서 설정)
        self.target_character = None

        # TODO: 이미지 파일 경로를 실제 파일로 변경하세요
        self.imageI = load_image('resource/Panda_Idle.png')    # 대기 애니메이션
        self.imageR = load_image('resource/Panda_Run.png')     # 달리기 애니메이션
        self.imageA = load_image('resource/Panda_Attack.png')  # 공격 애니메이션
        self.imageG = load_image('resource/Panda_Guard.png')   # 방어 애니메이션

        # 상태 초기화
        self.IDLE = PandaIdle(self)
        self.ATTACK = PandaAttack(self)
        self.GUARD = PandaGuard(self)
        self.RUN = PandaRun(self)

        # 상태 머신 초기화
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {},     # 자동으로 RUN, ATTACK, GUARD로 전환
                self.ATTACK: {},   # 자동으로 IDLE, RUN, GUARD로 전환
                self.GUARD: {},    # 자동으로 IDLE, RUN, ATTACK으로 전환
                self.RUN: {}       # 자동으로 IDLE, ATTACK, GUARD로 전환
            }
        )

    def update(self, delta_time):
        self.state_machine.update(delta_time)

        # 피격 이펙트 시간 감소
        if self.hit_effect_time > 0:
            self.hit_effect_time -= delta_time

    def draw(self, camera=None):
        self.state_machine.draw(camera)

    def handle_event(self, event):
        # AI 몬스터는 플레이어 입력을 받지 않음
        pass

    def get_bb(self):
        """충돌 박스"""
        # TODO: 히트박스 크기를 몬스터에 맞게 조정하세요
        half_width = int(35*1.56)
        half_height = int(35*1.56)
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height

    def get_attack_bb(self):
        """공격 충돌 박스 반환 (공격 중일 때만)"""
        # 공격 상태가 아니면 None 반환
        if self.state_machine.cur_state != self.ATTACK:
            return None

        # TODO: 공격 범위를 조정하세요
        attack_range = 110*1.56  # 공격 범위
        attack_height = 90*1.56 # 공격 박스 높이

        # 바라보는 방향에 따라 공격 박스 위치 설정
        if self.face_dir == 1:  # 오른쪽
            left = int(self.x + 10*1.56)
            right = int(self.x + 10*1.56 + attack_range)
        else:  # 왼쪽
            left = int(self.x - 20*1.56 - attack_range)
            right = int(self.x - 20*1.56)

        bottom = int(self.y - 10*1.56 - (attack_height // 2))
        top = int(self.y - 10*1.56 + (attack_height // 2))

        return left, bottom, right, top

    def get_current_attack_power(self):
        """현재 공격력 반환 (공격 중일 때만)"""
        if self.state_machine.cur_state == self.ATTACK:
            return self.attack_power
        return 0

    def is_guarding(self):
        """현재 가드 중인지 확인"""
        return self.state_machine.cur_state == self.GUARD

    def take_damage(self, damage, attacker_x=None):
        """데미지를 받음 (넉백 포함)"""
        # 가드 중이면 데미지를 받지 않고 무시
        if self.is_guarding():
            print(f"Panda가 가드 중! 데미지 무효화!")
            return

        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"Panda가 {damage} 데미지를 받음! (남은 HP: {self.hp}/{self.max_hp})")

        # 피격 이펙트 활성화 (0.5초)
        self.hit_effect_time = 0.5

        # 넉백 효과 (공격자 위치 기반)
        if attacker_x is not None:
            knockback_distance = 20  # 밀려나는 거리
            if self.x > attacker_x:  # 공격자가 왼쪽에 있으면 오른쪽으로 밀림
                self.x += knockback_distance
                print(f"[DEBUG] Panda 넉백: 오른쪽으로 {knockback_distance}px")
            else:  # 공격자가 오른쪽에 있으면 왼쪽으로 밀림
                self.x -= knockback_distance
                print(f"[DEBUG] Panda 넉백: 왼쪽으로 {knockback_distance}px")

        if self.hp <= 0:
            print("Panda 사망!")
            self.is_alive = False

    def apply_hit_effect(self, image):
        """피격 이펙트를 이미지에 적용하는 헬퍼 함수"""
        if self.hit_effect_time > 0:
            # 0.1초 간격으로 깜빡임 (5번)
            blink_interval = 0.1
            cycle_position = self.hit_effect_time % blink_interval
            # 절반은 투명, 절반은 불투명
            if cycle_position > blink_interval / 2:
                image.opacify(0.5)
            # else: 기본 투명도 유지 (1.0)

    def set_target_character(self, character):
        """타겟 캐릭터 설정"""
        self.target_character = character

#----------------------------------------------------------------
