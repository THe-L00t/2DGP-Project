from pico2d import *
from sdl2 import *
#----------------------------------------------------------------
def right_down(e):
    return e[0] == 'INPUT' and e[1].type ==  SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type ==  SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type ==  SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type ==  SDL_KEYUP and e[1].key == SDLK_LEFT

def up_down(e):
    return e[0] == 'INPUT' and e[1].type ==  SDL_KEYDOWN and e[1].key == SDLK_UP

def up_up(e):
    return e[0] == 'INPUT' and e[1].type ==  SDL_KEYUP and e[1].key == SDLK_UP

def down_down(e):
    return e[0] == 'INPUT' and e[1].type ==  SDL_KEYDOWN and e[1].key == SDLK_DOWN

def down_up(e):
    return e[0] == 'INPUT' and e[1].type ==  SDL_KEYUP and e[1].key == SDLK_DOWN

def action_end(e):
    return e[0] == 'ACTION_END'