from pico2d import *
from event_check import *
from state_machine import StateMachine
#----------------------------------------------------------------
class WIdle:
    def __init__(self, warrior):
        self.warrior = warrior
        self.animation_speed = 8  # 초당 프레임 수

    def enter(self, e):
        self.warrior.frame = 0
        self.warrior.dirx = 0
        self.warrior.diry = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        import time
        self.warrior.frame = (self.warrior.frame + self.animation_speed * delta_time) % 8

        if self.warrior.attack1_end_time:
            elapsed = time.time() - self.warrior.attack1_end_time
            if elapsed > 0.5:
                self.warrior.can_combo = False
                self.warrior.attack1_end_time = None
                print("콤보 타임 종료")

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.warrior.x, self.warrior.y)
        else:
            screen_x, screen_y = self.warrior.x, self.warrior.y

        if self.warrior.face_dir == 1:
            self.warrior.imageI.clip_draw(int(self.warrior.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.warrior.imageI.clip_composite_draw(int(self.warrior.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)
#----------------------------------------------------------------
class WRun:
    def __init__(self, warrior):
        self.warrior = warrior
        self.animation_speed = 10  # 초당 프레임 수
        self.move_speed = 300  # 초당 픽셀 수

    def enter(self, e):
        if left_down(e):
            self.warrior.keys['left'] = True
        elif left_up(e):
            self.warrior.keys['left'] = False
        elif right_down(e):
            self.warrior.keys['right'] = True
        elif right_up(e):
            self.warrior.keys['right'] = False
        elif up_down(e):
            self.warrior.keys['up'] = True
        elif up_up(e):
            self.warrior.keys['up'] = False
        elif down_down(e):
            self.warrior.keys['down'] = True
        elif down_up(e):
            self.warrior.keys['down'] = False

    def exit(self, e):
        pass

    def do(self, delta_time):
        import time
        self.warrior.frame = (self.warrior.frame + self.animation_speed * delta_time) % 6

        if self.warrior.attack1_end_time:
            elapsed = time.time() - self.warrior.attack1_end_time
            if elapsed > 0.5:
                self.warrior.can_combo = False
                self.warrior.attack1_end_time = None
                print("콤보 타임 종료")

        self.warrior.dirx = 0
        self.warrior.diry = 0

        if self.warrior.keys['right']:
            self.warrior.dirx += 1
        if self.warrior.keys['left']:
            self.warrior.dirx -= 1
        if self.warrior.keys['up']:
            self.warrior.diry += 1
        if self.warrior.keys['down']:
            self.warrior.diry -= 1

        if self.warrior.dirx > 0:
            self.warrior.face_dir = 1
        elif self.warrior.dirx < 0:
            self.warrior.face_dir = -1

        self.warrior.x += self.warrior.dirx * self.move_speed * delta_time
        self.warrior.y += self.warrior.diry * self.move_speed * delta_time

        if not any(self.warrior.keys.values()):
            self.warrior.state_machine.cur_state = self.warrior.IDLE
            self.warrior.IDLE.enter(('STOP', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.warrior.x, self.warrior.y)
        else:
            screen_x, screen_y = self.warrior.x, self.warrior.y

        if self.warrior.face_dir == 1:
            self.warrior.imageR.clip_draw(int(self.warrior.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.warrior.imageR.clip_composite_draw(int(self.warrior.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)

#----------------------------------------------------------------
class WAttack1:
    def __init__(self, warrior):
        self.warrior = warrior
        self.animation_speed = 12  # 초당 프레임 수 (공격은 빠르게)

    def enter(self, e):
        self.warrior.frame = 0
        self.warrior.attack1_end_time = None
        self.warrior.can_combo = False
        self.warrior.dirx = 0
        self.warrior.diry = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        import time
        prev_frame = int(self.warrior.frame)
        self.warrior.frame = (self.warrior.frame + self.animation_speed * delta_time) % 4

        # 애니메이션이 한 사이클 완료되었는지 확인 (프레임이 0으로 돌아갈 때)
        if int(self.warrior.frame) < prev_frame or (prev_frame == 3 and int(self.warrior.frame) == 0):
            self.warrior.attack1_end_time = time.time()
            self.warrior.can_combo = True
            print(f"Attack1 완료, 콤보 윈도우 시작: {self.warrior.can_combo}")

            if not any(self.warrior.keys.values()):
                self.warrior.state_machine.cur_state = self.warrior.IDLE
                self.warrior.IDLE.enter(('STOP', 0))
            else:
                self.warrior.state_machine.cur_state = self.warrior.RUN
                self.warrior.RUN.enter(('STOP', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.warrior.x, self.warrior.y)
        else:
            screen_x, screen_y = self.warrior.x, self.warrior.y

        if self.warrior.face_dir == 1:
            self.warrior.imageA1.clip_draw(int(self.warrior.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.warrior.imageA1.clip_composite_draw(int(self.warrior.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)
#----------------------------------------------------------------
class WAttack2:
    def __init__(self, warrior):
        self.warrior = warrior
        self.animation_speed = 12  # 초당 프레임 수 (공격은 빠르게)

    def enter(self, e):
        print("ATTACK2 시작!")
        self.warrior.frame = 0
        self.warrior.can_combo = False
        self.warrior.attack1_end_time = None
        self.warrior.dirx = 0
        self.warrior.diry = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        prev_frame = int(self.warrior.frame)
        self.warrior.frame = (self.warrior.frame + self.animation_speed * delta_time) % 4

        # 애니메이션이 한 사이클 완료되었는지 확인
        if int(self.warrior.frame) < prev_frame or (prev_frame == 3 and int(self.warrior.frame) == 0):
            if not any(self.warrior.keys.values()):
                self.warrior.state_machine.cur_state = self.warrior.IDLE
                self.warrior.IDLE.enter(('STOP', 0))
            else:
                self.warrior.state_machine.cur_state = self.warrior.RUN
                self.warrior.RUN.enter(('STOP', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.warrior.x, self.warrior.y)
        else:
            screen_x, screen_y = self.warrior.x, self.warrior.y

        if self.warrior.face_dir == 1:
            self.warrior.imageA2.clip_draw(int(self.warrior.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.warrior.imageA2.clip_composite_draw(int(self.warrior.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)

#----------------------------------------------------------------
class Warrior:
    def __init__(self):
        self.x, self.y = 300,300
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = -1
        self.keys = {'left': False, 'right': False, 'up': False, 'down': False}
        self.attack1_end_time = None
        self.can_combo = False
        self.imageI = load_image('resource/Warrior_Idle.png')
        self.imageR = load_image('resource/Warrior_Run.png')
        self.imageA1 = load_image('resource/Warrior_Attack1.png')
        self.imageA2 = load_image('resource/Warrior_Attack2.png')

        self.IDLE = WIdle(self)
        self.RUN = WRun(self)
        self.ATTACK1 = WAttack1(self)
        self.ATTACK2 = WAttack2(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE:{right_down:self.RUN, left_down:self.RUN, up_down:self.RUN, down_down:self.RUN,
                          a_down_combo(self):self.ATTACK2, a_down:self.ATTACK1},
                self.RUN:{right_up:self.RUN, left_up:self.RUN, right_down:self.RUN, left_down:self.RUN,
                          up_up:self.RUN, down_up:self.RUN, up_down:self.RUN, down_down:self.RUN,
                          a_down_combo(self):self.ATTACK2, a_down:self.ATTACK1},
                self.ATTACK1:{a_down_combo(self):self.ATTACK2},
                self.ATTACK2:{}
            })

    def update(self, delta_time):
        self.state_machine.update(delta_time)
        pass

    def draw(self, camera=None):
        self.state_machine.draw(camera)
        pass

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT',event))
        pass

    def get_bb(self):
        # 히트박스 크기 (스프라이트보다 작게 설정)
        half_width = 40
        half_height = 40
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height
#----------------------------------------------------------------