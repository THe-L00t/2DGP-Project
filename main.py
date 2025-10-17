from pico2d import *
from warior import Warrior
#----------------------------------------------------------------
def handle_events():
    global running

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            pass

#----------------------------------------------------------------
def init_world():
    global world
    global warrior

    warrior = Warrior()
    world = []

    world.append(warrior)


#----------------------------------------------------------------
def update_world():
    for object in world:
        object.update()
#----------------------------------------------------------------
def render_world():
    clear_canvas()
    for object in world:
        object.draw()
    update_canvas()
#----------------------------------------------------------------
running = True
open_canvas()
init_world()

while running:
    handle_events()
    update_world()
    render_world()
    #추후 deltaTime 적용해보기

close_canvas()