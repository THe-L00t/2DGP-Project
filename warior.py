from pico2d import *
from event_check import *
from state_machine import StateMachine
#----------------------------------------------------------------
class WIdle:
    def __init__(self, warrior):
        self.warrior = warrior

    def enter(self, e):
        self.warrior.frame = 0

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
        if left_down(e) or right_up(e):
            self.warrior.dir = -1
            self.warrior.face_dir = -1
        elif right_down(e) or left_up(e):
            self.warrior.dir = 1
            self.warrior.face_dir = 1

    def exit(self, e):
        pass

    def do(self):
        self.warrior.frame = (self.warrior.frame + 1) % 6
        self.warrior.x += self.warrior.dir * 5

    def draw(self):
        if self.warrior.face_dir == 1:
            self.warrior.imageR.clip_draw(self.warrior.frame * 192,0,192,192,self.warrior.x,self.warrior.y)
        else:
            self.warrior.imageR.clip_composite_draw(self.warrior.frame * 192,0,192,192,0,'h',self.warrior.x,self.warrior.y,192,192)

#----------------------------------------------------------------
class Warrior:
    def __init__(self):
        self.x, self.y = 400,300
        self.frame = 0
        self.dir = 0
        self.face_dir = -1
        self.imageI = load_image('resource/Warrior_Idle.png')
        self.imageR = load_image('resource/Warrior_Run.png')
        self.imageA1 = load_image('resource/Warrior_Attack1.png')
        self.imageA2 = load_image('resource/Warrior_Attack2.png')

        self.IDLE = WIdle(self)
        self.RUN = WRun(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE:{right_down:self.RUN, left_down:self.RUN, right_up:self.RUN, left_up:self.RUN},
                self.RUN:{right_up:self.IDLE, left_up:self.IDLE, right_down:self.IDLE, left_down:self.IDLE}
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