from pico2d import *
from event_check import *
from state_machine import StateMachine

#----------------------------------------------------------------
# 전역 설정 - 여기서 일괄 수정
#----------------------------------------------------------------
# 스프라이트 크기
PIXEL_WIDTH = 192
PIXEL_HEIGHT = 192

# 충돌 박스 크기
COLLISION_HALF_WIDTH = 40
COLLISION_HALF_HEIGHT = 40

# 공격 박스 크기
ATTACK_RANGE = 30
ATTACK_WIDTH = 80
ATTACK_HEIGHT = 110

# 이동 속도
MOVE_SPEED = 300  # 픽셀/초

# 체력
MAX_HP = 200

# 공격력
ATTACK1_POWER = 30  # 기본 공격
ATTACK2_POWER = 50  # 콤보 공격
#----------------------------------------------------------------

class WIdle:
    def __init__(self, warrior):
        self.warrior = warrior
        self.animation_speed = 8  # 초당 프레임 수

    def enter(self, e):
        self.warrior.frame = 0
        self.warrior.dirx = 0
        self.warrior.diry = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        import time
        self.warrior.frame = (self.warrior.frame + self.animation_speed * delta_time) % 8

        if self.warrior.attack1_end_time:
            elapsed = time.time() - self.warrior.attack1_end_time
            if elapsed > 0.5:
                self.warrior.can_combo = False
                self.warrior.attack1_end_time = None
                print("콤보 타임 종료")

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.warrior.x, self.warrior.y)
        else:
            screen_x, screen_y = self.warrior.x, self.warrior.y

        if self.warrior.face_dir == 1:
            self.warrior.imageI.clip_draw(int(self.warrior.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.warrior.imageI.clip_composite_draw(int(self.warrior.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)
#----------------------------------------------------------------
class WRun:
    def __init__(self, warrior):
        self.warrior = warrior
        self.animation_speed = 10  # 초당 프레임 수
        self.move_speed = MOVE_SPEED  # 전역 설정에서 가져옴

    def enter(self, e):
        # 공격에서 넘어올 때 이동 속도 초기화
        self.warrior.dirx = 0
        self.warrior.diry = 0

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

    def do(self, delta_time):
        import time
        self.warrior.frame = (self.warrior.frame + self.animation_speed * delta_time) % 6

        if self.warrior.attack1_end_time:
            elapsed = time.time() - self.warrior.attack1_end_time
            if elapsed > 0.5:
                self.warrior.can_combo = False
                self.warrior.attack1_end_time = None
                print("콤보 타임 종료")

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

        self.warrior.x += self.warrior.dirx * self.move_speed * delta_time
        self.warrior.y += self.warrior.diry * self.move_speed * delta_time

        if not any(self.warrior.keys.values()):
            self.warrior.state_machine.cur_state = self.warrior.IDLE
            self.warrior.IDLE.enter(('STOP', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.warrior.x, self.warrior.y)
        else:
            screen_x, screen_y = self.warrior.x, self.warrior.y

        if self.warrior.face_dir == 1:
            self.warrior.imageR.clip_draw(int(self.warrior.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.warrior.imageR.clip_composite_draw(int(self.warrior.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)

#----------------------------------------------------------------
class WAttack1:
    def __init__(self, warrior):
        self.warrior = warrior
        self.animation_speed = 12  # 초당 프레임 수
        self.attack_active_frames = [1, 2]  # 공격 판정이 활성화되는 프레임

    def enter(self, e):
        self.warrior.frame = 0
        self.warrior.attack1_end_time = None
        self.warrior.can_combo = False
        self.animation_finished = False
        self.warrior.attack1_active = False  # 공격 판정 활성화 플래그
        # 공격 시작 시 이동 속도 초기화
        self.warrior.dirx = 0
        self.warrior.diry = 0
        print(f"[DEBUG] Warrior ATTACK1 시작")

    def exit(self, e):
        pass

    def do(self, delta_time):
        import time

        # 이전 프레임의 정수 값 저장
        prev_frame_int = int(self.warrior.frame)

        # 프레임 업데이트
        self.warrior.frame = (self.warrior.frame + self.animation_speed * delta_time) % 4

        # 현재 프레임의 정수 값
        curr_frame_int = int(self.warrior.frame)

        # 공격 판정 프레임 체크
        if curr_frame_int in self.attack_active_frames:
            if not self.warrior.attack1_active:
                self.warrior.attack1_active = True
                print(f"[DEBUG] Warrior ATTACK1 판정 활성화! (프레임: {curr_frame_int})")
        else:
            self.warrior.attack1_active = False

        # 프레임이 한 바퀴 돌았는지 확인 (3 -> 0으로 wrap around)
        # 또는 정확히 0이 되었을 때
        if not self.animation_finished and (prev_frame_int > curr_frame_int or (prev_frame_int == 3 and curr_frame_int == 0)):
            self.animation_finished = True
            self.warrior.attack1_end_time = time.time()
            self.warrior.can_combo = True
            self.warrior.attack1_active = False
            print(f"[DEBUG] Warrior ATTACK1 완료, 콤보 윈도우 시작")

            # 공격 종료 시 이동 속도 초기화
            self.warrior.dirx = 0
            self.warrior.diry = 0

            # 키 눌림 상태 확인 (SDL 이벤트로 확인)
            from sdl2 import SDL_GetKeyboardState, SDL_SCANCODE_LEFT, SDL_SCANCODE_RIGHT, SDL_SCANCODE_UP, SDL_SCANCODE_DOWN
            key_state = SDL_GetKeyboardState(None)
            self.warrior.keys['left'] = bool(key_state[SDL_SCANCODE_LEFT])
            self.warrior.keys['right'] = bool(key_state[SDL_SCANCODE_RIGHT])
            self.warrior.keys['up'] = bool(key_state[SDL_SCANCODE_UP])
            self.warrior.keys['down'] = bool(key_state[SDL_SCANCODE_DOWN])

            if not any(self.warrior.keys.values()):
                self.warrior.state_machine.cur_state = self.warrior.IDLE
                self.warrior.IDLE.enter(('STOP', 0))
            else:
                self.warrior.state_machine.cur_state = self.warrior.RUN
                self.warrior.RUN.enter(('STOP', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.warrior.x, self.warrior.y)
        else:
            screen_x, screen_y = self.warrior.x, self.warrior.y

        if self.warrior.face_dir == 1:
            self.warrior.imageA1.clip_draw(int(self.warrior.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.warrior.imageA1.clip_composite_draw(int(self.warrior.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)
#----------------------------------------------------------------
class WAttack2:
    def __init__(self, warrior):
        self.warrior = warrior
        self.animation_speed = 12  # 초당 프레임 수
        self.attack_active_frames = [1, 2, 3]  # 공격 판정이 활성화되는 프레임 (콤보는 더 길게)

    def enter(self, e):
        print("[DEBUG] Warrior ATTACK2 시작! (콤보 공격)")
        self.warrior.frame = 0
        self.warrior.can_combo = False
        self.warrior.attack1_end_time = None
        self.animation_finished = False
        self.warrior.attack2_active = False  # 공격 판정 활성화 플래그
        # 콤보 연결 시에도 이동 속도 초기화
        self.warrior.dirx = 0
        self.warrior.diry = 0

    def exit(self, e):
        pass

    def do(self, delta_time):
        # 이전 프레임의 정수 값 저장
        prev_frame_int = int(self.warrior.frame)

        # 프레임 업데이트
        self.warrior.frame = (self.warrior.frame + self.animation_speed * delta_time) % 4

        # 현재 프레임의 정수 값
        curr_frame_int = int(self.warrior.frame)

        # 공격 판정 프레임 체크
        if curr_frame_int in self.attack_active_frames:
            if not self.warrior.attack2_active:
                self.warrior.attack2_active = True
                print(f"[DEBUG] Warrior ATTACK2 판정 활성화! (프레임: {curr_frame_int})")
        else:
            self.warrior.attack2_active = False

        # 프레임이 한 바퀴 돌았는지 확인 (3 -> 0으로 wrap around)
        if not self.animation_finished and (prev_frame_int > curr_frame_int or (prev_frame_int == 3 and curr_frame_int == 0)):
            self.animation_finished = True
            self.warrior.attack2_active = False
            print(f"[DEBUG] Warrior ATTACK2 완료")

            # 공격 종료 시 이동 속도 초기화
            self.warrior.dirx = 0
            self.warrior.diry = 0

            # 키 눌림 상태 확인 (SDL 이벤트로 확인)
            from sdl2 import SDL_GetKeyboardState, SDL_SCANCODE_LEFT, SDL_SCANCODE_RIGHT, SDL_SCANCODE_UP, SDL_SCANCODE_DOWN
            key_state = SDL_GetKeyboardState(None)
            self.warrior.keys['left'] = bool(key_state[SDL_SCANCODE_LEFT])
            self.warrior.keys['right'] = bool(key_state[SDL_SCANCODE_RIGHT])
            self.warrior.keys['up'] = bool(key_state[SDL_SCANCODE_UP])
            self.warrior.keys['down'] = bool(key_state[SDL_SCANCODE_DOWN])

            if not any(self.warrior.keys.values()):
                self.warrior.state_machine.cur_state = self.warrior.IDLE
                self.warrior.IDLE.enter(('STOP', 0))
            else:
                self.warrior.state_machine.cur_state = self.warrior.RUN
                self.warrior.RUN.enter(('STOP', 0))

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.warrior.x, self.warrior.y)
        else:
            screen_x, screen_y = self.warrior.x, self.warrior.y

        if self.warrior.face_dir == 1:
            self.warrior.imageA2.clip_draw(int(self.warrior.frame) * 192,0,192,192,screen_x,screen_y)
        else:
            self.warrior.imageA2.clip_composite_draw(int(self.warrior.frame) * 192,0,192,192,0,'h',screen_x,screen_y,192,192)

#----------------------------------------------------------------
class Warrior:
    def __init__(self):
        self.x, self.y = 300,300
        self.frame = 0
        self.dirx = 0
        self.diry = 0
        self.face_dir = -1
        self.keys = {'left': False, 'right': False, 'up': False, 'down': False}
        self.attack1_end_time = None
        self.can_combo = False

        # 체력 (전역 설정에서 가져옴)
        self.hp = MAX_HP
        self.max_hp = MAX_HP

        # 공격력 (전역 설정에서 가져옴)
        self.attack_power = ATTACK1_POWER  # 기본 공격력
        self.attack2_power = ATTACK2_POWER  # 콤보 공격력 (더 강함)

        # 생존 상태
        self.is_alive = True

        self.imageI = load_image('resource/Warrior_Idle.png')
        self.imageR = load_image('resource/Warrior_Run.png')
        self.imageA1 = load_image('resource/Warrior_Attack1.png')
        self.imageA2 = load_image('resource/Warrior_Attack2.png')

        self.IDLE = WIdle(self)
        self.RUN = WRun(self)
        self.ATTACK1 = WAttack1(self)
        self.ATTACK2 = WAttack2(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE:{right_down:self.RUN, left_down:self.RUN, up_down:self.RUN, down_down:self.RUN,
                          a_down_combo(self):self.ATTACK2, a_down:self.ATTACK1},
                self.RUN:{right_up:self.RUN, left_up:self.RUN, right_down:self.RUN, left_down:self.RUN,
                          up_up:self.RUN, down_up:self.RUN, up_down:self.RUN, down_down:self.RUN,
                          a_down_combo(self):self.ATTACK2, a_down:self.ATTACK1},
                self.ATTACK1:{a_down_combo(self):self.ATTACK2},
                self.ATTACK2:{}
            })

    def update(self, delta_time):
        self.state_machine.update(delta_time)
        pass

    def draw(self, camera=None):
        self.state_machine.draw(camera)
        pass

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT',event))
        pass

    def get_bb(self):
        # 히트박스 크기 (전역 설정에서 가져옴)
        return (self.x - COLLISION_HALF_WIDTH, self.y - COLLISION_HALF_HEIGHT,
                self.x + COLLISION_HALF_WIDTH, self.y + COLLISION_HALF_HEIGHT)

    def get_attack_bb(self):
        """공격 충돌 박스 반환 (공격 판정 프레임일 때만)"""
        # ATTACK1 상태이고 판정이 활성화된 경우
        if self.state_machine.cur_state == self.ATTACK1:
            if not hasattr(self, 'attack1_active') or not self.attack1_active:
                return None
        # ATTACK2 상태이고 판정이 활성화된 경우
        elif self.state_machine.cur_state == self.ATTACK2:
            if not hasattr(self, 'attack2_active') or not self.attack2_active:
                return None
        # 공격 상태가 아니면 None 반환
        else:
            return None

        # 전역 설정에서 공격 범위 가져옴
        # 바라보는 방향에 따라 공격 박스 위치 설정
        if self.face_dir == 1:  # 오른쪽
            left = self.x - ATTACK_WIDTH // 2
            right = self.x + ATTACK_RANGE + ATTACK_WIDTH // 2
        else:  # 왼쪽
            left = self.x - ATTACK_RANGE - ATTACK_WIDTH // 2
            right = self.x + ATTACK_WIDTH // 2

        bottom = self.y - ATTACK_HEIGHT // 2
        top = self.y + ATTACK_HEIGHT // 2

        return left, bottom, right, top

    def get_current_attack_power(self):
        """현재 공격력 반환 (공격 중일 때만)"""
        if self.state_machine.cur_state == self.ATTACK1:
            return self.attack_power
        elif self.state_machine.cur_state == self.ATTACK2:
            return self.attack2_power
        return 0

    def take_damage(self, damage, attacker_x=None):
        """데미지를 받음 (넉백 포함)"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"Warrior가 {damage} 데미지를 받음! (남은 HP: {self.hp}/{self.max_hp})")

        # 넉백 효과 (공격자 위치 기반)
        if attacker_x is not None:
            knockback_distance = 20  # 밀려나는 거리
            if self.x > attacker_x:  # 공격자가 왼쪽에 있으면 오른쪽으로 밀림
                self.x += knockback_distance
                print(f"[DEBUG] Warrior 넉백: 오른쪽으로 {knockback_distance}px")
            else:  # 공격자가 오른쪽에 있으면 왼쪽으로 밀림
                self.x -= knockback_distance
                print(f"[DEBUG] Warrior 넉백: 왼쪽으로 {knockback_distance}px")

        if self.hp <= 0:
            print("Warrior 사망!")
            self.is_alive = False
#----------------------------------------------------------------
