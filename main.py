from pico2d import *
from warior import Warrior
from child import Child
#----------------------------------------------------------------
def handle_events():
    global running, cur_character

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_f:
            if cur_character == 'warrior':
                cur_character = 'child'
            else:
                cur_character = 'warrior'
        else:
            if cur_character == 'warrior':
                warrior.handle_event(event)
            else:
                child.handle_event(event)
                pass

#----------------------------------------------------------------
def init_world():
    global world
    global warrior
    global child
    global cur_character
    cur_character = 'warrior'
    warrior = Warrior()
    child = Child()
    world = []

    world.append(warrior)
    world.append(child)

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
    delay(0.016)
    #추후 deltaTime 적용해보기

close_canvas()