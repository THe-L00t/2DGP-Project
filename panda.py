from pico2d import *
from state_machine import StateMachine
import random
import math

#----------------------------------------------------------------
# Panda - 원형 궤도 순찰 및 공격/방어 몬스터
#----------------------------------------------------------------

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
        self.panda.frame = (self.panda.frame + self.animation_speed * delta_time) % 6

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

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.panda.face_dir == 1:
            self.panda.imageI.clip_draw(int(self.panda.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.panda.imageI.clip_composite_draw(int(self.panda.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

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

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.panda.frame = (self.panda.frame + self.animation_speed * delta_time) % 6

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

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.panda.face_dir == 1:
            self.panda.imageA.clip_draw(int(self.panda.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.panda.imageA.clip_composite_draw(int(self.panda.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

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

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.panda.frame = (self.panda.frame + self.animation_speed * delta_time) % 4

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

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.panda.face_dir == 1:
            self.panda.imageG.clip_draw(int(self.panda.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.panda.imageG.clip_composite_draw(int(self.panda.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

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
        self.panda.frame = (self.panda.frame + self.animation_speed * delta_time) % 8

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

        # TODO: 프레임 크기를 실제 이미지에 맞게 수정하세요
        if self.panda.face_dir == 1:
            self.panda.imageR.clip_draw(int(self.panda.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.panda.imageR.clip_composite_draw(int(self.panda.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class Panda:
    """원형 궤도 순찰 및 공격/방어 몬스터 - IDLE, ATTACK, GUARD, RUN 상태를 가짐"""
    def __init__(self, x=500, y=400):
        self.x, self.y = x, y
        self.frame = 0
        self.face_dir = 1

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

    def draw(self, camera=None):
        self.state_machine.draw(camera)

    def handle_event(self, event):
        # AI 몬스터는 플레이어 입력을 받지 않음
        pass

    def get_bb(self):
        """충돌 박스"""
        # TODO: 히트박스 크기를 몬스터에 맞게 조정하세요
        half_width = 35
        half_height = 35
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height

#----------------------------------------------------------------
