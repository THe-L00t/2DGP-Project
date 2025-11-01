from pico2d import *
from warior import Warrior
from child import Child
from camera import Camera
#----------------------------------------------------------------
def handle_events():
    global running, cur_character, camera

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_f:
            if cur_character == 'warrior':
                cur_character = 'child'
                camera.set_target(child)
            else:
                cur_character = 'warrior'
                camera.set_target(warrior)
        else:
            if cur_character == 'warrior':
                warrior.handle_event(event)
            elif cur_character == 'child':
                child.handle_event(event)


#----------------------------------------------------------------
def init_world():
    global world
    global warrior
    global child
    global cur_character
    global camera

    cur_character = 'warrior'
    warrior = Warrior()
    child = Child()
    camera = Camera()
    camera.set_target(warrior)
    world = []

    world.append(child)
    world.append(warrior)


#----------------------------------------------------------------
def update_world():
    for object in world:
        object.update()

    if cur_character == 'warrior':
        camera.set_target(warrior)
    elif cur_character == 'child':
        camera.set_target(child)

    camera.update()
#----------------------------------------------------------------
def render_world():
    clear_canvas()
    for object in world:
        object.draw(camera)
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