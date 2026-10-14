"""The Player and Enemy classes."""

import random

from game_data import BOSSES, ENEMY_TEMPLATES, SCALING


class Player:
    def __init__(self, name):
        self.name = name
        # Base HP and attack grow with the world's strength (see SCALING).
        # Bonuses from items and wins are added on top.
        self.base_max_hp = 100
        self.base_attack = int(random.uniform(7, 10))
        self.max_hp_bonus = 0
        self.attack_bonus = 0
        self.damage_dealt = 0  # Total damage dealt to enemies, which summons bosses
        self.bosses_beaten = 0
        self.current_boss = None  # A boss you ran from, which keeps its HP and attack
        self.location = "village"  # Key in ROOMS; decides which enemies you meet
        self.hp = self.max_hp
        self.inventory = []
        self.gold = 300
        self.defense = 1.0  # Damage taken = enemy attack / defense
        self.conditional_effects = []  # Item effects that only apply against certain enemies

    @property
    def max_hp(self):
        return round(self.base_max_hp * self.scale()) + self.max_hp_bonus

    @max_hp.setter
    def max_hp(self, value):  # e.g. player.max_hp += 25 adds 25 to the bonus
        self.max_hp_bonus += value - self.max_hp

    @property
    def attack(self):
        return round(self.base_attack * self.scale()) + self.attack_bonus

    @attack.setter
    def attack(self, value):
        self.attack_bonus += value - self.attack

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

    def scale(self):
        """How much stronger regular enemies, and your base HP and attack, are than at the start."""
        return round(
            min(
                SCALING["max"],
                1
                + self.damage_dealt * SCALING["per_damage"]
                + self.bosses_beaten * SCALING["per_boss"],
            ),
            2,
        )


class Enemy:
    def __init__(self, name, hp, attack, gold=0, tags=(), drops=(), title=None, intro=None, death=None):
        self.name = name
        self.title = title or name  # Full name, shown when the enemy appears
        self.intro = intro  # Boss messages for when it appears and when it's defeated
        self.death = death
        self.hp = self.max_hp = hp
        self.attack = random.randint(*attack)  # Rolled once per enemy
        self.gold = gold
        self.tags = set(tags)  # e.g. "boss", used to target item effects
        self.drops = list(drops)
        self.lulled = 0  # Attacks left that may miss (Ukulele), each with miss_chance
        self.miss_chance = 0

    @classmethod
    def regular(cls, name, scale=1):
        return cls.scaled(name, ENEMY_TEMPLATES[name], scale)

    @classmethod
    def boss(cls, data, scale=1):
        return cls.scaled(
            data["name"], data, scale, data["tags"], data["drops"],
            data["title"], data["intro"], data["death"],
        )

    @classmethod
    def scaled(cls, name, data, scale, *extra):
        """Build an enemy with its HP and attack multiplied by scale."""
        low, high = data["attack"]
        return cls(
            name,
            round(data["hp"] * scale),
            (round(low * scale), round(high * scale)),
            data["gold"],
            *extra,
        )

    def matches(self, targets):
        return self.name in targets or bool(self.tags.intersection(targets))
