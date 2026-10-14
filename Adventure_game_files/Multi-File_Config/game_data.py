"""Items, enemies, bosses and areas. Add new content here."""


# Item fields:
#   "cost": shop price. Items without a cost aren't sold (e.g. boss drops).
#   "effects": permanent stat changes applied when the item is obtained. Each is
#       {"stat": <Player attribute>, "amount": <number>}. An item can list several.
#       Add "vs": [enemy names or tags] to make the effect only apply in fights
#       against those enemies, e.g. {"stat": "attack", "amount": 20, "vs": ["boss"]}.
#       A brand new stat only needs a default value in Player.__init__.
#   "use": makes the item usable from the inventory during a fight.
#       {"heal": HP restored, "damage": damage to the enemy,
#        "lull": the enemy's next N attacks each have a 7 in 8 chance to miss,
#        "vs": [enemy names or tags] the item only works against,
#        "consume": removed after use (default True)}
ITEMS = {
    "potion": {
        "name": "Health Potion",
        "effect_description": "Restores 40 HP.",
        "cost": 70,
        "use": {"heal": 40, "consume": True},
    },
    "knuckles": {
        "name": "Brass Knuckles",
        "effect_description": "Permanently increases Attack by 10.",
        "cost": 125,
        "effects": [{"stat": "attack", "amount": 10}],
    },
    "amulet": {
        "name": "Mystic Amulet",
        "effect_description": "Permanently increases Max HP by 25.",
        "cost": 120,
        "effects": [{"stat": "max_hp", "amount": 25}],
    },
    "refrigerator": {
        "name": "Refrigerator Door",
        "effect_description": "Permanently increases Attack by 10 and Defense by 0.2. Use in a fight to deal 50 damage (single use).",
        "cost": 150,
        "effects": [
            {"stat": "attack", "amount": 10},
            {"stat": "defense", "amount": 0.2},
        ],
        "use": {"damage": 50, "consume": True},
    },
    "quality_control": {
        "name": "Quality Control",
        "effect_description": "Calls the patent office on any cheap ripoffs. Deals 100 damage to a bootleg boss (single use).",
        "cost": 150,
        "use": {"damage": 100, "vs": ["ripoff"], "consume": True},
    },
    "sword": {
        "name": "Sword",
        "effect_description": "Permanently increases Attack by 5.",
        "cost": 60,
        "effects": [{"stat": "attack", "amount": 5}],
    },
    "shield": {
        "name": "Shield",
        "effect_description": "Permanently increases Defense by 0.1.",
        "cost": 60,
        "effects": [{"stat": "defense", "amount": 0.1}],
    },
    "spear": {
        "name": "Spear",
        "effect_description": "Permanently increases Attack by 15 against Orcs and bosses.",
        "cost": 90,
        "effects": [{"stat": "attack", "amount": 15, "vs": ["Orc", "boss"]}],
    },
    "ukulele": {
        "name": "Ukulele",
        "effect_description": "Lulls an enemy: its next 2 attacks each have a 7 in 8 chance to miss (single use).",
        "cost": 80,
        "use": {"lull": 2, "consume": True},
    },
    # Boss drops (not sold in the shop)
    "godzilla_scale": {
        "name": "Godzilla Scale",
        "effect_description": "Permanently increases Defense by 0.3 and Max HP by 30.",
        "effects": [
            {"stat": "defense", "amount": 0.3},
            {"stat": "max_hp", "amount": 30},
        ],
    },
    "kaiju_tooth": {
        "name": "Kaiju Tooth",
        "effect_description": "Permanently increases Attack by 25 against Tharnoth.",
        "effects": [{"stat": "attack", "amount": 25, "vs": ["tharnoth"]}],
    },
    "atomic_breath_mint": {
        "name": "Atomic Breath Mint",
        "effect_description": "Deals 120 damage to an enemy (single use).",
        "use": {"damage": 120, "consume": True},
    },
    "infinity_oven_mitt": {
        "name": "Infinity Oven Mitt",
        "effect_description": "Permanently increases Attack by 25 and Defense by 0.5.",
        "effects": [
            {"stat": "attack", "amount": 25},
            {"stat": "defense", "amount": 0.5},
        ],
    },
}

# Random finds while exploring: item key (or "gold") -> how likely it is
FIND_POOL = {"gold": 5, "potion": 3, "sword": 1, "shield": 1}

# Name -> HP, attack range (rolled when the enemy appears), gold reward
ENEMY_TEMPLATES = {
    "Gremlin": {"hp": 30, "attack": (3, 5), "gold": 25},
    "Goblin": {"hp": 75, "attack": (6, 6), "gold": 50},
    "Orc": {"hp": 90, "attack": (5, 8), "gold": 75},
}

# Regular enemies get stronger as you progress: their HP, attack and gold are
# multiplied by 1 + (damage dealt x per_damage) + (bosses beaten x per_boss).
ENEMY_SCALING = {"per_damage": 0.001, "per_boss": 0.75}

# Bosses appear in this order, each once the player's total damage dealt to
# enemies reaches "appears_at". Beating the boss tagged "final" wins the game.
# "drops" are item keys from ITEMS. "intro" is shown when the boss appears and
# "death" when it's defeated.
BOSSES = [
    {
        "name": "Demigodzilla",
        "title": "Our Holy Lord and Savior, Demigodzilla, TEMU Godzilla from The Halls of the Mountain King!",
        "hp": 250,
        "attack": (30, 55),
        "gold": 250,
        "tags": ("boss", "ripoff"),
        "appears_at": 400,
        "drops": ["godzilla_scale", "kaiju_tooth", "atomic_breath_mint"],
        "intro": "The ground rumbles. A slightly off-key roar echoes out of the Halls of the Mountain King.\n"
                 "Something enormous stomps into view, still wearing a shipping label that reads 'GODZILA (GENUINE)'.",
        "death": "Demigodzilla topples over with the squeak of a cheap rubber toy.\n"
                 "A return label flutters down from the sky: 'Item not as described.'",
    },
    {
        "name": "Tharnoth",
        "title": "Tharnoth the Inevitable, Bootleg Thanos from Bilbo Baggins's pantry!",
        "hp": 375,
        "attack": (40, 75),
        "gold": 500,
        "tags": ("boss", "ripoff", "tharnoth", "final"),
        "appears_at": 1000,
        "drops": ["infinity_oven_mitt"],
        "intro": "A pantry door creaks open somewhere far too close. Tharnoth steps out and snaps his fingers.\n"
                 "Nothing happens. He snaps them again, harder, and adjusts a gauntlet made of tinfoil.\n"
                 "'I... am... inevitable.'",
        "death": "Tharnoth looks down at his crumbling hands. 'I don't feel so good...'\n"
                 "He drifts away as a fine dust that smells faintly of expired cereal.",
    },
]

ROOMS = {
    "village": {"type": "safe", "chance_of_enemy": 0.1, "chance_of_item": 0.7, "enemies": ["Gremlin"]},
    "forest": {"type": "wild", "chance_of_enemy": 0.5, "chance_of_item": 0.875, "enemies": ["Gremlin", "Goblin"]},
    "cave": {"type": "dangerous", "chance_of_enemy": 0.8, "chance_of_item": 0.4, "enemies": ["Goblin", "Orc"]},
    "castle": {"type": "fatal", "chance_of_enemy": 1, "chance_of_item": 0.1, "enemies": ["Orc"]},
}
