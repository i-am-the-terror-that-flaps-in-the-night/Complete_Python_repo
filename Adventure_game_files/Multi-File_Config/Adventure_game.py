"""
This game is still in progress and will have bugs and non-functionality.
Run this file to play.
"""

import random
import sys

from Combat_logic import fight, spawn_enemy
from entities import Player
from game_data import ENEMY_TEMPLATES, FIND_POOL, ITEMS, ROOMS
from items import obtain_item, shop
from ui import type_slow


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
