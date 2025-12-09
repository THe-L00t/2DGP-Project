"""
퀘스트 시스템 - 몬스터 처치 퀘스트 관리
"""

class Quest:
    """단일 퀘스트 클래스"""
    def __init__(self, quest_id, title, description, target_monster, target_count):
        self.quest_id = quest_id          # 퀘스트 고유 ID
        self.title = title                # 퀘스트 제목
        self.description = description    # 퀘스트 설명
        self.target_monster = target_monster  # 목표 몬스터 ("Gnome", "Paddlefish", "Panda")
        self.target_count = target_count  # 목표 수량
        self.current_count = 0            # 현재 진행도
        self.is_completed = False         # 완료 여부
        self.is_active = False            # 활성화 여부 (순차 진행용)

    def add_progress(self, amount=1):
        """진행도 추가"""
        if not self.is_completed:
            self.current_count += amount
            if self.current_count >= self.target_count:
                self.current_count = self.target_count
                self.is_completed = True
                print(f"[QUEST] '{self.title}' 완료!")
                return True
        return False

    def get_progress_text(self):
        """진행도 텍스트 반환"""
        if self.is_completed:
            return "완료"
        return f"{self.current_count}/{self.target_count}"

    def reset(self):
        """퀘스트 초기화"""
        self.current_count = 0
        self.is_completed = False


class QuestManager:
    """퀘스트 관리자 클래스"""
    def __init__(self):
        self.quests = []  # 모든 퀘스트 목록 (순서대로)

    def add_quest(self, quest):
        """퀘스트 추가 (순서대로 추가해야 함)"""
        self.quests.append(quest)
        # 첫 번째 퀘스트는 자동으로 활성화
        if len(self.quests) == 1:
            quest.is_active = True
            print(f"[QUEST] 새 퀘스트 활성화: {quest.title}")
        else:
            print(f"[QUEST] 퀘스트 대기중: {quest.title}")

    def remove_quest(self, quest_id):
        """퀘스트 제거"""
        self.quests = [q for q in self.quests if q.quest_id != quest_id]

    def get_quest_by_id(self, quest_id):
        """ID로 퀘스트 찾기"""
        for quest in self.quests:
            if quest.quest_id == quest_id:
                return quest
        return None

    def get_active_quests(self):
        """활성화된 퀘스트만 반환 (현재 진행 가능한 퀘스트)"""
        return [q for q in self.quests if q.is_active]

    def get_completed_quests(self):
        """완료된 퀘스트만 반환"""
        return [q for q in self.quests if q.is_completed]

    def get_all_quests(self):
        """모든 퀘스트 반환"""
        return self.quests

    def on_monster_killed(self, monster_name):
        """몬스터 처치 시 호출 - 해당 몬스터를 목표로 하는 활성화된 퀘스트 진행도 증가"""
        for i, quest in enumerate(self.quests):
            # 활성화된 퀘스트이고, 목표 몬스터가 맞고, 완료되지 않았으면
            if quest.is_active and quest.target_monster == monster_name and not quest.is_completed:
                completed = quest.add_progress(1)
                print(f"[QUEST] '{quest.title}' 진행도: {quest.get_progress_text()}")

                # 퀘스트 완료 시 다음 퀘스트 활성화
                if completed:
                    quest.is_active = False  # 현재 퀘스트 비활성화
                    # 다음 퀘스트 활성화
                    if i + 1 < len(self.quests):
                        next_quest = self.quests[i + 1]
                        next_quest.is_active = True
                        print(f"[QUEST] 새 퀘스트 활성화: {next_quest.title}")
                    else:
                        print(f"[QUEST] 모든 퀘스트 완료!")

    def check_quest_completion(self):
        """모든 퀘스트 완료 확인"""
        return all(q.is_completed for q in self.quests)

    def get_quest_count(self):
        """퀘스트 개수 반환"""
        return len(self.quests)

    def get_active_quest_count(self):
        """진행중인 퀘스트 개수 반환"""
        return len(self.get_active_quests())

    def get_completed_quest_count(self):
        """완료된 퀘스트 개수 반환"""
        return len(self.get_completed_quests())
