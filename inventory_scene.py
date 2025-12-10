"""
퀘스트 Scene - 플레이 화면 위에 오버레이로 표시
"""
from pico2d import *
import game_framework

# 전역 변수
quest_manager = None  # play_scene에서 설정
font = None
quest_bg_image = None  # 퀘스트 배경 이미지

def enter():
    """Scene 진입 시 호출"""
    global font, quest_bg_image
    try:
        # 프로젝트 내 맑은 고딕 폰트 사용
        font = load_font('resource/malgun.ttf', 20)
    except:
        try:
            # 시스템 폰트 시도
            font = load_font('C:/Windows/Fonts/malgun.ttf', 20)
        except:
            # 폰트 로딩 실패 시 None으로 설정
            font = None
            print("[WARNING] 폰트를 로드할 수 없습니다. 텍스트가 표시되지 않습니다.")

    # 퀘스트 배경 이미지 로드
    try:
        quest_bg_image = load_image('resource/quest.png')
    except:
        quest_bg_image = None
        print("[WARNING] quest.png를 로드할 수 없습니다.")

def exit():
    """Scene 종료 시 호출"""
    pass

def pause():
    """Scene이 일시정지될 때 호출"""
    pass

def resume():
    """Scene이 재개될 때 호출"""
    pass

def handle_events(event):
    """이벤트 처리"""
    if event.type == SDL_KEYDOWN:
        if event.key == SDLK_ESCAPE or event.key == SDLK_i:
            # ESC 또는 I 키를 누르면 퀘스트 창 닫기
            game_framework.pop_scene()

def update(delta_time):
    """업데이트"""
    pass

def draw():
    """렌더링 - 퀘스트 목록 창"""
    # 캔버스 크기 가져오기
    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 퀘스트 창 배경 (중앙에 사각형)
    center_x = canvas_width // 2
    center_y = canvas_height // 2
    box_width = 350  # 350으로 줄임
    box_height = 600

    left = center_x - box_width // 2
    right = center_x + box_width // 2
    bottom = center_y - box_height // 2
    top = center_y + box_height // 2

    # 배경 이미지 그리기 (투명도 적용 - composite_draw 사용)
    if quest_bg_image:
        quest_bg_image.composite_draw(0, ' ', center_x, center_y, 600, box_height)

    else:
        # 이미지가 없으면 3중 사각형으로 테두리 효과
        draw_rectangle(left, bottom, right, top)
        draw_rectangle(left + 2, bottom + 2, right - 2, top - 2)
        draw_rectangle(left + 4, bottom + 4, right - 4, top - 4)

    # 제목 그리기
    if font:
        title_text = "퀘스트 목록"
        title_color = (60, 40, 20)
        font.draw(center_x - 60, top - 40, title_text, title_color)

    # 퀘스트 목록 그리기 (활성화된 퀘스트만 표시)
    if quest_manager:
        quests = quest_manager.get_active_quests()  # 현재 활성화된 퀘스트만

        if len(quests) == 0:
            # 퀘스트가 없을 경우
            if font:
                no_quest_text = "사용 가능한 퀘스트가 없습니다"
                color = (60, 40, 20)
                font.draw(center_x - 80, center_y, no_quest_text, color)
        else:
            # 퀘스트 목록 표시
            start_y = top - 80
            quest_spacing = 130  # 간격을 넓힘 (description 추가로 인해)

            for i, quest in enumerate(quests):
                quest_y = start_y - (i * quest_spacing)

                # 퀘스트가 화면 밖으로 나가면 표시 중단
                if quest_y < bottom + 50:
                    break

                # 퀘스트 제목 및 설명
                if font:
                    # 완료된 퀘스트는 어두운 녹색, 진행중인 퀘스트는 진한 갈색
                    if quest.is_completed:
                        title_color = (40, 100, 40)  # 어두운 녹색 (양피지에 어울림)
                        desc_color = (50, 110, 50)
                        progress_color = (40, 100, 40)
                    else:
                        title_color = (60, 40, 20)  # 진한 갈색
                        desc_color = (90, 65, 40)  # 약간 연한 갈색
                        progress_color = (80, 55, 30)  # 약간 밝은 갈색

                    # 제목 그리기
                    font.draw(left + 30, quest_y, quest.title, title_color)

                    # Description 그리기 (제목 아래)
                    font.draw(left + 30, quest_y - 25, quest.description, desc_color)

                    # 진행도 그리기 (description 아래)
                    progress_text = f"진행도: {quest.get_progress_text()}"
                    font.draw(left + 30, quest_y - 50, progress_text, progress_color)

                # 구분선 그리기 (얇은 사각형으로 표현)
                if i < len(quests) - 1:
                    line_y = quest_y - 70
                    draw_rectangle(left + 20, line_y, right - 20, line_y + 1)
