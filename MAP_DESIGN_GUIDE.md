# 맵 구성 방법 가이드

## 📋 개요
타일 기반 맵 시스템으로 블럭 단위 맵을 구성합니다.
- 타일 크기: 64x64 픽셀
- 타입: 바닥(FLOOR), 벽(WALL), 사다리(LADDER), 빈공간(EMPTY)
- floor_level로 층 구분
- 청크 기반 렌더링 최적화

---

## 🎨 맵 구성 방법 3가지

### **방법 1: 텍스트 기반 맵 (추천 - 초기 개발/프로토타입)**

**장점:**
- 가장 직관적이고 빠른 맵 작성
- 코드 내에서 바로 수정 가능
- 맵 구조를 시각적으로 파악하기 쉬움
- 버전 관리(Git)에 최적

**사용 예시:**
```python
# 간단한 맵 작성
map_text = """
###########
#.........#
#==...==..#
#.H.......#
#=====H====#
###########
"""

tilemap = TileMap()
tilemap.load_from_text(map_text, floor_level=0)

# 문자 의미:
# # = 벽 (WALL)
# = = 바닥 (FLOOR)
# H = 사다리 (LADDER)
# . = 빈공간 (EMPTY)
```

**다층 맵 구성:**
```python
# 1층
floor1 = """
###########
#==========#
###########
"""
tilemap.load_from_text(floor1, floor_level=1)

# 2층 (사다리로 연결)
floor2 = """
###########
#==========#
#....H.....#
###########
"""
tilemap.load_from_text(floor2, floor_level=2)
```

---

### **방법 2: JSON 파일 기반 (추천 - 대규모 맵)**

**장점:**
- 맵 데이터와 코드 분리
- 맵 에디터 도구 제작 가능
- 재사용 가능한 맵 라이브러리 구축
- 동적 맵 로딩 (스테이지 시스템)

**파일 예시 (map_stage1.json):**
```json
{
  "tiles": [
    {"type": 2, "grid_x": 0, "grid_y": 0, "floor_level": 0},
    {"type": 1, "grid_x": 1, "grid_y": 0, "floor_level": 0},
    {"type": 3, "grid_x": 5, "grid_y": 5, "floor_level": 0}
  ]
}
```

**사용 코드:**
```python
tilemap = TileMap()
tilemap.load_from_file('maps/stage1.json')
```

**저장 코드:**
```python
# 코드로 맵 작성 후 저장
tilemap.add_tile(TILE_WALL, 0, 0)
tilemap.add_tile(TILE_FLOOR, 1, 0, floor_level=1)
tilemap.save_to_file('maps/stage1.json')
```

---

### **방법 3: 코드 직접 작성 (추천 - 동적 맵 생성)**

**장점:**
- 프로시저럴 생성 가능
- 런타임 맵 변경
- 패턴 기반 맵 생성

**사용 예시:**
```python
tilemap = TileMap()

# 벽으로 테두리 생성
for x in range(20):
    tilemap.add_tile(TILE_WALL, x, 0)
    tilemap.add_tile(TILE_WALL, x, 10)

# 바닥 생성
for x in range(1, 19):
    tilemap.add_tile(TILE_FLOOR, x, 1, floor_level=1)

# 사다리 추가
for y in range(1, 5):
    tilemap.add_tile(TILE_LADDER, 10, y)
```

---

## 🏗️ 권장 워크플로우

### **단계 1: 프로토타입 (텍스트 기반)**
```python
# 빠른 레벨 디자인
prototype_map = """
#################
#...............#
#===...H...===..#
#......H........#
#======H========#
#################
"""
tilemap.load_from_text(prototype_map, floor_level=0)
```

### **단계 2: 개발 중기 (JSON 변환)**
```python
# 프로토타입이 확정되면 JSON으로 저장
tilemap.save_to_file('maps/level1.json')
```

### **단계 3: 최종 (JSON + 이미지 설정)**
```python
# 맵 로드
tilemap.load_from_file('maps/level1.json')

# 타일별 이미지 설정
for tile in tilemap.tiles.values():
    if tile.tile_type == TILE_FLOOR:
        tile.set_image('resource/floor.png')
    elif tile.tile_type == TILE_WALL:
        tile.set_image('resource/wall.png')
    elif tile.tile_type == TILE_LADDER:
        tile.set_image('resource/ladder.png')
```

---

## 📦 청크 시스템 (자동 최적화)

**작동 방식:**
- 화면 크기(800x600)를 한 청크로 간주
- `get_visible_tiles(camera)` 함수가 자동으로 보이는 타일만 반환
- 카메라 밖의 타일은 렌더링하지 않음

**사용 예시:**
```python
def render_world():
    clear_canvas()
    tilemap.draw(camera)  # 자동으로 최적화됨
    for object in world:
        object.draw(camera)
    update_canvas()
```

---

## 🎯 층(Floor) 시스템

**개념:**
- 각 바닥 타일은 floor_level 값을 가짐
- 캐릭터는 같은 floor_level의 바닥만 이동 가능
- 사다리를 통해 다른 floor_level로 이동

**구현 예시:**
```python
# 1층 바닥
for x in range(10, 20):
    tilemap.add_tile(TILE_FLOOR, x, 5, floor_level=1)

# 2층 바닥
for x in range(10, 20):
    tilemap.add_tile(TILE_FLOOR, x, 10, floor_level=2)

# 1층과 2층을 연결하는 사다리
for y in range(5, 11):
    tilemap.add_tile(TILE_LADDER, 15, y)
```

---

## 🛠️ 맵 에디터 도구 (향후 개발 가능)

간단한 맵 에디터를 만들 수 있습니다:
```python
# 마우스 클릭으로 타일 배치
# 1,2,3 키로 타일 타입 선택
# S키로 JSON 저장
# L키로 JSON 로드
```

---

## 📊 성능 최적화 팁

1. **타일 이미지 재사용**
   - 같은 타입의 타일은 이미지 객체 공유

2. **정적 맵은 JSON 사용**
   - 런타임 파싱보다 빠름

3. **청크 시스템 활용**
   - 자동으로 보이는 부분만 렌더링

4. **딕셔너리 기반 저장**
   - `tiles = {(x,y): Tile}` 구조로 빠른 접근

---

## 🎮 실제 사용 예시

```python
# main.py에서
def init_world():
    global tilemap

    # 방법 1: 텍스트로 빠른 프로토타입
    map_data = """
    ###################
    #.................#
    #===....H.....===..#
    #.......H.........#
    #=======H=========#
    ###################
    """
    tilemap = TileMap()
    tilemap.load_from_text(map_data, floor_level=0)

    # 이미지 설정 (일괄 적용)
    for tile in tilemap.tiles.values():
        if tile.tile_type == TILE_FLOOR:
            tile.set_image('resource/floor.png')
        # ... 기타 타입

def render_world():
    clear_canvas()
    tilemap.draw(camera)  # 자동 청크 최적화
    # ... 캐릭터 렌더링
```

---

## 💡 결론 및 추천

**초기 개발:**
- ✅ 텍스트 기반 맵 사용
- 빠른 반복 개발 가능

**중기 개발:**
- ✅ JSON 파일로 변환
- 맵 데이터 관리 시작

**최종 단계:**
- ✅ 맵 에디터 도구 개발 (선택)
- JSON + 이미지 시스템 완성

**핵심:** 청크 시스템은 자동으로 작동하므로 개발자는 맵 구성에만 집중하면 됩니다!
