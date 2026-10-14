"""The Player and Enemy classes."""

import random

from game_data import BOSSES, ENEMY_SCALING, ENEMY_TEMPLATES


class Player:
    def __init__(self, name):
        self.name = name
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = int(random.uniform(7, 10))
        self.inventory = []
        self.gold = 300
        self.defense = 1.0  # Damage taken = enemy attack / defense
        self.conditional_effects = []  # Item effects that only apply against certain enemies
        self.damage_dealt = 0  # Total damage dealt to enemies, which summons bosses
        self.bosses_beaten = 0

    def stat(self, name, enemy=None):
        """Return a stat's value, including bonuses that apply against this enemy."""
        value = getattr(self, name)
        if enemy:
            for effect in self.conditional_effects:
                if effect["stat"] == name and enemy.matches(effect["vs"]):
                    value += effect["amount"]
        return value

    def next_boss(self):
        """Return the next boss's data, or None once every boss is beaten."""
        if self.bosses_beaten < len(BOSSES):
            return BOSSES[self.bosses_beaten]
        return None

    def boss_ready(self):
        boss = self.next_boss()
        return boss is not None and self.damage_dealt >= boss["appears_at"]

    def enemy_scale(self):
        """How much stronger regular enemies are than their base stats."""
        return round(
            1
            + self.damage_dealt * ENEMY_SCALING["per_damage"]
            + self.bosses_beaten * ENEMY_SCALING["per_boss"],
            2,
        )


class Enemy:
    def __init__(self, name, hp, attack, gold=0, tags=(), drops=(), title=None, intro=None, death=None):
        self.name = name
        self.title = title or name  # Full name, shown when the enemy appears
        self.intro = intro  # Boss messages for when it appears and when it's defeated
        self.death = death
        self.hp = hp
        self.attack = random.randint(*attack)  # Rolled once per enemy
        self.gold = gold
        self.tags = set(tags)  # e.g. "boss", used to target item effects
        self.drops = list(drops)
        self.lulled = 0  # Attacks left that will probably miss (Ukulele)

    @classmethod
    def regular(cls, name, scale=1):
        data = ENEMY_TEMPLATES[name]
        low, high = data["attack"]
        return cls(
            name,
            round(data["hp"] * scale),
            (round(low * scale), round(high * scale)),
            round(data["gold"] * scale),
        )

    @classmethod
    def boss(cls, data):
        return cls(
            data["name"], data["hp"], data["attack"], data["gold"], data["tags"],
            data["drops"], data["title"], data["intro"], data["death"],
        )

    def matches(self, targets):
        return self.name in targets or bool(self.tags.intersection(targets))
