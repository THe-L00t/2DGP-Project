from pico2d import *
from state_machine import StateMachine
import random

#----------------------------------------------------------------
# Monster1 - 기본 순찰형 몬스터
#----------------------------------------------------------------

class M1Idle:
    """Monster1의 대기 상태"""
    def __init__(self, monster):
        self.monster = monster
        self.animation_speed = 6  # 초당 프레임 수
        self.idle_time = 0
        self.max_idle_time = 2.0  # 2초 대기 후 순찰

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

        # 대기 시간 체크 - 일정 시간 후 자동으로 순찰 시작
        self.idle_time += delta_time
        if self.idle_time >= self.max_idle_time:
            self.monster.state_machine.cur_state = self.monster.PATROL
            self.monster.PATROL.enter(('AUTO_PATROL', 0))

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
class M1Patrol:
    """Monster1의 순찰 상태"""
    def __init__(self, monster):
        self.monster = monster
        self.animation_speed = 8  # 초당 프레임 수
        self.move_speed = 150  # 초당 픽셀 수 (Warrior보다 느림)
        self.patrol_time = 0
        self.max_patrol_time = 3.0  # 3초 순찰 후 대기

    def enter(self, e):
        self.monster.frame = 0
        self.patrol_time = 0
        # 랜덤한 방향 선택
        directions = [-1, 1]
        self.monster.dirx = random.choice(directions)
        self.monster.face_dir = self.monster.dirx

    def exit(self, e):
        pass

    def do(self, delta_time):
        # ============================================================
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        # 현재는 6프레임으로 가정했습니다
        # ============================================================
        self.monster.frame = (self.monster.frame + self.animation_speed * delta_time) % 6

        # 순찰 이동
        self.monster.x += self.monster.dirx * self.move_speed * delta_time

        # 순찰 시간 체크
        self.patrol_time += delta_time
        if self.patrol_time >= self.max_patrol_time:
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
            self.monster.imageP.clip_draw(int(self.monster.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.monster.imageP.clip_composite_draw(int(self.monster.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)

#----------------------------------------------------------------
class Monster1:
    """기본 순찰형 몬스터 - 좌우로 랜덤 순찰"""
    def __init__(self, x=400, y=300):
        self.x, self.y = x, y
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = 1

        # ============================================================
        # ★★★ TODO: 이미지 파일 경로를 실제 파일로 변경하세요 ★★★
        # ============================================================
        self.imageI = load_image('resource/Monster1_Idle.png')      # ← 대기 애니메이션
        self.imageP = load_image('resource/Monster1_Patrol.png')    # ← 순찰 애니메이션
        # ============================================================

        # 상태 초기화
        self.IDLE = M1Idle(self)
        self.PATROL = M1Patrol(self)

        # 상태 머신 초기화 (AI는 입력 이벤트 없이 자동 전환)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {},      # 자동으로 PATROL로 전환 (do() 내부에서)
                self.PATROL: {}     # 자동으로 IDLE로 전환 (do() 내부에서)
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
        half_width = 40
        half_height = 40
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height

#----------------------------------------------------------------
