"""Fights, item use in fights, rewards and boss spawning."""

import random
import sys

from entities import Enemy
from game_data import ITEMS
from items import obtain_item
from ui import type_slow


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
