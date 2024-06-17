class Player:
    def __init__(self):
        self.changed_location = False
        self.npc = ""
        self.name = "Булат"
        self.items = [{
            "name": "Булат",
            "id": "1",
            "type": "ally"
        }, {
            "name": "Тычкан",
            "id": "13",
            "type": "ally"
        }, {
            "name": "Бака",
            "id": "14",
            "type": "ally"
        }]
        self.deck = []
        self.will_fight = 1
        self.changed = False

    def apply_changes(self, items=None, clear="False", will_fight=1):
        if clear == "True":
            self.items = list(filter(lambda x: x['type'] == "ally", self.items))
        if items is None:
            items = []
        if self.will_fight == 1:
            self.will_fight = will_fight
        for it in items:
            if not any((i['id'] == it['id'] and i['type'] == 'ally') for i in self.items):
                self.items.extend(items)
