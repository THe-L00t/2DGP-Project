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

    def draw(self):
        if self.child.face_dir == 1:
            self.child.imageI.clip_draw(self.child.frame * 192,0,192,192,self.child.x,self.child.y)
        else:
            self.child.imageI.clip_composite_draw(self.child.frame * 192,0,192,192,0,'h',self.child.x,self.child.y,192,192)
#----------------------------------------------------------------
class CRun:
    def __init__(self, child):
        self.child = child

    def enter(self, e):
        if left_down(e):
            self.child.dirx -= 1
            self.child.face_dir = -1
        elif right_up(e):
            self.child.dirx -= 1
            self.child.face_dir = -1
        elif right_down(e):
            self.child.dirx += 1
            self.child.face_dir = 1
        elif left_up(e):
            self.child.dirx += 1
            self.child.face_dir = 1

        if up_down(e):
            self.child.diry += 1
        elif down_up(e):
            self.child.diry += 1
        elif down_down(e):
            self.child.diry -= 1
        elif up_up(e):
            self.child.diry -= 1

    def exit(self, e):
        pass

    def do(self):
        self.child.frame = (self.child.frame + 1) % 4
        self.child.x += self.child.dirx * 5
        self.child.y += self.child.diry * 5

    def draw(self):
        if self.child.face_dir == 1:
            self.child.imageR.clip_draw(self.child.frame * 192,0,192,192,self.child.x,self.child.y)
        else:
            self.child.imageR.clip_composite_draw(self.child.frame * 192,0,192,192,0,'h',self.child.x,self.child.y,192,192)
#----------------------------------------------------------------
class Child:
    def __init__(self):
        self.x, self.y = 500, 300
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = 1
        self.imageI = load_image('resource/Child_Idle.png')
        self.imageR = load_image('resource/Child_Run.png')

        self.IDLE = CIdle(self)
        self.RUN = CRun(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.RUN, left_down: self.RUN, right_up: self.RUN, left_up: self.RUN,
                            up_down: self.RUN, down_down: self.RUN, up_up: self.RUN, down_up: self.RUN},
                self.RUN: {right_up: self.IDLE, left_up: self.IDLE, right_down: self.IDLE, left_down: self.IDLE,
                           up_up: self.IDLE, down_up: self.IDLE, up_down: self.IDLE, down_down: self.IDLE}
            })
    def update(self):
        self.state_machine.update()
        pass

    def draw(self):
        self.state_machine.draw()
        pass

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass
#----------------------------------------------------------------