import random


class Combat:
    @staticmethod
    def get_enemy_stats(is_boss):
        enemy_health = random.randint(10, 90)
        if is_boss:
            enemy_health *= 7

        if enemy_health <= 30:
            enemy_name = "Gremlin"
        elif 30 < enemy_health <= 60:
            enemy_name = "Goblin"
        elif 60 < enemy_health <= 90:
            enemy_name = "Orc"
        else:
            enemy_name = (
                "Tharnoth the inevitable, Bootleg Thanos out of Bilbo Baggins' pantry"
            )

        return enemy_name, enemy_health

    @staticmethod
    def calculate_player_attack(player):
        return 5 + (player["inventory"].count("sword") * 10)

    @staticmethod
    def calculate_enemy_damage(is_boss, player):
        base_atk = random.randint(5, 15)
        if is_boss:
            base_atk = round(base_atk * 6.7)
            if player.get("ukulele_active") and player.get("ukulele_charges") > 0:
                base_atk = random.choice([base_atk, 0, 0, 0, 0, 0, 0, 0])
                player["ukulele_charges"] -= 1
            if player.get("ukulele_charges") <= 0:
                player["ukulele_active"] = False

        evasion = player["inventory"].count("shield") * 5
        return max(0, base_atk - evasion), evasion

    @staticmethod
    def handle_victory(enemy_name, player):
        loot = random.randint(5, 20)
        player["gold"] += loot
        print(f"You defeated the {enemy_name} and found {loot} gold!")
        return True

    @staticmethod
    def encounter_enemy(is_boss, player, current_kills):
        # We check the boss status based on the kills passed from the main file
        if current_kills > 5:
            is_boss = True

        enemy, enemy_health = Combat.get_enemy_stats(is_boss)
        print(f"👾 {enemy} appears with {enemy_health} HP!")

        while enemy_health > 0 and player["health"] > 0:
            action = input("[Fight] or [Run]? ").lower().strip()

            if action == "run":
                print("You ran away!")
                return current_kills  # Return the same number if they ran

            if action == "fight":
                atk = Combat.calculate_player_attack(player)
                enemy_health -= atk
                print(f"You hit for {atk} damage!")

                if enemy_health > 0:
                    dmg, blocked = Combat.calculate_enemy_damage(is_boss, player)
                    player["health"] -= dmg
                    print(f"The {enemy} hit you for {dmg}! (Blocked {blocked})")
                    print(f"Your Health: {player['health']}")
            else:
                print("Invalid action.")

        if enemy_health <= 0:
            Combat.handle_victory(enemy, player)
            return current_kills + 1  # Return the NEW kill count

        return current_kills  # If they died, just return current
