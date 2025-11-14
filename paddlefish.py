from pico2d import *
from state_machine import StateMachine
import random

#----------------------------------------------------------------
# Paddlefish - 순찰 및 공격 몬스터
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
COLLISION_HALF_WIDTH = 40
COLLISION_HALF_HEIGHT = 40

# 공격 박스 크기
ATTACK_RANGE = 65
ATTACK_HEIGHT = 35

# 이동 속도
MOVE_SPEED = 150

# 체력
MAX_HP = 80
# ============================================================

class PaddlefishIdle:
    """Paddlefish의 대기 상태"""
    def __init__(self, paddlefish):
        self.paddlefish = paddlefish
        self.animation_speed = 6  # 초당 프레임 수
        self.idle_time = 0
        self.max_idle_time = 2.0  # 2초 대기 후 다른 상태로 전환

    def enter(self, e):
        self.paddlefish.frame = 0
        self.paddlefish.dirx = 0
        self.paddlefish.diry = 0
        self.idle_time = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.paddlefish.frame = (self.paddlefish.frame + self.animation_speed * delta_time) % 8

        # 대기 시간 체크
        self.idle_time += delta_time
        if self.idle_time >= self.max_idle_time:
            # 무작위로 RUN 또는 ATTACK 상태로 전환
            next_state = random.choice([self.paddlefish.RUN, self.paddlefish.ATTACK])
            self.paddlefish.state_machine.cur_state = next_state
            next_state.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.paddlefish.x, self.paddlefish.y)
        else:
            screen_x, screen_y = self.paddlefish.x, self.paddlefish.y

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.paddlefish.face_dir == 1:
            self.paddlefish.imageI.clip_draw(int(self.paddlefish.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.paddlefish.imageI.clip_composite_draw(int(self.paddlefish.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class PaddlefishAttack:
    """Paddlefish의 공격 상태"""
    def __init__(self, paddlefish):
        self.paddlefish = paddlefish
        self.animation_speed = 10  # 초당 프레임 수
        self.attack_time = 0
        self.max_attack_time = 1.5  # 1.5초 공격 후 다른 상태로 전환

    def enter(self, e):
        self.paddlefish.frame = 0
        self.attack_time = 0
        self.paddlefish.dirx = 0
        self.paddlefish.diry = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.paddlefish.frame = (self.paddlefish.frame + self.animation_speed * delta_time) % 6

        # 공격 시간 체크
        self.attack_time += delta_time
        if self.attack_time >= self.max_attack_time:
            # 공격 후 IDLE 또는 RUN 상태로 전환
            next_state = random.choice([self.paddlefish.IDLE, self.paddlefish.RUN])
            self.paddlefish.state_machine.cur_state = next_state
            next_state.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.paddlefish.x, self.paddlefish.y)
        else:
            screen_x, screen_y = self.paddlefish.x, self.paddlefish.y

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.paddlefish.face_dir == 1:
            self.paddlefish.imageA.clip_draw(int(self.paddlefish.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.paddlefish.imageA.clip_composite_draw(int(self.paddlefish.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class PaddlefishRun:
    """Paddlefish의 이동 상태"""
    def __init__(self, paddlefish):
        self.paddlefish = paddlefish
        self.animation_speed = 8  # 초당 프레임 수
        self.move_speed = 150  # 초당 픽셀 수
        self.run_time = 0
        self.max_run_time = 3.0  # 3초 이동 후 다른 상태로 전환

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
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.paddlefish.frame = (self.paddlefish.frame + self.animation_speed * delta_time) % 6

        # 좌우 이동
        self.paddlefish.x += self.paddlefish.dirx * self.move_speed * delta_time

        # 이동 시간 체크
        self.run_time += delta_time
        if self.run_time >= self.max_run_time:
            # 이동 후 IDLE 또는 ATTACK 상태로 전환
            next_state = random.choice([self.paddlefish.IDLE, self.paddlefish.ATTACK])
            self.paddlefish.state_machine.cur_state = next_state
            next_state.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.paddlefish.x, self.paddlefish.y)
        else:
            screen_x, screen_y = self.paddlefish.x, self.paddlefish.y

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.paddlefish.face_dir == 1:
            self.paddlefish.imageR.clip_draw(int(self.paddlefish.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.paddlefish.imageR.clip_composite_draw(int(self.paddlefish.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class Paddlefish:
    """순찰 및 공격 몬스터 - IDLE, ATTACK, RUN 상태를 가짐"""
    def __init__(self, x=400, y=300):
        self.x, self.y = x, y
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = 1

        # 체력
        self.hp = MAX_HP
        self.max_hp = MAX_HP

        # 공격력
        self.attack_power = 12  # Paddlefish의 공격력

        # 생존 상태
        self.is_alive = True

        # TODO: 이미지 파일 경로를 실제 파일로 변경하세요
        self.imageI = load_image('resource/PaddleFish_Idle.png')    # 대기 애니메이션
        self.imageR = load_image('resource/PaddleFish_Run.png')     # 달리기 애니메이션
        self.imageA = load_image('resource/PaddleFish_Attack.png')  # 공격 애니메이션

        # 상태 초기화
        self.IDLE = PaddlefishIdle(self)
        self.ATTACK = PaddlefishAttack(self)
        self.RUN = PaddlefishRun(self)

        # 상태 머신 초기화
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {},     # 자동으로 RUN 또는 ATTACK으로 전환
                self.ATTACK: {},   # 자동으로 IDLE 또는 RUN으로 전환
                self.RUN: {}       # 자동으로 IDLE 또는 ATTACK으로 전환
            }
        )

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
        half_width = 40
        half_height = 40
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height

    def get_attack_bb(self):
        """공격 충돌 박스 반환 (공격 중일 때만)"""
        # 공격 상태가 아니면 None 반환
        if self.state_machine.cur_state != self.ATTACK:
            return None

        # TODO: 공격 범위를 조정하세요
        attack_range = 65  # 공격 범위
        attack_height = 35 # 공격 박스 높이

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

    def take_damage(self, damage):
        """데미지를 받음"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"Paddlefish가 {damage} 데미지를 받음! (남은 HP: {self.hp}/{self.max_hp})")

        if self.hp <= 0:
            print("Paddlefish 사망!")
            self.is_alive = False

#----------------------------------------------------------------
