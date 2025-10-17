from pico2d import *

#----------------------------------------------------------------



#----------------------------------------------------------------
class Warrior:
    def __init__(self):
        self.x, self.y = 400,300
        self.frame = 0
        self.image = load_image('resource/Warrior_Idle.png')
        pass

    def update(self):
        self.frame = (self.frame + 1) % 8
        pass

    def draw(self):
        self.image.clip_draw(self.frame*192,0,192,192,self.x,self.y,100,100)
        pass

    def handle_event(self, event):
        pass
#----------------------------------------------------------------