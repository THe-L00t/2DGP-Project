from pico2d import *
from state_machine import StateMachine
import random
import math

#----------------------------------------------------------------
# Gnome - 무작위 이동 및 공격 몬스터 (캐릭터 추적 AI)
#----------------------------------------------------------------

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
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.gnome.frame = (self.gnome.frame + self.animation_speed * delta_time) % 8

        # 캐릭터 감지 및 상태 전환
        if self.gnome.check_character_in_range():
            distance = self.gnome.get_distance_to_character()
            # ============================================================
            # TODO: 공격 범위를 조정하세요 (현재: 100픽셀)
            # ============================================================
            if distance < 100:  # 공격 범위
                self.gnome.state_machine.cur_state = self.gnome.ATTACK
                self.gnome.ATTACK.enter(('DETECT_CHARACTER', 0))
                return
            # ============================================================
            # TODO: 추적 범위를 조정하세요 (현재: 300픽셀)
            # ============================================================
            elif distance < 300:  # 추적 범위
                self.gnome.state_machine.cur_state = self.gnome.CHASE
                self.gnome.CHASE.enter(('DETECT_CHARACTER', 0))
                return

        # 대기 시간 체크
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
        self.animation_speed = 10  # 초당 프레임 수
        self.attack_time = 0
        self.max_attack_time = 1.5  # 1.5초 공격 후 다른 상태로 전환

    def enter(self, e):
        self.gnome.frame = 0
        self.attack_time = 0
        self.gnome.dirx = 0
        self.gnome.diry = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        # TODO: 애니메이션 프레임 수를 실제 이미지에 맞게 수정하세요
        self.gnome.frame = (self.gnome.frame + self.animation_speed * delta_time) % 6

        # 캐릭터가 공격 범위를 벗어났는지 체크
        if self.gnome.check_character_in_range():
            distance = self.gnome.get_distance_to_character()
            # ============================================================
            # TODO: 공격 범위를 조정하세요 (현재: 100픽셀)
            # ============================================================
            if distance >= 100:  # 공격 범위를 벗어남
                # 추적 범위 내라면 추적, 아니면 IDLE
                # ============================================================
                # TODO: 추적 범위를 조정하세요 (현재: 300픽셀)
                # ============================================================
                if distance < 300:
                    self.gnome.state_machine.cur_state = self.gnome.CHASE
                    self.gnome.CHASE.enter(('TRACK_CHARACTER', 0))
                else:
                    self.gnome.state_machine.cur_state = self.gnome.IDLE
                    self.gnome.IDLE.enter(('LOSE_CHARACTER', 0))
                return

        # 공격 시간 체크
        self.attack_time += delta_time
        if self.attack_time >= self.max_attack_time:
            # 공격 후 IDLE로 전환
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
            # ============================================================
            # TODO: 공격 범위를 조정하세요 (현재: 100픽셀)
            # ============================================================
            if distance < 100:  # 공격 범위
                self.gnome.state_machine.cur_state = self.gnome.ATTACK
                self.gnome.ATTACK.enter(('DETECT_CHARACTER', 0))
                return
            # ============================================================
            # TODO: 추적 범위를 조정하세요 (현재: 300픽셀)
            # ============================================================
            elif distance < 300:  # 추적 범위
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

        # 캐릭터까지의 거리 계산
        distance = self.gnome.get_distance_to_character()

        # ============================================================
        # TODO: 공격 범위를 조정하세요 (현재: 100픽셀)
        # ============================================================
        if distance < 100:  # 공격 범위 도달
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

#----------------------------------------------------------------
