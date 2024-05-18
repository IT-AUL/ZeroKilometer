class Choice:
    def __init__(self, choice_id, to_quest, text, video_path, conditions, result):
        self.choice_id: str = choice_id
        self.to_quest: str = to_quest
        self.text: str = text
        self.video_path = video_path
        self.conditions = conditions
        self.result: str = result
