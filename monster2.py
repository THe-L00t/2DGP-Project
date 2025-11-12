from pico2d import *
from state_machine import StateMachine
import random
import math

#----------------------------------------------------------------
# Monster2 - 원형 궤도 순찰 몬스터
#----------------------------------------------------------------

class M2Idle:
    """Monster2의 대기 상태"""
    def __init__(self, monster):
        self.monster = monster
        self.animation_speed = 5  # 초당 프레임 수
        self.idle_time = 0
        self.max_idle_time = 1.5  # 1.5초 대기 후 순찰

    def enter(self, e):
        self.monster.frame = 0
        self.idle_time = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        # ============================================================
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        # 현재는 6프레임으로 가정했습니다
        # ============================================================
        self.monster.frame = (self.monster.frame + self.animation_speed * delta_time) % 6

        # 대기 시간 체크
        self.idle_time += delta_time
        if self.idle_time >= self.max_idle_time:
            self.monster.state_machine.cur_state = self.monster.CIRCLE
            self.monster.CIRCLE.enter(('AUTO_CIRCLE', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.monster.x, self.monster.y)
        else:
            screen_x, screen_y = self.monster.x, self.monster.y

        # ============================================================
        # TODO: 192를 실제 프레임 크기에 맞게 수정하세요
        # ============================================================
        if self.monster.face_dir == 1:
            self.monster.imageI.clip_draw(int(self.monster.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.monster.imageI.clip_composite_draw(int(self.monster.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class M2Circle:
    """Monster2의 원형 궤도 순찰 상태"""
    def __init__(self, monster):
        self.monster = monster
        self.animation_speed = 10  # 초당 프레임 수
        self.rotation_speed = 2.0  # 회전 속도 (라디안/초)
        self.circle_radius = 100  # 원형 궤도 반지름
        self.angle = 0  # 현재 각도
        self.circle_time = 0
        self.max_circle_time = 5.0  # 5초 원형 순찰 후 대기

    def enter(self, e):
        self.monster.frame = 0
        self.circle_time = 0
        self.angle = 0
        # 시작 위치를 중심점으로 저장
        self.center_x = self.monster.x
        self.center_y = self.monster.y

    def exit(self, e):
        pass

    def do(self, delta_time):
        # ============================================================
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        # 현재는 8프레임으로 가정했습니다
        # ============================================================
        self.monster.frame = (self.monster.frame + self.animation_speed * delta_time) % 8

        # 원형 궤도 이동
        self.angle += self.rotation_speed * delta_time
        self.monster.x = self.center_x + math.cos(self.angle) * self.circle_radius
        self.monster.y = self.center_y + math.sin(self.angle) * self.circle_radius

        # 이동 방향에 따라 캐릭터 방향 전환
        if math.cos(self.angle) > 0:
            self.monster.face_dir = 1
        else:
            self.monster.face_dir = -1

        # 순찰 시간 체크
        self.circle_time += delta_time
        if self.circle_time >= self.max_circle_time:
            self.monster.state_machine.cur_state = self.monster.IDLE
            self.monster.IDLE.enter(('AUTO_IDLE', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.monster.x, self.monster.y)
        else:
            screen_x, screen_y = self.monster.x, self.monster.y

        # ============================================================
        # TODO: 192를 실제 프레임 크기에 맞게 수정하세요
        # ============================================================
        if self.monster.face_dir == 1:
            self.monster.imageC.clip_draw(int(self.monster.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.monster.imageC.clip_composite_draw(int(self.monster.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class Monster2:
    """원형 궤도 순찰 몬스터 - 중심점을 기준으로 원형 궤도로 이동"""
    def __init__(self, x=500, y=400):
        self.x, self.y = x, y
        self.frame = 0
        self.face_dir = 1

        # ============================================================
        # ★★★ TODO: 이미지 파일 경로를 실제 파일로 변경하세요 ★★★
        # ============================================================
        self.imageI = load_image('resource/Monster2_Idle.png')      # ← 대기 애니메이션
        self.imageC = load_image('resource/Monster2_Circle.png')    # ← 원형 순찰 애니메이션
        # ============================================================

        # 상태 초기화
        self.IDLE = M2Idle(self)
        self.CIRCLE = M2Circle(self)

        # 상태 머신 초기화
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {},      # 자동으로 CIRCLE로 전환
                self.CIRCLE: {}     # 자동으로 IDLE로 전환
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
        # ============================================================
        # TODO: 히트박스 크기를 몬스터에 맞게 조정하세요
        # ============================================================
        half_width = 35
        half_height = 35
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height

#----------------------------------------------------------------
