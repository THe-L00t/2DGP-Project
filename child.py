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
COLLISION_HALF_WIDTH = 40
COLLISION_HALF_HEIGHT = 40

# 이동 속도
MOVE_SPEED = 250  # 픽셀/초 (Warrior보다 약간 느림)

# 체력 (Child는 비전투 캐릭터)
MAX_HP = 100
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

        self.imageI = load_image('resource/Child_Idle.png')
        self.imageR = load_image('resource/Child_Run.png')

        self.IDLE = CIdle(self)
        self.RUN = CRun(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.RUN, left_down: self.RUN, up_down: self.RUN, down_down: self.RUN},
                self.RUN: {right_up: self.RUN, left_up: self.RUN, right_down: self.RUN, left_down: self.RUN,
                           up_up: self.RUN, down_up: self.RUN, up_down: self.RUN, down_down: self.RUN}
            })
    def update(self, delta_time):
        self.state_machine.update(delta_time)
        pass

    def draw(self, camera=None):
        self.state_machine.draw(camera)
        pass

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
        print(f"Child가 {damage} 데미지를 받음! (남은 HP: {self.hp}/{self.max_hp})")

        # 넉백 효과 (공격자 위치 기반)
        if attacker_x is not None:
            knockback_distance = 20  # 밀려나는 거리
            if self.x > attacker_x:  # 공격자가 왼쪽에 있으면 오른쪽으로 밀림
                self.x += knockback_distance
                print(f"[DEBUG] Child 넉백: 오른쪽으로 {knockback_distance}px")
            else:  # 공격자가 오른쪽에 있으면 왼쪽으로 밀림
                self.x -= knockback_distance
                print(f"[DEBUG] Child 넉백: 왼쪽으로 {knockback_distance}px")

        if self.hp <= 0:
            print("Child 사망!")
            self.is_alive = False
#----------------------------------------------------------------