# === Imports ===
import random, time, sys

# === Setup ===
def type_slow(text, delay=0.02):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# === Global Game Data ===

SHOP_INVENTORY = {
    "potion": {
        "name": "Health Potion",
        "effect_description": "Restores 40 HP.",
        "cost": 50,
        "type": "heal",
        "heal_amount": 40
    },
    "knuckles": {
        "name": "Brass Knuckles",
        "effect_description": "Permanently increases Attack by 5.",
        "cost": 150,
        "type": "upgrade",
        "stat_boost": "attack",
        "boost_amount": 10
    },
    "amulet": {
        "name": "Mystic Amulet",
        "effect_description": "Permanently increases Max HP by 25.",
        "cost": 100,
        "type": "upgrade",
        "stat_boost": "max_hp",
        "boost_amount": 25
    }
}

# CRITICAL FIX 1: Defined enemy templates as a list of TUPLES/LISTS of parameters
ENEMY_TEMPLATES = [
    ("Gremlin", 30, int(random.uniform(3, 5))), # Name, HP, Attack
    ("Goblin", 75, 6),
    ("Orc", 90, int(random.uniform(5, 8)))
]
FINAL_BOSS = [
    ("Tharnoth the Inevitable, Bootleg Thanos out of Bilbo Baggins's pantry!", 250, int(random.uniform(30, 50)))
]

# === Classes ===
class Player:
    def __init__(self, name):
        self.name = name
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = int(random.uniform(7, 10))
        self.inventory = []
        self.gold = 300

class Enemy:
    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack


# === Game Logic ===

def shop(player):
    type_slow("\nWelcome to the Shop! What are you looking for?", 0.05)

    while True:
        type_slow(f"\nYou have {player.gold} gold. Your Max HP is {player.max_hp}.", 0.05)
        type_slow("--- Inventory ---", 0.02)

        options = []
        for i, (key, item) in enumerate(SHOP_INVENTORY.items()):
            display_line = f"[{i+1}] {item['name']} ({item['effect_description']}) - {item['cost']} Gold"
            type_slow(display_line, 0.01)
            options.append(key)

        type_slow("[L]eave shop", 0.05)

        choice = input("Enter the number of the item you want, or [L] to leave: ").lower().strip()

        if choice == 'l':
            type_slow("Thank you for stopping by! Come again soon.", 0.05)
            return

        try:
            item_index = int(choice) - 1
            if 0 <= item_index < len(options):
                item_key = options[item_index]
                item_data = SHOP_INVENTORY[item_key]
            else:
                type_slow("Invalid selection. Please enter a valid number or 'L'.", 0.05)
                continue
        except ValueError:
            type_slow("Invalid selection. Please enter a valid number or 'L'.", 0.05)
            continue

        cost = item_data['cost']
        if player.gold >= cost:
            player.gold -= cost
            type_slow(f"You bought a {item_data['name']} for {cost} gold!", 0.05)

            if item_data['type'] == 'heal':
                player.inventory.append(item_data['name'])

            elif item_data['type'] == 'upgrade':
                stat = item_data['stat_boost']
                amount = item_data['boost_amount']

                if stat == 'attack':
                    player.attack += amount
                elif stat == 'max_hp':
                    player.max_hp += amount
                    player.hp = min(player.max_hp, player.hp + amount) # Heal up to max_hp

                type_slow(f"Your {stat} increased by {amount}.", 0.05)

        else:
            type_slow("You don't have enough gold for that!", 0.05)


def fight(player, enemy):
    type_slow(f"\n--- Start of Fight: {player.name} vs {enemy.name} ---", 0.05)

    while player.hp > 0 and enemy.hp > 0:
        player_attack_choice = input("Do you want to attack[A] or use an item[I]?\n").lower().strip()

        # Flag to skip enemy turn if player wins or uses an invalid move
        action_performed = False

        if player_attack_choice == "a":
            # Player's Turn
            enemy.hp -= player.attack
            type_slow(f"{player.name} did {player.attack} damage to {enemy.name}", 0.05)
            type_slow(f"{enemy.name}'s hp is {max(0, enemy.hp)}") # Display 0 instead of negative

            action_performed = True

            # Check for Victory
            if enemy.hp <= 0:
                player.attack += 2
                player.hp = min(player.max_hp, player.hp + 10)
                # CRITICAL FIX 3: Give gold reward
                gold_reward = 0
                if enemy == "Orc":
                    gold_reward = 75
                elif enemy == "Goblin":
                    gold_reward = 50
                else:
                    gold_reward = 25
                player.gold += gold_reward
                type_slow(f"{enemy.name} is defeated! You gained 2 attack, restored 10 HP, and found {gold_reward} gold.", 0.05)
                return # Exit the function

        elif player_attack_choice == "i":
            if not player.inventory:
                type_slow("Your inventory is empty! You panic and waste a turn.", 0.05)
        action_performed = True # Enemy still gets a turn
        player_item_choice = input(f"Your items are: {player.inventory}. \n What item do you want to use?").strip().lower()
        if player_item_choice == "potion":
            player.hp += 40
            player.inventory.remove("potion")
            if player.hp > player.max_hp:
                player.hp = player.max_hp
        elif player_item_choice == "knuckles":
            player.attack += 10
            player.inventory.remove("knuckles")
        elif player_item_choice == "amulet":
            player.max_hp += 25
            player.inventory.remove("amulet")
        elif player_item_choice == "mana vial":
            print("")

            action_performed = False

        else:
            type_slow("Invalid choice. Enter 'A' or 'I'. Wasting a turn...", 0.05)
            action_performed = True

        # CRITICAL FIX 2: Enemy's Turn is now separate from the player's 'A' choice
        if player.hp > 0 and action_performed:
            # Enemy's Turn
            player.hp -= enemy.attack
            type_slow(f"{enemy.name} did {enemy.attack} damage to {player.name}", 0.1)
            type_slow(f"{player.name}'s hp is {max(0, player.hp)}\n")

        # Check for Defeat (Must happen after the enemy attacks)
        if player.hp <= 0:
            type_slow(f"{player.name}'s hp is 0! \n----- KO -----\n", 0.2)
            sys.exit()


# === Main Loop ===
def main():
    player = Player(input("Enter your name: "))
    while True:
        # Display Status
        type_slow("-" * 30)
        type_slow(f"Your health: {player.hp}/{player.max_hp} \nYour attack: {player.attack} \nYour items: {player.inventory} \nYour gold: {player.gold}", 0.02)

        player_choice = input(f"\nYour options are: \n[F]ight \n[S]hop \n[R]est \n[Q]uit \n").lower().strip()

        if player_choice == "f":
            # CRITICAL FIX 1: Correctly instantiate a new enemy object every time
            enemy_params = random.choice(ENEMY_TEMPLATES)
            selected_enemy = Enemy(enemy_params[0], enemy_params[1], enemy_params[2])

            type_slow(f"A wild {selected_enemy.name} appears!", 0.05)
            fight(player, selected_enemy)

        elif player_choice == "s":
            shop(player)

        elif player_choice == "r":
            type_slow(f"Resting... \nResting...\nResting... \n\n", 0.35)
            type_slow(f"{player.name} has rested! \nYour HP is now at {player.max_hp}!", 0.05)
            player.hp = player.max_hp
        elif player_choice == "q":
            quit_choice = input("Do you wish to quit the game (y/n)?").lower().strip()
            if quit_choice == "y":
                sys.exit()
        else:
            type_slow("Invalid choice. Try again.", 0.05)


if __name__ == "__main__":
    main()
