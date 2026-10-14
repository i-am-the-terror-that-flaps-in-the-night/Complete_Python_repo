"""
Tests for both versions of the adventure game. Every test runs once against the
single-file version and once against the multi-file version.

Run from the repo root with:
    python -m unittest discover Adventure_game_files
"""

import contextlib
import importlib
import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

HERE = Path(__file__).parent


def load_single_file():
    sys.path.insert(0, str(HERE / "Single-File_Config"))
    module = importlib.import_module("Adventure_game_2")
    return module


def load_multi_file():
    sys.path.insert(0, str(HERE / "Multi-File_Config"))
    game = SimpleNamespace()
    for name in ["game_data", "entities", "items", "Combat_logic", "Adventure_game"]:
        vars(game).update(vars(importlib.import_module(name)))
    return game


class GameTests:
    """Shared tests. Subclasses set `game` to one version of the game."""

    game = None

    def setUp(self):
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        self.sleep = stack.enter_context(mock.patch("time.sleep"))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.player = self.game.Player("Tester")
        self.player.base_attack = 8

    def answer(self, *answers):
        """Make input() return these answers in order."""
        patcher = mock.patch("builtins.input", side_effect=list(answers))
        patcher.start()
        self.addCleanup(patcher.stop)

    def boss(self, index):
        return self.game.Enemy.boss(self.game.BOSSES[index])

    # --- Damage and defense ---

    def test_damage_taken_is_attack_divided_by_defense(self):
        self.player.defense = 1.2
        brute = self.game.Enemy("Brute", 100, (24, 24))
        taken = self.game.enemy_turn(self.player, brute)
        self.assertEqual(taken, 20)
        self.assertEqual(self.player.hp, 80)

    def test_overkill_does_not_count_toward_damage_dealt(self):
        gremlin = self.game.Enemy.regular("Gremlin")
        self.game.deal_damage(self.player, gremlin, 100)
        self.assertEqual(self.player.damage_dealt, 30)

    def test_attack_gain_scales_with_damage_taken(self):
        for damage_taken, expected_gain in [(0, 1), (21, 3), (200, 21)]:
            player = self.game.Player("P")
            before = player.attack
            self.game.handle_victory(player, self.game.Enemy.regular("Gremlin"), damage_taken)
            self.assertEqual(player.attack - before, expected_gain)

    # --- Items ---

    def test_refrigerator_door_boosts_two_stats(self):
        attack = self.player.attack
        self.game.obtain_item(self.player, "refrigerator")
        self.assertEqual(self.player.attack, attack + 10)
        self.assertEqual(self.player.defense, 1.2)
        self.assertEqual(self.player.inventory, ["refrigerator"])

    def test_max_hp_items_also_heal(self):
        self.player.hp = 50
        self.game.obtain_item(self.player, "amulet")
        self.assertEqual(self.player.max_hp, 125)
        self.assertEqual(self.player.hp, 75)

    def test_enemy_specific_bonus_only_applies_to_that_enemy(self):
        self.game.obtain_item(self.player, "spear")
        orc = self.game.Enemy.regular("Orc")
        goblin = self.game.Enemy.regular("Goblin")
        self.assertEqual(self.player.stat("attack", orc), self.player.attack + 15)
        self.assertEqual(self.player.stat("attack", goblin), self.player.attack)
        self.assertEqual(self.player.stat("attack", self.boss(0)), self.player.attack + 15)

    def test_using_an_item_consumes_one_copy(self):
        self.player.inventory = ["potion", "potion"]
        self.player.hp = 30
        self.answer("1")
        self.assertTrue(self.game.use_item(self.player, self.game.Enemy.regular("Gremlin")))
        self.assertEqual(self.player.hp, 70)
        self.assertEqual(self.player.inventory, ["potion"])

    def test_potion_does_not_overheal(self):
        self.player.inventory = ["potion"]
        self.player.hp = 90
        self.answer("1")
        self.game.use_item(self.player, self.game.Enemy.regular("Gremlin"))
        self.assertEqual(self.player.hp, 100)

    def test_quality_control_only_works_on_ripoffs(self):
        self.player.inventory = ["quality_control"]
        gremlin = self.game.Enemy.regular("Gremlin")
        self.answer("1")
        self.assertFalse(self.game.use_item(self.player, gremlin))
        self.assertEqual(self.player.inventory, ["quality_control"])

        boss = self.boss(0)
        self.answer("1")
        self.assertTrue(self.game.use_item(self.player, boss))
        self.assertEqual(boss.hp, self.game.BOSSES[0]["hp"] - 100)
        self.assertEqual(self.player.inventory, [])

    def test_ukulele_makes_attacks_miss_and_does_not_stack(self):
        brute = self.game.Enemy("Brute", 1000, (10, 10))
        self.player.inventory = ["ukulele", "ukulele"]
        self.answer("1", "1")
        self.game.use_item(self.player, brute)
        self.game.use_item(self.player, brute)
        self.assertEqual(brute.lulled, self.game.ITEMS["ukulele"]["use"]["lull"])

        brute.miss_chance = 1  # Guarantee the misses
        self.assertEqual(self.game.enemy_turn(self.player, brute), 0)
        self.assertEqual(self.game.enemy_turn(self.player, brute), 0)
        self.assertEqual(self.game.enemy_turn(self.player, brute), 10)  # The daze wore off

    def test_shop_only_sells_items_with_a_cost(self):
        self.player.gold = 10_000
        sold = [key for key, item in self.game.ITEMS.items() if "cost" in item]
        self.assertNotIn("godzilla_scale", sold)
        self.answer(str(sold.index("potion") + 1), "l")
        self.game.shop(self.player)
        self.assertEqual(self.player.inventory, ["potion"])
        self.assertEqual(self.player.gold, 10_000 - self.game.ITEMS["potion"]["cost"])

    def test_cannot_buy_without_enough_gold(self):
        self.player.gold = 0
        self.answer("1", "l")
        self.game.shop(self.player)
        self.assertEqual(self.player.inventory, [])

    # --- Bosses ---

    def test_bosses_appear_at_their_damage_thresholds(self):
        self.assertFalse(self.player.boss_ready())
        self.player.damage_dealt = self.game.BOSSES[0]["appears_at"]
        enemy = self.game.spawn_enemy(self.player, "village")
        self.assertEqual(enemy.name, "Demigodzilla")

    def test_boss_drops_items_and_advances_progress(self):
        self.player.attack = 1000
        self.player.damage_dealt = 400
        boss = self.game.spawn_enemy(self.player, "village")
        self.answer("a")
        self.game.fight(self.player, boss)
        self.assertEqual(self.player.bosses_beaten, 1)
        self.assertIsNone(self.player.current_boss)
        self.assertIn("atomic_breath_mint", self.player.inventory)
        self.assertFalse(self.player.boss_ready())
        self.assertEqual(self.player.next_boss()["name"], "Tharnoth")

    def test_fled_boss_keeps_its_damage_and_attack(self):
        self.player.damage_dealt = 400
        self.player.attack = 50
        boss = self.game.spawn_enemy(self.player, "village")
        full_hp, attack = boss.hp, boss.attack
        self.answer("a", "r")  # Hit it once, survive its hit, then run
        self.game.fight(self.player, boss)
        again = self.game.spawn_enemy(self.player, "village")
        self.assertEqual(again.hp, full_hp - 50)
        self.assertEqual(again.attack, attack)

    def test_beating_the_final_boss_wins_and_it_never_returns(self):
        self.player.attack = 1000
        self.player.bosses_beaten = 1
        self.player.damage_dealt = 1000
        boss = self.game.spawn_enemy(self.player, "village")
        self.assertEqual(boss.name, "Tharnoth")
        self.answer("a", "y")  # Attack, then keep playing
        self.game.fight(self.player, boss)
        self.assertIsNone(self.player.next_boss())
        self.player.damage_dealt = 100_000
        self.assertNotIn("boss", self.game.spawn_enemy(self.player, "village").tags)

    def test_declining_to_keep_playing_ends_the_game(self):
        self.player.attack = 1000
        self.player.bosses_beaten = 1
        self.player.damage_dealt = 1000
        self.answer("a", "n")
        with self.assertRaises(SystemExit):
            self.game.fight(self.player, self.game.spawn_enemy(self.player, "village"))

    def test_dying_respawns_in_the_village_losing_only_gold_and_hp(self):
        self.game.obtain_item(self.player, "refrigerator")
        self.player.location = "castle"
        self.player.gold = 200
        self.player.hp = 1
        attack, defense, inventory = self.player.attack, self.player.defense, list(self.player.inventory)
        self.answer("a")
        self.game.fight(self.player, self.game.Enemy("Brute", 1000, (50, 50)))  # Doesn't exit

        penalty = self.game.DEATH_PENALTY
        self.assertEqual(self.player.location, "village")
        self.assertEqual(self.player.gold, round(200 * (1 - penalty["gold_lost"])))
        self.assertEqual(self.player.hp, round(self.player.max_hp * penalty["hp_left"]))
        self.assertEqual((self.player.attack, self.player.defense), (attack, defense))
        self.assertEqual(self.player.inventory, inventory)

    def test_a_boss_that_beats_you_heals(self):
        self.player.damage_dealt = 400
        self.player.attack = 50
        boss = self.game.spawn_enemy(self.player, "village")
        full_hp = boss.hp
        self.player.hp = 1  # Dies to the boss's first hit
        self.answer("a")
        self.game.fight(self.player, boss)
        self.assertIs(self.game.spawn_enemy(self.player, "village"), boss)
        self.assertEqual(boss.hp, full_hp)

    # --- Scaling ---

    def test_world_strength_grows_and_is_capped(self):
        self.assertEqual(self.player.scale(), 1)
        self.player.damage_dealt = 500
        self.player.bosses_beaten = 1
        self.assertEqual(self.player.scale(), 2.25)
        self.player.damage_dealt = 10**9
        self.assertEqual(self.player.scale(), self.game.SCALING["max"])

    def test_regular_enemies_scale_but_their_gold_does_not(self):
        data = self.game.ENEMY_TEMPLATES["Orc"]
        orc = self.game.Enemy.regular("Orc", 2)
        self.assertEqual(orc.hp, data["hp"] * 2)
        self.assertTrue(data["attack"][0] * 2 <= orc.attack <= data["attack"][1] * 2)
        self.assertEqual(orc.gold, data["gold"])

    def test_player_base_stats_scale_but_bonuses_do_not(self):
        self.game.obtain_item(self.player, "knuckles")  # +10 attack
        self.game.obtain_item(self.player, "amulet")  # +25 max HP
        self.player.damage_dealt = 1000  # World strength x2
        self.assertEqual(self.player.attack, 8 * 2 + 10)
        self.assertEqual(self.player.max_hp, 100 * 2 + 25)

    def test_bosses_get_part_of_the_scaling(self):
        self.player.damage_dealt = 1000  # World strength x2
        boss = self.game.spawn_enemy(self.player, "village")
        expected = 1 + (2 - 1) * self.game.SCALING["boss_share"]
        self.assertEqual(boss.hp, round(self.game.BOSSES[0]["hp"] * expected))

    # --- Locations ---

    def test_enemies_depend_on_location(self):
        for room_name, room in self.game.ROOMS.items():
            enemy = self.game.spawn_enemy(self.player, room_name)
            self.assertIn(enemy.name, room["enemies"])
            data = self.game.ENEMY_TEMPLATES[enemy.name]
            self.assertEqual(enemy.hp, round(data["hp"] * room["strength"]))
            self.assertEqual(enemy.gold, round(data["gold"] * room["strength"]))

    def test_exploring_moves_the_player(self):
        self.answer("cave")
        with mock.patch("random.random", return_value=0.99):  # Nothing happens there
            self.game.explore(self.player)
        self.assertEqual(self.player.location, "cave")

    # --- Rest ---

    def test_rest_time_depends_on_hp_healed(self):
        self.player.hp = 40
        self.assertEqual(self.game.rest_time(self.player), round(60 / self.game.REST_HP_PER_SECOND, 1))
        self.player.hp = self.player.max_hp
        self.assertEqual(self.game.rest_time(self.player), 0)

    def test_rest_waits_and_heals_fully(self):
        self.player.hp = 40
        seconds = self.game.rest_time(self.player)
        self.game.rest(self.player)
        self.assertEqual(self.player.hp, self.player.max_hp)
        typing_delays = (0.02, 0.05)
        rest_waits = [c.args[0] for c in self.sleep.call_args_list if c.args[0] not in typing_delays]
        self.assertAlmostEqual(sum(rest_waits), seconds)


class SingleFileTests(GameTests, unittest.TestCase):
    game = load_single_file()


class MultiFileTests(GameTests, unittest.TestCase):
    game = load_multi_file()


if __name__ == "__main__":
    unittest.main()
