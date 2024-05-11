import random


class Player:
    def __init__(self):
        self.changed_location = False
        self.health = 50
        self.name = "Алмаз"
        self.items = []
        self.damage = 25
        self.damage_spread = 5
        self.armor = 12

    def apply_changes(self, health=0, items=None):
        """
        Apply changes to the player's health and stats
        :param health: How much to increase the health of the player
        :param items: List of items to add to the player's items
        :return: None
        """
        if items is None:
            items = []
        self.health += health
        self.items.extend(items)

    def attack(self, enemy):
        enemy.health -= random.randrange(self.damage - self.damage_spread, self.damage + self.damage_spread)

    def defense(self, enemy):
        self.health -= max(
            random.randrange(enemy.damage - enemy.damage_spread, enemy.damage + enemy.damage_spread) - self.armor, 0)
