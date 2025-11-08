# 맵 구성 가이드 (세분화된 타일 시스템)

## 📋 개요
세분화된 타일 기반 맵 시스템으로 블럭 단위 맵을 구성합니다.
- 타일 크기: 64x64 픽셀
- floor_level로 층 구분
- 애니메이션 타일 지원
- 청크 기반 렌더링 최적화

---

## 🎨 타일 타입 (세분화)

### 배경/환경
- **`~`** (TILE_WATER = 0): 물/바다 - 빈 공간을 바다로 채움, 통과 불가

### 바닥 타입
- **`=`** (TILE_FLOOR_CENTER = 1): 바닥 중앙부 - 평평한 일반 바닥
- **`[`** (TILE_FLOOR_EDGE_LEFT = 2): 바닥 왼쪽 가장자리 - 절벽
- **`]`** (TILE_FLOOR_EDGE_RIGHT = 3): 바닥 오른쪽 가장자리 - 절벽
- **`^`** (TILE_FLOOR_EDGE_TOP = 4): 바닥 위쪽 가장자리
- **`_`** (TILE_FLOOR_EDGE_BOTTOM = 5): 바닥 아래쪽 가장자리

### 경사로 (슬로프)
- **`/`** (TILE_SLOPE_UP_RIGHT = 6): 오른쪽으로 올라가는 슬로프
- **`\`** (TILE_SLOPE_UP_LEFT = 7): 왼쪽으로 올라가는 슬로프

### 벽
- **`#`** (TILE_WALL = 8): 벽 - 통과 불가

### 하위 호환 (기존 코드 지원)
- **`.`** = `~` (TILE_WATER)
- **`H`** = `/` (TILE_SLOPE_UP_RIGHT)

---

## 🏗️ 맵 구성 방법

### 방법 1: 텍스트 기반 맵 (추천 - 프로토타입)

**간단한 섬 맵 예시:**
```python
island_map = """
~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~[========]~~~~~~~~~~~
~~~~~~[========]~~~~~~~~~~~
~~~~[/==========\\]~~~~~~~~~
~~~~[============]~~~~~~~~~
~~~/==============\\~~~~~~~~
~~~~~~~~~~~~~~~~~~~
"""

tilemap = TileMap()
tilemap.load_from_text(island_map, floor_level=0)
```

**다층 구조 예시:**
```python
# 1층
floor1 = """
#####################
#[=================]#
#[=================]#
#[=====/========\\===]#
#####################
"""
tilemap.load_from_text(floor1, floor_level=0)

# 2층 (슬로프로 연결)
floor2 = """
~~~~~###########~~~~~
~~~~~#[=======]#~~~~~
~~~~~#[=======]#~~~~~
~~~~~###########~~~~~
"""
tilemap.load_from_text(floor2, floor_level=1)
```

**시각적 절벽 디자인:**
```python
cliff_map = """
####################
#[================]#
#[================]#  <- 양쪽 가장자리가 절벽
#[====/===\\=======]#  <- 슬로프 포함
####################
"""
```

---

### 방법 2: JSON 파일 기반

**파일 예시 (maps/island.json):**
```json
{
  "tiles": [
    {"type": 0, "grid_x": 0, "grid_y": 0, "floor_level": 0},
    {"type": 1, "grid_x": 5, "grid_y": 5, "floor_level": 0},
    {"type": 2, "grid_x": 4, "grid_y": 5, "floor_level": 0},
    {"type": 3, "grid_x": 10, "grid_y": 5, "floor_level": 0},
    {"type": 6, "grid_x": 7, "grid_y": 6, "floor_level": 0}
  ]
}
```

**사용 코드:**
```python
tilemap = TileMap()
tilemap.load_from_file('maps/island.json')
```

---

### 방법 3: 코드 직접 작성

```python
from tile import *

tilemap = TileMap()

# 바다 배경
for x in range(20):
    for y in range(15):
        tilemap.add_tile(TILE_WATER, x, y)

# 섬 만들기
for x in range(5, 15):
    tilemap.add_tile(TILE_FLOOR_CENTER, x, 5)

# 절벽 (가장자리)
tilemap.add_tile(TILE_FLOOR_EDGE_LEFT, 4, 5)
tilemap.add_tile(TILE_FLOOR_EDGE_RIGHT, 15, 5)

# 슬로프 (경사로)
tilemap.add_tile(TILE_SLOPE_UP_RIGHT, 7, 6)
tilemap.add_tile(TILE_SLOPE_UP_LEFT, 12, 6)
```

---

## 🎬 애니메이션 타일 설정

### 단일 이미지 타일
```python
tile = tilemap.get_tile(5, 5)
tile.set_image('resource/Water Background color.png')
```

### 애니메이션 타일 (스프라이트 시트)
```python
# 12프레임 물 애니메이션
tile = tilemap.get_tile(3, 3)
tile.set_animated_image(
    'resource/Water_FlatGround_#1_(12frames).png',
    frame_count=12,
    frame_width=64,
    frame_duration=0.1  # 각 프레임 0.1초
)
```

### 타일별 이미지 일괄 설정
```python
for tile in tilemap.tiles.values():
    if tile.is_water():
        tile.set_animated_image('resource/Water_FlatGround_#1_(12frames).png', 12, 64, 0.1)
    elif tile.is_floor_center():
        tile.set_image('resource/floor_center.png')
    elif tile.is_floor_edge():
        tile.set_image('resource/floor_edge.png')
    elif tile.is_slope():
        tile.set_image('resource/slope.png')
```

---

## 🎮 타일 메서드 활용

### 타일 타입 확인
```python
tile = tilemap.get_tile(x, y)

# 타입 확인
if tile.is_floor():          # 모든 바닥 타입
    print("바닥")
if tile.is_floor_center():   # 중앙 바닥만
    print("중앙 바닥")
if tile.is_floor_edge():     # 가장자리만
    print("절벽")
if tile.is_slope():          # 슬로프
    direction = tile.get_slope_direction()  # 1: 오른쪽 위, -1: 왼쪽 위
if tile.is_water():          # 바다
    print("물")
if tile.is_passable():       # 통과 가능 여부
    print("지나갈 수 있음")
```

### 디버깅
```python
tile = tilemap.get_tile(5, 5)
print(f"타일 타입: {tile.get_type_name()}")  # "FLOOR_CENTER", "SLOPE_UP_RIGHT" 등
```

---

## 💡 디자인 패턴 예시

### 1. 단순 플랫폼
```
~~~~~~~~~~~~~~~~~~~
~~[============]~~~
~~[============]~~~
~~~~~~~~~~~~~~~~~~~
```

### 2. 슬로프가 있는 언덕
```
~~~~~~~~~~~~~~~~~~~
~~~~~~[====]~~~~~~~
~~~~[/======\\]~~~~~
~~[============]~~~
~~~~~~~~~~~~~~~~~~~
```

### 3. 다층 구조
```
층 2:
~~~~~[====]~~~~~
~~~~~[====]~~~~~

층 1 (슬로프로 연결):
[===/========\\===]
[================]
```

### 4. 섬 지형
```
~~~~~~~~~~~~~~~~~~~~~~~
~~~~[========]~~~~~~~~~
~~[/==========\\]=======]
~~[==================]~
~~~~[==============]~~~
~~~~~~[==========]~~~~~
~~~~~~~~~~~~~~~~~~~~~~~
```

---

## 📦 청크 시스템 (자동 최적화)

**작동 방식:**
- 화면 크기(800x600)를 한 청크로 간주
- `get_visible_tiles(camera)` 함수가 자동으로 보이는 타일만 반환
- 카메라 밖의 타일은 렌더링하지 않음

**사용 예시:**
```python
def update_world(delta_time):
    tilemap.update(delta_time)  # 애니메이션 업데이트
    # ...

def render_world():
    clear_canvas()
    tilemap.draw(camera)  # 자동으로 최적화됨
    # ...
```

---

## 🎯 층(Floor) 시스템

**개념:**
- 각 타일은 floor_level 값을 가짐
- 캐릭터는 같은 floor_level만 이동 가능
- 슬로프를 통해 다른 floor_level로 이동

**구현 예시:**
```python
# 1층 바닥
for x in range(10, 20):
    tilemap.add_tile(TILE_FLOOR_CENTER, x, 5, floor_level=1)

# 2층 바닥
for x in range(10, 20):
    tilemap.add_tile(TILE_FLOOR_CENTER, x, 10, floor_level=2)

# 1층과 2층을 연결하는 슬로프
for y in range(5, 11):
    tilemap.add_tile(TILE_SLOPE_UP_RIGHT, 15, y)
```

---

## 📊 타일 타입 코드 참조표

| 기호 | 타입 코드 | 상수명 | 설명 | 통과 가능 |
|------|----------|--------|------|----------|
| `~` | 0 | TILE_WATER | 물/바다 | ❌ |
| `=` | 1 | TILE_FLOOR_CENTER | 바닥 중앙 | ✅ |
| `[` | 2 | TILE_FLOOR_EDGE_LEFT | 왼쪽 절벽 | ✅ |
| `]` | 3 | TILE_FLOOR_EDGE_RIGHT | 오른쪽 절벽 | ✅ |
| `^` | 4 | TILE_FLOOR_EDGE_TOP | 위쪽 가장자리 | ✅ |
| `_` | 5 | TILE_FLOOR_EDGE_BOTTOM | 아래쪽 가장자리 | ✅ |
| `/` | 6 | TILE_SLOPE_UP_RIGHT | 오른쪽 위 슬로프 | ✅ |
| `\` | 7 | TILE_SLOPE_UP_LEFT | 왼쪽 위 슬로프 | ✅ |
| `#` | 8 | TILE_WALL | 벽 | ❌ |

---

## 🎮 실전 사용 예시

```python
# main.py에서
def init_world():
    global tilemap

    # 텍스트로 빠른 프로토타입
    map_data = """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ~~~~~~[====================]~~~~~~~
    ~~~~~~[====================]~~~~~~~
    ~~~~[/========================\\]~~~
    ~~~~[=====/========\\===========]~~~
    ~~~/============================\\~~
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    tilemap = TileMap()
    tilemap.load_from_text(map_data, floor_level=0)

    # 이미지 설정 (일괄 적용)
    for tile in tilemap.tiles.values():
        if tile.is_water():
            tile.set_animated_image(
                'resource/Water_FlatGround_#1_(12frames).png',
                frame_count=12,
                frame_width=64,
                frame_duration=0.08
            )
        elif tile.is_floor_center():
            tile.set_image('resource/floor_center.png')
        elif tile.is_floor_edge():
            tile.set_image('resource/floor_edge.png')
        elif tile.is_slope():
            tile.set_image('resource/slope.png')

def update_world(delta_time):
    tilemap.update(delta_time)  # 애니메이션 업데이트
    # ...

def render_world():
    clear_canvas()
    tilemap.draw(camera)  # 자동 청크 최적화
    # ...
```

---

## 💡 핵심 요약

**초기 개발:**
- ✅ 텍스트 기반 맵 사용
- 빠른 반복 개발 가능

**중기 개발:**
- ✅ JSON 파일로 변환
- 맵 데이터 관리 시작

**최종 단계:**
- ✅ 애니메이션 타일 적용
- JSON + 이미지 시스템 완성

**핵심:**
- 청크 시스템은 자동 작동
- 개발자는 맵 디자인에만 집중
- 바다(~)로 빈 공간을 채우고, 바닥 가장자리([, ])로 절벽 표현
- 슬로프(/, \)로 층간 이동
