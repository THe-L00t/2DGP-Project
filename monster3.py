from pico2d import *
from state_machine import StateMachine
import random

#----------------------------------------------------------------
# Monster3 - 상하좌우 무작위 이동 몬스터
#----------------------------------------------------------------

class M3Idle:
    """Monster3의 대기 상태"""
    def __init__(self, monster):
        self.monster = monster
        self.animation_speed = 7  # 초당 프레임 수
        self.idle_time = 0
        self.max_idle_time = 1.0  # 1초 대기 후 이동

    def enter(self, e):
        self.monster.frame = 0
        self.monster.dirx = 0
        self.monster.diry = 0
        self.idle_time = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        # ============================================================
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        # 현재는 8프레임으로 가정했습니다
        # ============================================================
        self.monster.frame = (self.monster.frame + self.animation_speed * delta_time) % 8

        # 대기 시간 체크
        self.idle_time += delta_time
        if self.idle_time >= self.max_idle_time:
            self.monster.state_machine.cur_state = self.monster.WANDER
            self.monster.WANDER.enter(('AUTO_WANDER', 0))

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
class M3Wander:
    """Monster3의 무작위 배회 상태"""
    def __init__(self, monster):
        self.monster = monster
        self.animation_speed = 9  # 초당 프레임 수
        self.move_speed = 200  # 초당 픽셀 수
        self.wander_time = 0
        self.max_wander_time = 2.0  # 2초 이동 후 대기

    def enter(self, e):
        self.monster.frame = 0
        self.wander_time = 0

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
        self.monster.dirx = chosen_dir[0]
        self.monster.diry = chosen_dir[1]

        # 좌우 방향만 face_dir에 반영
        if self.monster.dirx != 0:
            self.monster.face_dir = self.monster.dirx

    def exit(self, e):
        pass

    def do(self, delta_time):
        # ============================================================
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        # 현재는 6프레임으로 가정했습니다
        # ============================================================
        self.monster.frame = (self.monster.frame + self.animation_speed * delta_time) % 6

        # 대각선 이동 시 속도 보정 (√2로 나눔)
        if self.monster.dirx != 0 and self.monster.diry != 0:
            normalized_speed = self.move_speed / 1.414
        else:
            normalized_speed = self.move_speed

        # 무작위 방향으로 이동
        self.monster.x += self.monster.dirx * normalized_speed * delta_time
        self.monster.y += self.monster.diry * normalized_speed * delta_time

        # 이동 시간 체크
        self.wander_time += delta_time
        if self.wander_time >= self.max_wander_time:
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
            self.monster.imageW.clip_draw(int(self.monster.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.monster.imageW.clip_composite_draw(int(self.monster.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class Monster3:
    """무작위 배회 몬스터 - 상하좌우 8방향 무작위 이동"""
    def __init__(self, x=600, y=350):
        self.x, self.y = x, y
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = 1

        # ============================================================
        # ★★★ TODO: 이미지 파일 경로를 실제 파일로 변경하세요 ★★★
        # ============================================================
        self.imageI = load_image('resource/Monster3_Idle.png')      # ← 대기 애니메이션
        self.imageW = load_image('resource/Monster3_Wander.png')    # ← 배회 애니메이션
        # ============================================================

        # 상태 초기화
        self.IDLE = M3Idle(self)
        self.WANDER = M3Wander(self)

        # 상태 머신 초기화
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {},      # 자동으로 WANDER로 전환
                self.WANDER: {}     # 자동으로 IDLE로 전환
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
        half_width = 45
        half_height = 45
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height

#----------------------------------------------------------------
