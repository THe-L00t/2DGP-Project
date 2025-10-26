from pico2d import *
from event_check import *
from state_machine import StateMachine
#----------------------------------------------------------------
class Child:
    def __init__(self):
        self.x, self.y = 400, 300
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = 1
        self.imageI = load_image('resource/Child_Idle.png')
        self.imageR = load_image('resource/Child_Run.png')

    def update(self):
        self.state_machine.update()
        pass

    def draw(self):
        pass

    def handle_event(self, event):
        pass
#----------------------------------------------------------------