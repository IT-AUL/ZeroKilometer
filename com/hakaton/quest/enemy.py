import random


class Enemy:
    def __init__(self, health, damage, damage_spread, armor):
        self.health = health
        self.damage = damage
        self.damage_spread = damage_spread
        self.armor = armor

    def attack(self, player):
        player.health -= random.randrange(self.damage - self.damage_spread, self.damage + self.damage_spread)

    def defense(self, player):
        self.health -= max(
            random.randrange(player.damage - player.damage_spread, player.damage + player.damage_spread) - self.armor,
            0)

    def analyze(self, player):
        if player.health <= self.health:
            self.attack(player)
        else:
            self.defense(player)
