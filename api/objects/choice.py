class Choice:
    def __init__(self, choice_id, next_id, text, res_path, conditions, result):
        self.choice_id: str = choice_id
        self.next_id: str = next_id
        self.text: str = text
        self.res_path: str = res_path
        self.conditions: list = conditions
        self.result: str = result
