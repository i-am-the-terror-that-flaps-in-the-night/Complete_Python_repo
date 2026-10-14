"""
This game is still in progress and will have bugs and non-functionality.
Run this file to play.
"""

import random
import sys
import time

from Combat_logic import fight, spawn_enemy
from entities import Player
from game_data import FIND_POOL, ITEMS, REST_HP_PER_SECOND, ROOMS, SCALING
from items import obtain_item, shop
from ui import type_slow


def choose_room():
    areas = ", ".join(f"{name} ({room['type']}, enemies x{room['strength']})" for name, room in ROOMS.items())
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
    player.location = choose_room()
    room = ROOMS[player.location]
    type_slow(f"You travel to the {player.location}.", 0.05)

    # Decide if something happens in the room, based on the room's odds.
    # A boss that's ready always finds you.
    found_item = random.random() < room["chance_of_item"]
    met_enemy = player.boss_ready() or random.random() < room["chance_of_enemy"]

    if found_item:
        find_item(player)
    if met_enemy:
        fight(player, spawn_enemy(player, player.location))
    if not found_item and not met_enemy:
        type_slow("The area is quiet. Nothing here.", 0.05)


def show_status(player):
    type_slow("-" * 30)
    item_names = [ITEMS[key]["name"] for key in player.inventory]
    type_slow(
        f"Location: {player.location} ({ROOMS[player.location]['type']}) \nYour health: {player.hp}/{player.max_hp} \nYour attack: {player.attack} \nYour defense: {player.defense} \nYour items: {item_names} \nYour gold: {player.gold} \nDamage dealt: {player.damage_dealt} \nWorld strength: x{player.scale()} (enemies, plus your base HP and attack)",
        0.02,
    )

    boss = player.next_boss()
    if player.boss_ready():
        type_slow(f"⚠ {boss['name']} is hunting you! Your next fight will be against it.", 0.02)
    elif boss:
        type_slow(f"{boss['name']} appears at {boss['appears_at']} damage dealt.", 0.02)
    else:
        type_slow(f"Every boss is defeated. You've won! Enemies keep coming, up to x{SCALING['max']} strength.", 0.02)


def rest_time(player):
    """Seconds it takes to rest back to full HP."""
    return round((player.max_hp - player.hp) / REST_HP_PER_SECOND, 1)


def rest(player):
    healed = player.max_hp - player.hp
    if healed <= 0:
        type_slow("You're already at full health.", 0.05)
        return

    seconds = rest_time(player)
    print(f"Resting for {seconds} seconds...")

    # Count HP up live, in steps of about 0.1 seconds, for the advertised time
    start_hp = player.hp
    steps = max(1, round(seconds * 10))
    for step in range(1, steps + 1):
        time.sleep(seconds / steps)
        player.hp = start_hp + round(healed * step / steps)
        sys.stdout.write(f"\rHP: {player.hp}/{player.max_hp}")
        sys.stdout.flush()
    print()
    type_slow(f"{player.name} has rested and healed {healed} HP!", 0.02)


def main():
    player = Player(input("Enter your name: "))
    while True:
        show_status(player)

        healing = player.max_hp - player.hp
        rest_option = f"heals {healing} HP, takes {rest_time(player)}s" if healing else "already at full health"
        player_choice = (
            input(f"\nYour options are: \n[F]ight (look for trouble in the {player.location}) \n[E]xplore (travel to an area) \n[S]hop \n[R]est ({rest_option}) \n[Q]uit \n")
            .lower()
            .strip()
        )

        if player_choice == "f":
            fight(player, spawn_enemy(player, player.location))

        elif player_choice == "e":
            explore(player)

        elif player_choice == "s":
            shop(player)

        elif player_choice == "r":
            rest(player)
        elif player_choice == "q":
            quit_choice = input("Do you wish to quit the game (y/n)?").lower().strip()
            if quit_choice == "y":
                sys.exit()
        else:
            type_slow("Invalid choice. Try again.", 0.05)


if __name__ == "__main__":
    main()
