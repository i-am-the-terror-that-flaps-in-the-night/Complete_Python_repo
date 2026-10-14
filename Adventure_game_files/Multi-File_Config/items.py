"""Gaining items and the shop."""

from game_data import ITEMS
from ui import type_slow


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
