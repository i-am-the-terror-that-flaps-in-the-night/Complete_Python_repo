"""
This game is still in progress and will have bugs and non-functionality.
"""

import random

from Combat_logic import Combat

# ---------- Game Data ----------


player = {
    "name": "",
    "health": 100,
    "inventory": ["sword"],
    "gold": 0,
    "ukulele_active": False,
    "ukulele_charges": 0,
}

rooms_list = {
    "village": {"type": "safe", "chance_of_enemy": 0.1, "chance_of_item": 0.7},
    "forest": {"type": "wild", "chance_of_enemy": 0.5, "chance_of_item": 0.875},
    "cave": {"type": "dangerous", "chance_of_enemy": 0.8, "chance_of_item": 0.4},
    "castle": {"type": "fatal", "chance_of_enemy": 1, "chance_of_item": 0.1},
}

items = ["potion", "sword", "shield"]
enemies_killed = 0


# ---------- Functions ----------


def intro():
    print("Welcome to the Adventure Game!")
    player["name"] = input("What is your hero's name? ")


def show_status():
    print(
        f"\n--- {player['name']} | HP: {player['health']} | Gold: {player['gold']} ---"
    )


def use_item():
    if not player["inventory"]:
        print("Your inventory is empty.")
        return

    print("\nItems in inventory:")
    for i, item in enumerate(player["inventory"], 1):
        print(f"{i}. {item}")

    item_usage = input("Use an item [yes/no]? ").strip().lower()
    if item_usage == "yes":
        item_chosen = input("Which item? ").strip().lower()
        if item_chosen == "potion" and "potion" in player["inventory"]:
            player["inventory"].remove("potion")
            player["health"] = min(100, player["health"] + 20)  # Caps health at 100
            print(f"Healed! Health is now {player['health']}.")
        elif item_chosen == "ukulele" and "ukulele" in player["inventory"]:
            player["inventory"].remove("ukulele")
            print("The ukulele was used. Effect unknown")
            player["ukulele_active"] = True
            player["ukulele_charges"] += 2
        elif item_chosen in player["inventory"]:
            print(f"You can't use the {item_chosen} right now.")
        else:
            print("You don't have that item.")


def choose_room():
    # .keys() gives you just "village", "forest", etc.
    print(f"Areas: {', '.join(rooms_list.keys())}")
    while True:
        choice = input("Enter an area: ").strip().lower()
        if choice in rooms_list:
            return choice
        print("That area doesn't exist.")


def find_item():
    found = random.choice(items)
    player["inventory"].append(found)
    print(f"✨ You found a {found}!")
    return found  # We return this so other functions can see it


def shop():
    print("\n--- Welcome to the Shop! ---")
    while True:
        items_in_shop = ["potion", "sword", "shield", "spear", "ukulele"]
        print(f"Your Gold: {player['gold']}")
        for i, item in enumerate(items_in_shop, 1):
            print(f"{i}. {item} (15 Gold)")

        choice = input("\nBuy an item (type name) or 'exit' to leave: ").strip().lower()

        if choice == "exit":
            break
        elif choice in items_in_shop:
            if player["gold"] >= 15:
                player["inventory"].append(choice)
                player["gold"] -= 15
                print(f"Purchased {choice}!")
            else:
                print("You're too broke for that.")
        else:
            print("We don't sell that here.")


def main():
    global enemies_killed  # Use global so we can update the counter
    intro()
    while player["health"] > 0:
        show_status()
        # Maybe don't force them into the shop EVERY turn?
        # You could move shop() inside an 'if room == "village"' block later.
        shop()
        use_item()
        room = choose_room()

        # Decide if something happens in the room, based on the room's odds
        found_item = random.random() < rooms_list[room]["chance_of_item"]
        met_enemy = random.random() < rooms_list[room]["chance_of_enemy"]

        if found_item:
            find_item()
        if met_enemy:
            # Update the kills by catching the return value
            enemies_killed = Combat.encounter_enemy(False, player, enemies_killed)
        if not found_item and not met_enemy:
            print("The room is quiet. Nothing here.")

    print("\n💀 You have died. Game Over.")


if __name__ == "__main__":
    main()
