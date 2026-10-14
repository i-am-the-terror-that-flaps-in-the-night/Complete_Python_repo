# === Imports ===
import random
import sys
import time


# === Setup ===
def type_slow(text, delay=0.02):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# === Global Game Data ===

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


# === Classes ===
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


# === Items and Shop ===
def obtain_item(player, key):
    """Apply an item's permanent effects, and keep it if it can be used in fights."""
    item_data = ITEMS[key]
    apply_effects(player, item_data)
    if "use" in item_data:
        player.inventory.append(key)


def apply_effects(player, item_data):
    for effect in item_data.get("effects", []):
        stat, amount = effect["stat"], effect["amount"]

        if "vs" in effect:
            player.conditional_effects.append(effect)
            type_slow(
                f"Your {stat} increased by {amount} against {', '.join(effect['vs'])}.",
                0.05,
            )
            continue

        new_value = getattr(player, stat) + amount
        setattr(
            player,
            stat,
            round(new_value, 2) if isinstance(new_value, float) else new_value,
        )
        if stat == "max_hp":
            player.hp = min(player.max_hp, player.hp + amount)  # Heal up to max_hp
        type_slow(f"Your {stat} increased by {amount}.", 0.05)


def shop(player):
    type_slow("\nWelcome to the Shop! What are you looking for?", 0.05)
    options = [key for key, item in ITEMS.items() if "cost" in item]

    while True:
        type_slow(
            f"\nYou have {player.gold} gold. Your Max HP is {player.max_hp}.", 0.05
        )
        type_slow("--- Inventory ---", 0.02)

        for i, key in enumerate(options):
            item = ITEMS[key]
            display_line = f"[{i + 1}] {item['name']} ({item['effect_description']}) - {item['cost']} Gold"
            type_slow(display_line, 0.01)

        type_slow("[L]eave shop", 0.05)

        choice = (
            input("Enter the number of the item you want, or [L] to leave: ")
            .lower()
            .strip()
        )

        if choice == "l":
            type_slow("Thank you for stopping by! Come again soon.", 0.05)
            return

        try:
            item_index = int(choice) - 1
            if 0 <= item_index < len(options):
                item_key = options[item_index]
                item_data = ITEMS[item_key]
            else:
                type_slow(
                    "Invalid selection. Please enter a valid number or 'L'.", 0.05
                )
                continue
        except ValueError:
            type_slow("Invalid selection. Please enter a valid number or 'L'.", 0.05)
            continue

        cost = item_data["cost"]
        if player.gold >= cost:
            player.gold -= cost
            type_slow(f"You bought a {item_data['name']} for {cost} gold!", 0.05)
            obtain_item(player, item_key)

        else:
            type_slow("You don't have enough gold for that!", 0.05)


# === Combat ===
def deal_damage(player, enemy, damage):
    player.damage_dealt += min(damage, enemy.hp)  # Overkill doesn't count toward bosses
    enemy.hp -= damage
    type_slow(f"{player.name} did {damage} damage to {enemy.name}", 0.05)
    type_slow(f"{enemy.name}'s hp is {max(0, enemy.hp)}")  # Display 0 instead of negative


def use_item(player, enemy):
    """Let the player use an inventory item. Returns True if a turn was spent."""
    for i, key in enumerate(player.inventory):
        type_slow(f"[{i + 1}] {ITEMS[key]['name']}", 0.01)

    choice = input("Enter the number of the item you want to use: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(player.inventory):
        type_slow("Invalid selection.", 0.05)
        return False

    key = player.inventory[int(choice) - 1]
    item_data = ITEMS[key]
    use = item_data["use"]
    if "vs" in use and not enemy.matches(use["vs"]):
        type_slow(f"The {item_data['name']} has no effect on {enemy.name}.", 0.05)
        return False

    type_slow(f"{player.name} used the {item_data['name']}!", 0.05)

    if "heal" in use:
        healed = min(use["heal"], player.max_hp - player.hp)
        player.hp += healed
        type_slow(
            f"{player.name} restored {healed} HP. HP is now {player.hp}/{player.max_hp}",
            0.05,
        )
    if "damage" in use:
        deal_damage(player, enemy, use["damage"])
    if "lull" in use:
        enemy.lulled += use["lull"]
        type_slow(f"{enemy.name} looks drowsy...", 0.05)

    if use.get("consume", True):
        player.inventory.remove(key)
    return True


def enemy_turn(player, enemy):
    if enemy.lulled > 0:
        enemy.lulled -= 1
        if random.random() < 7 / 8:
            type_slow(f"{enemy.name} is lost in the music and misses!\n", 0.05)
            return

    damage = round(enemy.attack / player.stat("defense", enemy))
    player.hp -= damage
    type_slow(f"{enemy.name} did {damage} damage to {player.name}", 0.1)
    type_slow(f"{player.name}'s hp is {max(0, player.hp)}\n")


def handle_victory(player, enemy):
    if enemy.death:
        type_slow(f"\n{enemy.death}\n", 0.04)
    player.attack += 2
    player.hp = min(player.max_hp, player.hp + 10)
    player.gold += enemy.gold
    type_slow(
        f"{enemy.name} is defeated! You gained 2 attack, restored 10 HP, and found {enemy.gold} gold.",
        0.05,
    )
    for key in enemy.drops:
        type_slow(f"{enemy.name} dropped a {ITEMS[key]['name']}!", 0.05)
        obtain_item(player, key)

    if "boss" in enemy.tags:
        player.bosses_beaten += 1
    if "final" in enemy.tags:
        win_game(player)


def win_game(player):
    type_slow(f"\n*** {player.name} has defeated the final boss! YOU WIN! ***\n", 0.1)
    if input("Keep playing? (y/n) ").lower().strip() != "y":
        sys.exit()


def spawn_enemy(player, enemy_names):
    """Summon the next boss if it's ready, otherwise a random regular enemy."""
    if player.boss_ready():
        enemy = Enemy.boss(player.next_boss())
        type_slow(f"\n{enemy.intro}\n", 0.04)
        type_slow(f"{enemy.title} appears!", 0.05)
    else:
        enemy = Enemy.regular(random.choice(enemy_names), player.enemy_scale())
        type_slow(f"A vicious {enemy.name} appears! ({enemy.hp} HP, {enemy.attack} attack)", 0.05)
    return enemy


def fight(player, enemy):
    type_slow(f"\n--- Start of Fight: {player.name} vs {enemy.name} ---", 0.05)

    while player.hp > 0 and enemy.hp > 0:
        player_attack_choice = (
            input("Do you want to attack[A], use an item[I], or run[R]?\n")
            .lower()
            .strip()
        )

        # Flag to skip enemy turn if player uses an invalid item
        action_performed = False

        if player_attack_choice == "a":
            deal_damage(player, enemy, player.stat("attack", enemy))
            action_performed = True

        elif player_attack_choice == "i":
            if not player.inventory:
                type_slow("Your inventory is empty! You panic and waste a turn.", 0.05)
                action_performed = True  # Enemy still gets a turn
            else:
                action_performed = use_item(player, enemy)

        elif player_attack_choice == "r":
            type_slow("You ran away!", 0.05)
            if "boss" in enemy.tags:
                type_slow(f"{enemy.name} will be waiting for you...", 0.05)
            return

        else:
            type_slow("Invalid choice. Enter 'A', 'I' or 'R'. Wasting a turn...", 0.05)
            action_performed = True

        # Check for Victory
        if enemy.hp <= 0:
            handle_victory(player, enemy)
            return

        if action_performed:
            enemy_turn(player, enemy)

        # Check for Defeat (Must happen after the enemy attacks)
        if player.hp <= 0:
            type_slow(f"{player.name}'s hp is 0! \n----- KO -----\n", 0.2)
            sys.exit()


# === Exploring ===
def choose_room():
    areas = ", ".join(f"{name} ({room['type']})" for name, room in ROOMS.items())
    type_slow(f"Areas: {areas}", 0.02)
    while True:
        choice = input("Enter an area: ").strip().lower()
        if choice in ROOMS:
            return choice
        type_slow("That area doesn't exist.", 0.05)


def find_item(player):
    found = random.choices(list(FIND_POOL), weights=list(FIND_POOL.values()))[0]
    if found == "gold":
        amount = random.randint(10, 30)
        player.gold += amount
        type_slow(f"✨ You found {amount} gold!", 0.05)
    else:
        type_slow(f"✨ You found a {ITEMS[found]['name']}!", 0.05)
        obtain_item(player, found)


def explore(player):
    room = ROOMS[choose_room()]

    # Decide if something happens in the room, based on the room's odds.
    # A boss that's ready always finds you.
    found_item = random.random() < room["chance_of_item"]
    met_enemy = player.boss_ready() or random.random() < room["chance_of_enemy"]

    if found_item:
        find_item(player)
    if met_enemy:
        fight(player, spawn_enemy(player, room["enemies"]))
    if not found_item and not met_enemy:
        type_slow("The area is quiet. Nothing here.", 0.05)


# === Main Loop ===
def show_status(player):
    type_slow("-" * 30)
    item_names = [ITEMS[key]["name"] for key in player.inventory]
    type_slow(
        f"Your health: {player.hp}/{player.max_hp} \nYour attack: {player.attack} \nYour defense: {player.defense} \nYour items: {item_names} \nYour gold: {player.gold} \nDamage dealt: {player.damage_dealt} \nEnemy strength: x{player.enemy_scale()}",
        0.02,
    )

    boss = player.next_boss()
    if player.boss_ready():
        type_slow(f"⚠ {boss['name']} is hunting you! Your next fight will be against it.", 0.02)
    elif boss:
        type_slow(f"{boss['name']} appears at {boss['appears_at']} damage dealt.", 0.02)


def main():
    player = Player(input("Enter your name: "))
    while True:
        show_status(player)

        player_choice = (
            input("\nYour options are: \n[F]ight \n[E]xplore \n[S]hop \n[R]est \n[Q]uit \n")
            .lower()
            .strip()
        )

        if player_choice == "f":
            fight(player, spawn_enemy(player, list(ENEMY_TEMPLATES)))

        elif player_choice == "e":
            explore(player)

        elif player_choice == "s":
            shop(player)

        elif player_choice == "r":
            type_slow("Resting... \nResting...\nResting... \n\n", 0.35)
            type_slow(
                f"{player.name} has rested! \nYour HP is now at {player.max_hp}!", 0.05
            )
            player.hp = player.max_hp
        elif player_choice == "q":
            quit_choice = input("Do you wish to quit the game (y/n)?").lower().strip()
            if quit_choice == "y":
                sys.exit()
        else:
            type_slow("Invalid choice. Try again.", 0.05)


if __name__ == "__main__":
    main()
