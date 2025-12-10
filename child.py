from pico2d import *
from event_check import *
from state_machine import StateMachine

#----------------------------------------------------------------
# 전역 설정 - 여기서 일괄 수정
#----------------------------------------------------------------
# 스프라이트 크기
PIXEL_WIDTH = 192
PIXEL_HEIGHT = 192

# 충돌 박스 크기
COLLISION_HALF_WIDTH = 30
COLLISION_HALF_HEIGHT = 30

# 이동 속도
MOVE_SPEED = 250  # 픽셀/초 (Warrior보다 약간 느림)

# 체력 (Child는 비전투 캐릭터)
MAX_HP = 100

# Power 재생 속도
POWER_REGEN_RATE = 7  # 초당 7씩 회복
#----------------------------------------------------------------

class CIdle:
    def __init__(self, child):
        self.child = child
        self.animation_speed = 8  # 초당 프레임 수

    def enter(self, e):
        self.child.frame = 0
        self.child.dirx = 0
        self.child.diry = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        self.child.frame = (self.child.frame + self.animation_speed * delta_time) % 6

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.child.x, self.child.y)
        else:
            screen_x, screen_y = self.child.x, self.child.y

        if self.child.face_dir == 1:
            self.child.imageI.clip_draw(int(self.child.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.child.imageI.clip_composite_draw(int(self.child.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)
#----------------------------------------------------------------
class CRun:
    def __init__(self, child):
        self.child = child
        self.animation_speed = 8  # 초당 프레임 수
        self.move_speed = MOVE_SPEED  # 전역 설정에서 가져옴

    def enter(self, e):
        if left_down(e):
            self.child.keys['left'] = True
        elif left_up(e):
            self.child.keys['left'] = False
        elif right_down(e):
            self.child.keys['right'] = True
        elif right_up(e):
            self.child.keys['right'] = False
        elif up_down(e):
            self.child.keys['up'] = True
        elif up_up(e):
            self.child.keys['up'] = False
        elif down_down(e):
            self.child.keys['down'] = True
        elif down_up(e):
            self.child.keys['down'] = False

    def exit(self, e):
        pass

    def do(self, delta_time):
        self.child.frame = (self.child.frame + self.animation_speed * delta_time) % 4

        self.child.dirx = 0
        self.child.diry = 0

        if self.child.keys['right']:
            self.child.dirx += 1
        if self.child.keys['left']:
            self.child.dirx -= 1
        if self.child.keys['up']:
            self.child.diry += 1
        if self.child.keys['down']:
            self.child.diry -= 1

        if self.child.dirx > 0:
            self.child.face_dir = 1
        elif self.child.dirx < 0:
            self.child.face_dir = -1

        self.child.x += self.child.dirx * self.move_speed * delta_time
        self.child.y += self.child.diry * self.move_speed * delta_time

        if not any(self.child.keys.values()):
            self.child.state_machine.cur_state = self.child.IDLE
            self.child.IDLE.enter(('STOP', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.child.x, self.child.y)
        else:
            screen_x, screen_y = self.child.x, self.child.y

        if self.child.face_dir == 1:
            self.child.imageR.clip_draw(int(self.child.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.child.imageR.clip_composite_draw(int(self.child.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)
#----------------------------------------------------------------
class CInteraction:
    """Child의 Interaction 상태 - Warrior 힐"""
    def __init__(self, child):
        self.child = child
        self.animation_speed = 11  # 11프레임을 1초에 재생
        self.interaction_time = 0
        self.max_interaction_time = 1.0  # 1초 동안 재생
        self.has_healed = False  # 힐을 한 번만 적용하기 위한 플래그

    def enter(self, e):
        self.child.frame = 0
        self.interaction_time = 0
        self.has_healed = False
        self.child.dirx = 0
        self.child.diry = 0
        # 힐 사운드 재생
        self.child.heal_sound.play()
        print(f"[DEBUG] Child Interaction 시작!")

    def exit(self, e):
        pass

    def do(self, delta_time):
        # 애니메이션 프레임 업데이트
        self.child.frame = (self.child.frame + self.animation_speed * delta_time)

        # 애니메이션이 끝까지 재생되도록 보장
        if self.child.frame >= 11:
            self.child.frame = 10.99  # 마지막 프레임에 고정

        # 애니메이션 중간(약 절반)에 힐 적용
        if self.child.frame >= 5.5 and not self.has_healed:
            self.has_healed = True
            # Child power 40% 소모
            power_cost = self.child.max_hp * 0.4
            self.child.hp -= power_cost
            if self.child.hp < 0:
                self.child.hp = 0
            print(f"[INTERACTION] Child Power 40% 소모! (남은 Power: {self.child.hp}/{self.child.max_hp})")

            # Warrior HP 20% 회복
            if self.child.warrior:
                heal_amount = self.child.warrior.max_hp * 0.2
                self.child.warrior.hp += heal_amount
                if self.child.warrior.hp > self.child.warrior.max_hp:
                    self.child.warrior.hp = self.child.warrior.max_hp
                print(f"[INTERACTION] Warrior HP 20% 회복! ({heal_amount:.1f} HP 회복, 현재 HP: {self.child.warrior.hp}/{self.child.warrior.max_hp})")

        # 시간 증가
        self.interaction_time += delta_time
        if self.interaction_time >= self.max_interaction_time:
            # 애니메이션 종료, IDLE로 전환
            print(f"[DEBUG] Child Interaction 종료")
            self.child.state_machine.cur_state = self.child.IDLE
            self.child.IDLE.enter(('AUTO_TRANSITION', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.child.x, self.child.y)
        else:
            screen_x, screen_y = self.child.x, self.child.y

        if self.child.face_dir == 1:
            self.child.imageInteraction.clip_draw(int(self.child.frame) * 192, 0, 192, 192, screen_x, screen_y)
        else:
            self.child.imageInteraction.clip_composite_draw(int(self.child.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)
#----------------------------------------------------------------
class Child:
    def __init__(self):
        self.x, self.y = 500, 300
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = 1
        self.keys = {'left': False, 'right': False, 'up': False, 'down': False}

        # 체력 (전역 설정에서 가져옴)
        self.hp = MAX_HP
        self.max_hp = MAX_HP

        # 생존 상태
        self.is_alive = True

        # Warrior 참조 (play_scene에서 설정)
        self.warrior = None

        # 자동 추적 설정
        self.follow_distance = 200  # 이 거리보다 멀어지면 따라옴
        self.follow_stop_distance = 100  # 이 거리 이하로 가까워지면 멈춤
        self.is_following = False  # 현재 따라가는 중인지

        self.imageI = load_image('resource/Child_Idle.png')
        self.imageR = load_image('resource/Child_Run.png')
        self.imageInteraction = load_image('resource/Child_Interaction.png')

        # 힐 사운드 로드
        self.heal_sound = load_wav('resource/child.wav')
        self.heal_sound.set_volume(64)  # 볼륨 설정 (0~128)

        self.IDLE = CIdle(self)
        self.RUN = CRun(self)
        self.INTERACTION = CInteraction(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.RUN, left_down: self.RUN, up_down: self.RUN, down_down: self.RUN,
                            a_down: self.INTERACTION},
                self.RUN: {right_up: self.RUN, left_up: self.RUN, right_down: self.RUN, left_down: self.RUN,
                           up_up: self.RUN, down_up: self.RUN, up_down: self.RUN, down_down: self.RUN,
                           a_down: self.INTERACTION},
                self.INTERACTION: {}
            })
    def follow_target(self, target, delta_time):
        """타겟(warrior)을 따라가는 AI 로직"""
        if not target or self.state_machine.cur_state == self.INTERACTION:
            # Interaction 중이거나 타겟이 없으면 따라가지 않음
            self.is_following = False
            return

        # 타겟까지의 거리 계산
        import math
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # 거리에 따라 행동 결정
        if distance > self.follow_distance:
            # 너무 멀어지면 따라가기 시작
            self.is_following = True
        elif distance < self.follow_stop_distance:
            # 충분히 가까우면 멈춤
            self.is_following = False

        # 따라가는 중이면 타겟을 향해 이동
        if self.is_following and distance > self.follow_stop_distance:
            # 방향 벡터 정규화
            self.dirx = dx / distance
            self.diry = dy / distance

            # 얼굴 방향 설정
            if self.dirx > 0:
                self.face_dir = 1
            elif self.dirx < 0:
                self.face_dir = -1

            # 이동
            self.x += self.dirx * MOVE_SPEED * delta_time
            self.y += self.diry * MOVE_SPEED * delta_time

            # Run 애니메이션 프레임 업데이트
            self.frame = (self.frame + 8 * delta_time) % 4
        else:
            # 멈춰 있으면 Idle 애니메이션
            self.frame = (self.frame + 8 * delta_time) % 6
            self.dirx = 0
            self.diry = 0

    def update(self, delta_time):
        # 자동으로 따라가는 중이 아닐 때만 State Machine 업데이트
        if not self.is_following:
            self.state_machine.update(delta_time)

        # Power 자동 재생 (초당 7씩 회복)
        if self.hp < self.max_hp:
            self.hp += POWER_REGEN_RATE * delta_time
            if self.hp > self.max_hp:
                self.hp = self.max_hp

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.x, self.y)
        else:
            screen_x, screen_y = self.x, self.y

        # 자동으로 따라가는 중일 때
        if self.is_following:
            # Run 애니메이션 표시
            if self.face_dir == 1:
                self.imageR.clip_draw(int(self.frame) * 192, 0, 192, 192, screen_x, screen_y)
            else:
                self.imageR.clip_composite_draw(int(self.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)
        # AI 모드지만 멈춰있을 때 (거리가 가까워서 따라가지 않음)
        elif self.warrior and self.state_machine.cur_state == self.IDLE and not any(self.keys.values()):
            # Idle 애니메이션 표시
            if self.face_dir == 1:
                self.imageI.clip_draw(int(self.frame) * 192, 0, 192, 192, screen_x, screen_y)
            else:
                self.imageI.clip_composite_draw(int(self.frame) * 192, 0, 192, 192, 0, 'h', screen_x, screen_y, 192, 192)
        else:
            # State machine의 draw 호출 (수동 조작 중)
            self.state_machine.draw(camera)

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass

    def get_bb(self):
        # 히트박스 크기 (전역 설정에서 가져옴)
        return (self.x - COLLISION_HALF_WIDTH, self.y - COLLISION_HALF_HEIGHT,
                self.x + COLLISION_HALF_WIDTH, self.y + COLLISION_HALF_HEIGHT)

    def get_attack_bb(self):
        """공격 충돌 박스 반환 - Child는 공격이 없으므로 None 반환"""
        return None

    def get_current_attack_power(self):
        """Child는 공격력이 없음"""
        return 0

    def take_damage(self, damage, attacker_x=None):
        """데미지를 받음 (넉백 포함)"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"Child가 {damage} 데미지를 받음! (남은 Power: {self.hp}/{self.max_hp})")

        # 넉백 효과 (공격자 위치 기반)
        if attacker_x is not None:
            knockback_distance = 20  # 밀려나는 거리
            if self.x > attacker_x:  # 공격자가 왼쪽에 있으면 오른쪽으로 밀림
                self.x += knockback_distance
                print(f"[DEBUG] Child 넉백: 오른쪽으로 {knockback_distance}px")
            else:  # 공격자가 오른쪽에 있으면 왼쪽으로 밀림
                self.x -= knockback_distance
                print(f"[DEBUG] Child 넉백: 왼쪽으로 {knockback_distance}px")

        # Child는 죽지 않음 - Power가 0이 되면 play_scene에서 자동으로 Warrior로 전환됨
        if self.hp <= 0:
            print("Child Power 소진! (사라지지 않음, Warrior로 전환됨)")
#----------------------------------------------------------------