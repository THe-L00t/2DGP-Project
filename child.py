from pico2d import *
from event_check import *
from state_machine import StateMachine
#----------------------------------------------------------------
class CIdle:
    def __init__(self, child):
        self.child = child

    def enter(self, e):
        self.child.frame = 0
        self.child.dirx = 0
        self.child.diry = 0

    def exit(self, e):
        pass

    def do(self):
        self.child.frame = (self.child.frame +1) % 6

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.child.x, self.child.y)
        else:
            screen_x, screen_y = self.child.x, self.child.y

        if self.child.face_dir == 1:
            self.child.imageI.clip_draw(self.child.frame * 192,0,192,192,screen_x,screen_y)
        else:
            self.child.imageI.clip_composite_draw(self.child.frame * 192,0,192,192,0,'h',screen_x,screen_y,192,192)
#----------------------------------------------------------------
class CRun:
    def __init__(self, child):
        self.child = child

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

    def do(self):
        self.child.frame = (self.child.frame + 1) % 4

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

        self.child.x += self.child.dirx * 5
        self.child.y += self.child.diry * 5

        if not any(self.child.keys.values()):
            self.child.state_machine.cur_state = self.child.IDLE
            self.child.IDLE.enter(('STOP', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.child.x, self.child.y)
        else:
            screen_x, screen_y = self.child.x, self.child.y

        if self.child.face_dir == 1:
            self.child.imageR.clip_draw(self.child.frame * 192,0,192,192,screen_x,screen_y)
        else:
            self.child.imageR.clip_composite_draw(self.child.frame * 192,0,192,192,0,'h',screen_x,screen_y,192,192)
#----------------------------------------------------------------
class Child:
    def __init__(self):
        self.x, self.y = 500, 300
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = 1
        self.keys = {'left': False, 'right': False, 'up': False, 'down': False}
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
    def update(self):
        self.state_machine.update()
        pass

    def draw(self, camera=None):
        self.state_machine.draw(camera)
        pass

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass
#----------------------------------------------------------------