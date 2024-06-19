class Quest:
    def __init__(self, quest_id, description, choices):
        self.quest_id: str = quest_id
        self.description: str = description
        self.choices: list = choices
