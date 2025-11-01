from pico2d import *
from event_check import *
from state_machine import StateMachine
#----------------------------------------------------------------
class WIdle:
    def __init__(self, warrior):
        self.warrior = warrior

    def enter(self, e):
        self.warrior.frame = 0
        self.warrior.dirx = 0
        self.warrior.diry = 0

    def exit(self, e):
        pass

    def do(self):
        self.warrior.frame = (self.warrior.frame +1) % 8

    def draw(self):
        if self.warrior.face_dir == 1:
            self.warrior.imageI.clip_draw(self.warrior.frame * 192,0,192,192,self.warrior.x,self.warrior.y)
        else:
            self.warrior.imageI.clip_composite_draw(self.warrior.frame * 192,0,192,192,0,'h',self.warrior.x,self.warrior.y,192,192)
#----------------------------------------------------------------
class WRun:
    def __init__(self, warrior):
        self.warrior = warrior

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

    def do(self):
        self.warrior.frame = (self.warrior.frame + 1) % 6

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

        self.warrior.x += self.warrior.dirx * 5
        self.warrior.y += self.warrior.diry * 5

        if not any(self.warrior.keys.values()):
            self.warrior.state_machine.cur_state = self.warrior.IDLE
            self.warrior.IDLE.enter(('STOP', 0))

    def draw(self):
        if self.warrior.face_dir == 1:
            self.warrior.imageR.clip_draw(self.warrior.frame * 192,0,192,192,self.warrior.x,self.warrior.y)
        else:
            self.warrior.imageR.clip_composite_draw(self.warrior.frame * 192,0,192,192,0,'h',self.warrior.x,self.warrior.y,192,192)

#----------------------------------------------------------------
class Warrior:
    def __init__(self):
        self.x, self.y = 300,300
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = -1
        self.keys = {'left': False, 'right': False, 'up': False, 'down': False}
        self.imageI = load_image('resource/Warrior_Idle.png')
        self.imageR = load_image('resource/Warrior_Run.png')
        self.imageA1 = load_image('resource/Warrior_Attack1.png')
        self.imageA2 = load_image('resource/Warrior_Attack2.png')

        self.IDLE = WIdle(self)
        self.RUN = WRun(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE:{right_down:self.RUN, left_down:self.RUN, up_down:self.RUN, down_down:self.RUN},
                self.RUN:{right_up:self.RUN, left_up:self.RUN, right_down:self.RUN, left_down:self.RUN,
                          up_up:self.RUN, down_up:self.RUN, up_down:self.RUN, down_down:self.RUN}
            })

    def update(self):
        self.state_machine.update()
        pass

    def draw(self):
        self.state_machine.draw()
        pass

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT',event))
        pass
#----------------------------------------------------------------