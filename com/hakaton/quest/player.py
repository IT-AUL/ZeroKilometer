import random


class Player:
    def __init__(self):
        self.changed_location = False
        self.npc = ""
        self.health = 50
        self.name = "Алмаз"
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
        self.damage = 25
        self.damage_spread = 5
        self.armor = 12
        self.deck = []
        self.will_fight = 1
        self.changed = False

    def apply_changes(self, health=0, items=None, clear="False", will_fight=1):
        if clear == "True":
            self.items = list(filter(lambda x: x['type'] == "ally", self.items))
        if items is None:
            items = []
        if self.will_fight == 1:
            self.will_fight = will_fight
        self.health += health
        for it in items:
            if not any((i['id'] == it['id'] and i['type'] == 'ally') for i in self.items):
                self.items.extend(items)
        print(self.items)

    def attack(self, enemy):
        enemy.health -= random.randrange(self.damage - self.damage_spread, self.damage + self.damage_spread)

    def defense(self, enemy):
        self.health -= max(
            random.randrange(enemy.damage - enemy.damage_spread, enemy.damage + enemy.damage_spread) - self.armor, 0)
