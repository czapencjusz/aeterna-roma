"""Tests for the game rules. Run with:  python -m unittest discover -s tests"""

import copy
import json
import os
import tempfile
import unittest

from aeterna import data, util
from aeterna.api import Api
from aeterna.data import DUNGEONS, LOCATIONS, PREFIXES, RECIPES, SLOTS, SUFFIXES
from aeterna.engine import Game
from aeterna.items import display_name, generate_item, make_potion, sell_price
from aeterna.rules import max_damage, min_damage, total_armor, training_cost, work_pay, xp_multiplier, hp_regen_per_min
from aeterna.state import build_ladder, new_game_state, normalize_state
from aeterna.storage import SaveStore
from aeterna.view import build_view

START = 1_700_000_000_000  # fixed "now" for tests (ms)


class Clock:
    def __init__(self, now=START):
        self.now = now

    def __call__(self):
        return self.now


def make_game(seed=1):
    util.rng.seed(seed)
    clock = Clock()
    return Game(clock=clock), clock


def make_strong(game):
    """Makes the player strong enough to win any fight."""
    p = game.player
    p['BaseStrength'] = p['BaseDexterity'] = p['BaseConstitution'] = 400
    from aeterna.rules import recalc_stats
    recalc_stats(p)
    p['CurrentHP'] = p['MaxHP']


def unique_ranks(state):
    return len({o['Rank'] for o in state['ArenaLadder']} | {state['Player']['ArenaRank']})


class NewGameTests(unittest.TestCase):
    def test_new_game(self):
        game, _ = make_game()
        p = game.player
        self.assertEqual(p['Name'], 'Flavius')
        self.assertEqual((min_damage(p), max_damage(p)), (8, 16))
        self.assertEqual(p['MaxHP'], 275)
        self.assertEqual(len(game.state['ArenaLadder']), 20)
        self.assertEqual(unique_ranks(game.state), 21)
        self.assertTrue(all(slot['Quest'] for slot in game.state['QuestSlots']))

    def test_vendors_stock_their_own_types(self):
        game, _ = make_game()
        vendors = game.state['Vendors']
        self.assertTrue(all(i['Type'] in ('Weapon', 'Shield') for i in vendors['Weaponsmith']['Items']))
        self.assertTrue(all(i['Type'] in ('Armor', 'Helmet', 'Gloves', 'Shoes') for i in vendors['Armorer']['Items']))
        self.assertTrue(all(i['Type'] in ('Ring', 'Amulet') for i in vendors['General']['Items']))
        self.assertEqual(len(vendors['Alchemist']['Items']), len(data.ALCHEMIST_ITEMS))

    def test_state_is_json_serializable(self):
        game, _ = make_game()
        json.dumps(game.state)
        json.dumps(build_view(game))


class ItemTests(unittest.TestCase):
    def test_affixes_grant_their_stats(self):
        util.rng.seed(2)
        with_affix = 0
        for _ in range(2000):
            item = generate_item(util.rand_int(1, 20))
            affixes = [a for a in PREFIXES if a['Name'] == item['Prefix']] + [a for a in SUFFIXES if a['Name'] == item['Suffix']]
            with_affix += bool(affixes)
            for affix in affixes:
                for stat, weight in affix['Stats'].items():
                    self.assertGreaterEqual(item[stat], weight)
        self.assertGreater(with_affix, 1000)

    def test_icons_match_item_names(self):
        util.rng.seed(3)
        for _ in range(300):
            item = generate_item(3, 'Weapon')
            if item['Name'] == 'Trident':
                self.assertEqual(item['IconSvg'], 'weapon_4')
            if item['Name'] == 'Halberd':
                self.assertEqual(item['IconSvg'], 'weapon_5')

    def test_licensed_icons_are_embedded_and_credited(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, 'aeterna', 'ui', 'index.html'), encoding='utf-8') as f:
            page = f.read()
        with open(os.path.join(root, 'CREDITS.md'), encoding='utf-8') as f:
            credits = f.read()
        block = page[page.index('const LICENSED_ICONS = '):]
        embedded = json.loads(block[len('const LICENSED_ICONS = '):block.index(';\n')])
        used = {icon for icon in data.ICON_BY_NAME.values() if icon.startswith('gi_')}
        self.assertTrue(used)
        self.assertLessEqual(used, set(embedded))
        for name, icon in data.ICON_BY_NAME.items():
            if icon.startswith('gi_'):
                self.assertIn('| %s |' % name, credits)
        for names in data.BASE_NAMES.values():
            for name in names:
                self.assertIn(name, data.ICON_BY_NAME)

    def test_display_name_and_sell_price(self):
        item = make_potion({'Name': 'Test', 'Price': 21})
        self.assertEqual(display_name(item), 'Test')
        self.assertEqual(sell_price(item), 10)
        item.update(Prefix='Titan', Suffix='of Mars', Upgrade=2)
        self.assertEqual(display_name(item), 'Titan Test of Mars +2')


class FightTests(unittest.TestCase):
    def test_expedition_costs_energy_and_returns_report(self):
        game, _ = make_game()
        result = game.start_expedition(0, 1)
        self.assertIsNotNone(result)
        self.assertEqual(game.player['CurrentEnergy'], 23)
        self.assertTrue(result['Turns'])
        for turn in result['Turns']:
            self.assertGreaterEqual(turn['PHP'], 0)
            self.assertGreaterEqual(turn['EHP'], 0)

    def test_locked_region_and_dungeon(self):
        game, _ = make_game()
        self.assertIsNone(game.start_expedition(1, 0))
        self.assertIsNone(game.enter_dungeon(0))
        self.assertEqual(len(game.take_notices()), 2)

    def test_cannot_fight_wounded_or_while_working(self):
        game, _ = make_game()
        game.player['CurrentHP'] = 1
        self.assertIsNone(game.start_expedition(0, 0))
        game.player['CurrentHP'] = game.player['MaxHP']
        game.start_work(1)
        self.assertIsNone(game.start_expedition(0, 0))
        self.assertEqual(game.player['CurrentEnergy'], 24)

    def test_bad_indices_are_ignored(self):
        game, _ = make_game()
        for args in [(-1, 0), (0, 99), ('x', 0), (None, None), (1.9, 0.2)]:
            game.start_expedition(*args)
        game.challenge_arena(500)
        game.enter_dungeon('nope')
        game.equip(99)
        game.buy('Nobody', 0)
        game.enhance(7, 0)
        json.dumps(game.state)

    def test_arena_win_swaps_ranks_and_sets_cooldown(self):
        game, clock = make_game()
        make_strong(game)
        idx = next(i for i, o in enumerate(game.state['ArenaLadder']) if o['Rank'] == 9)
        result = game.challenge_arena(idx)
        self.assertTrue(result['IsVictory'])
        self.assertEqual(game.player['ArenaRank'], 9)
        self.assertEqual(game.state['ArenaLadder'][idx]['Rank'], 10)
        self.assertEqual(unique_ranks(game.state), 21)
        self.assertEqual(game.state['ArenaCooldownUntil'], clock.now + data.ARENA_COOLDOWN_MS)
        self.assertIsNone(game.challenge_arena(0))  # still cooling down

    def test_arena_milestones_pay_once(self):
        game, _ = make_game()
        make_strong(game)
        game.state['ArenaLadder'] = build_ladder(6)
        game.player['ArenaRank'] = 6
        rubies = game.player['Rubies']
        game.challenge_arena(next(i for i, o in enumerate(game.state['ArenaLadder']) if o['Rank'] == 5))
        self.assertEqual(game.player['Rubies'] - rubies, 2)
        # Drop back and win rank 5 again: no second payout.
        other = next(o for o in game.state['ArenaLadder'] if o['Rank'] == 6)
        other['Rank'], game.player['ArenaRank'] = 5, 6
        game.state['ArenaCooldownUntil'] = 0
        rubies = game.player['Rubies']
        game.challenge_arena(game.state['ArenaLadder'].index(other))
        self.assertEqual(game.player['Rubies'], rubies)

    def test_dungeon_conquest_and_boss_rubies(self):
        game, _ = make_game()
        make_strong(game)
        game.player['Level'] = 20
        game.player['CurrentEnergy'] = 99
        progress = game.state['DungeonProgress']['1']
        rubies = game.player['Rubies']
        for _ in range(3):
            game.player['CurrentHP'] = game.player['MaxHP']
            self.assertTrue(game.enter_dungeon(0)['IsVictory'])
        self.assertTrue(progress['IsCompleted'])
        self.assertEqual(progress['Conquests'], 1)
        self.assertIn(game.player['Rubies'] - rubies, (2, 3))
        self.assertIsNone(game.enter_dungeon(0))
        game.restart_dungeon(0)
        self.assertEqual((progress['CurrentStage'], progress['IsCompleted'], progress['Conquests']), (1, False, 1))

    def test_combat_fuzz(self):
        game, _ = make_game(5)
        for n in range(1500):
            game.player['Level'] = 1 + n % 18
            game.player['CurrentHP'] = game.player['MaxHP']
            location = LOCATIONS[n % len(LOCATIONS)]
            if game.player['Level'] < location['ReqLevel']:
                continue
            from aeterna import combat
            monster = combat.scale_monster(location['Monsters'][n % len(location['Monsters'])], game.player['Level'],
                                           location['ReqLevel'])
            result = combat.run_fight(game.state, 't', combat.monster_combatant(monster))
            self.assertGreaterEqual(game.player['CurrentHP'], 1)
            self.assertTrue(all(isinstance(t['Damage'], int) for t in result['Turns']))


class CharacterTests(unittest.TestCase):
    def test_potion_heals_with_intelligence_bonus(self):
        game, _ = make_game()
        game.player['CurrentHP'] = 1
        game.use_potion(0)
        self.assertEqual(game.player['CurrentHP'], 1 + int(50 * 1.1))

    def test_potion_not_wasted(self):
        game, _ = make_game()
        game.use_potion(0)
        self.assertEqual(len(game.player['Inventory']), 1)
        self.assertTrue(game.take_notices())

    def test_regen_over_time(self):
        game, clock = make_game()
        game.player['CurrentHP'] = 10
        game.state['LastHPRegen'] = clock.now - 180000
        game.apply_regen(clock.now)
        self.assertEqual(game.player['CurrentHP'], 23)  # (2 + 5 * 0.5) * 3 minutes

    def test_regen_ignores_clock_going_backwards(self):
        game, clock = make_game()
        game.player['CurrentHP'] = 10
        game.state['LastHPRegen'] = clock.now + 999999
        game.apply_regen(clock.now)
        self.assertEqual(game.player['CurrentHP'], 10)
        self.assertEqual(game.state['LastHPRegen'], clock.now)

    def test_equip_unequip_sell_smelt(self):
        game, _ = make_game()
        p = game.player
        too_high = generate_item(5, 'Helmet')
        p['Inventory'].append(too_high)
        game.equip(len(p['Inventory']) - 1)
        self.assertIsNone(p['Equipment']['Head'])
        ok = generate_item(1, 'Helmet')
        p['Inventory'].append(ok)
        game.equip(len(p['Inventory']) - 1)
        self.assertIs(p['Equipment']['Head'], ok)
        armor = total_armor(p)
        game.unequip('Head')
        self.assertEqual(total_armor(p), armor - ok['Armor'])
        gold = p['Gold']
        game.sell(p['Inventory'].index(ok))
        self.assertEqual(p['Gold'], gold + ok['Price'] // 2)
        iron = game.state['IronStash']
        game.smelt(p['Inventory'].index(too_high))
        self.assertEqual(game.state['IronStash'], iron + too_high['SmeltIron'])

    def test_buy_sell_round_trip_costs_gold(self):
        game, _ = make_game()
        p = game.player
        p['Gold'] = 10000
        item = game.state['Vendors']['Weaponsmith']['Items'][0]
        game.buy('Weaponsmith', 0)
        game.sell(p['Inventory'].index(item))
        self.assertEqual(10000 - p['Gold'], item['Price'] - sell_price(item))

    def test_apothecary_never_runs_out(self):
        game, _ = make_game()
        game.buy('Alchemist', 0)
        self.assertEqual(len(game.state['Vendors']['Alchemist']['Items']), len(data.ALCHEMIST_ITEMS))
        self.assertEqual(game.player['Inventory'][-1]['Name'], 'Small Health Potion')

    def test_sell_junk_keeps_rares_and_potions(self):
        game, _ = make_game()
        p = game.player
        p['Inventory'] = [generate_item(1, 'Helmet', 'Common') for _ in range(3)]
        p['Inventory'] += [generate_item(1, 'Helmet', 'Epic'), make_potion({'Name': 'P', 'HealAmount': 10, 'Price': 10})]
        expected = sum(sell_price(i) for i in p['Inventory'][:3])
        gold = p['Gold']
        game.sell_junk()
        self.assertEqual([i['Rarity'] + i['Type'] for i in p['Inventory']], ['EpicHelmet', 'CommonPotion'])
        self.assertEqual(p['Gold'], gold + expected)

    def test_crafting(self):
        game, _ = make_game()
        p = game.player
        count = len(p['Inventory'])
        game.craft(0)  # needs level 2
        self.assertEqual(len(p['Inventory']), count)
        p['Level'] = 2
        game.craft(0)
        item = p['Inventory'][-1]
        self.assertEqual((item['Type'], item['Rarity'], item['Name']), ('Weapon', 'Uncommon', 'Centurion Gladius'))
        self.assertGreater(item['MaxDamage'], item['MinDamage'])
        self.assertEqual(item['Armor'], 0)

    def test_craft_with_full_inventory_keeps_materials(self):
        game, _ = make_game()
        p = game.player
        p['Level'] = 2
        game.state['IronStash'] = 99
        while len(p['Inventory']) < p['InventoryCapacity']:
            p['Inventory'].append(generate_item(1))
        game.craft(0)
        self.assertEqual(game.state['IronStash'], 99)

    def test_enhancement(self):
        game, _ = make_game()
        p = game.player
        weapon = p['Equipment']['Weapon']
        before = (weapon['MinDamage'], weapon['MaxDamage'], max_damage(p))
        p['Gold'] = 100000
        for key in ('IronStash', 'BronzeStash', 'LeatherStash', 'RubyStash'):
            game.state[key] = 999
        for _ in range(6):
            game.enhance(0, SLOTS.index('Weapon'))
        self.assertEqual(weapon['Upgrade'], 5)
        self.assertTrue(display_name(weapon).endswith('+5'))
        self.assertGreater(weapon['MinDamage'], before[0])
        self.assertGreater(max_damage(p), before[2])
        self.assertLessEqual(weapon['MinDamage'], weapon['MaxDamage'])
        self.assertEqual(999 - game.state['RubyStash'], 6)
        ring = generate_item(1, 'Ring')
        p['Inventory'] = [ring]
        strength = ring['Strength']
        game.enhance(1, 0)
        self.assertEqual(ring['Strength'], strength + 1)

    def test_training_and_level_up(self):
        game, _ = make_game()
        p = game.player
        p['Gold'] = 1000
        cost = training_cost(game.state, p['BaseStrength'])
        game.train(0)
        self.assertEqual((p['BaseStrength'], p['Gold']), (6, 1000 - cost))
        old_id = game.state['Vendors']['Weaponsmith']['Items'][0]['Id']
        self.assertEqual(game.gain_xp(p['MaxXP']), 1)
        self.assertEqual(p['Level'], 2)
        self.assertNotEqual(game.state['Vendors']['Weaponsmith']['Items'][0]['Id'], old_id)

    def test_rename(self):
        game, _ = make_game()
        game.rename('  Maximus   Decimus ')
        self.assertEqual(game.player['Name'], 'Maximus Decimus')
        game.rename('X')
        self.assertEqual(game.player['Name'], 'Maximus Decimus')


class WorkGuildQuestTests(unittest.TestCase):
    def test_work_pays_when_done(self):
        game, clock = make_game()
        game.start_work(2)
        gold = game.player['Gold']
        self.assertEqual(game.tick(), 'none')
        clock.now += 2 * 3600 * 1000
        self.assertEqual(game.tick(), 'all')
        self.assertEqual(game.player['Gold'] - gold, 220)
        self.assertFalse(game.state['ActiveWork']['IsWorking'])

    def test_guild_and_buildings(self):
        game, _ = make_game()
        p = game.player
        p['Gold'] = 100000
        game.create_guild('X', 'ROM')  # name too short
        self.assertFalse(game.state['PlayerGuild']['HasGuild'])
        game.create_guild('Legio X', 'lx')
        guild = game.state['PlayerGuild']
        self.assertEqual((guild['Name'], guild['Tag']), ('Legio X', 'LX'))
        train_before, work_before, regen_before = training_cost(game.state, 10), work_pay(game.state, 1)[0], hp_regen_per_min(game.state)
        for _ in range(20):
            game.donate(2)
        for key in ('TrainingGrounds', 'Library', 'Villa', 'Library'):
            game.upgrade_building(key)
        self.assertEqual(guild['GoldVault'], 20000 - 500 - 500 - 500 - 2000)
        self.assertEqual(guild['Level'], 2)
        self.assertEqual(guild['Buildings'], {'TrainingGrounds': 1, 'Library': 2, 'Villa': 1})
        self.assertEqual(training_cost(game.state, 10), int(train_before * 0.95))
        self.assertAlmostEqual(xp_multiplier(game.state), 1.1)
        self.assertEqual(work_pay(game.state, 1)[0], 121)
        self.assertEqual(work_before, 110)
        self.assertAlmostEqual(hp_regen_per_min(game.state) / regen_before, 1.1)

    def test_quests(self):
        game, clock = make_game()
        make_strong(game)
        p = game.player
        slots = game.state['QuestSlots']
        slots[0]['Quest'] = {'Id': 'q', 'Kind': 'expedition', 'Target': '', 'Goal': 1, 'Progress': 0,
                             'RewardGold': 77, 'RewardXP': 5, 'RewardRubies': 1}
        slots[1]['Quest'] = {'Id': 'q2', 'Kind': 'monster', 'Target': 'm3', 'Goal': 1, 'Progress': 0,
                             'RewardGold': 1, 'RewardXP': 1, 'RewardRubies': 0}
        game.start_expedition(0, 0)  # Wild Boar: counts for the expedition quest, not the bandit quest
        self.assertEqual((slots[0]['Quest']['Progress'], slots[1]['Quest']['Progress']), (1, 0))
        game.start_expedition(0, 2)
        self.assertEqual(slots[1]['Quest']['Progress'], 1)
        gold, rubies = p['Gold'], p['Rubies']
        game.claim_quest(0)
        self.assertEqual((p['Gold'] - gold, p['Rubies'] - rubies), (77, 1))
        self.assertNotEqual(slots[0]['Quest']['Id'], 'q')
        game.abandon_quest(2)
        self.assertIsNone(slots[2]['Quest'])
        self.assertEqual(game.tick(), 'none')
        clock.now = slots[2]['NextAt']
        self.assertEqual(game.tick(), 'all')
        self.assertIsNotNone(slots[2]['Quest'])

    def test_ruby_shop(self):
        game, clock = make_game()
        p = game.player
        p['Rubies'], p['CurrentEnergy'] = 3, 0
        game.ruby_refill_energy()
        self.assertEqual((p['CurrentEnergy'], p['Rubies']), (p['MaxEnergy'], 1))
        game.state['ArenaCooldownUntil'] = clock.now + 100000
        game.ruby_skip_arena()
        self.assertEqual((game.state['ArenaCooldownUntil'], p['Rubies']), (0, 0))
        first_id = game.state['Vendors']['Weaponsmith']['Items'][0]['Id']
        game.ruby_restock('Weaponsmith')
        self.assertEqual(game.state['Vendors']['Weaponsmith']['Items'][0]['Id'], first_id)  # no rubies left
        p['Rubies'] = 1
        game.ruby_restock('Weaponsmith')
        self.assertNotEqual(game.state['Vendors']['Weaponsmith']['Items'][0]['Id'], first_id)


class SaveTests(unittest.TestCase):
    def test_round_trip_is_lossless(self):
        game, clock = make_game()
        make_strong(game)
        game.start_expedition(0, 0)
        game.player['Gold'] = 5000
        game.create_guild('Legio X', 'LX')
        restored = normalize_state(json.loads(json.dumps(game.state)), clock.now)
        self.assertEqual(restored, json.loads(json.dumps(game.state)))

    def test_browser_version_save_imports(self):
        """A save exported from the earlier HTML/JavaScript version (numeric dungeon keys, v2 fields)."""
        game, clock = make_game()
        old = copy.deepcopy(game.state)
        old['Version'] = 2
        old['DungeonProgress'] = {'1': {'CurrentStage': 2, 'IsCompleted': False, 'Conquests': 0}}
        old['LastHPRegen'] = clock.now - 60000.5  # the JS version stored fractional timestamps
        state = normalize_state(old, clock.now)
        self.assertEqual(state['DungeonProgress']['1']['CurrentStage'], 2)
        self.assertEqual(state['DungeonProgress']['3']['CurrentStage'], 1)
        self.assertEqual(state['LastHPRegen'], clock.now - 60000.5)

    def test_csharp_server_save_imports(self):
        legacy = {
            'Player': {'Name': 'Maximus', 'Level': 3, 'XP': 10, 'MaxXP': 225, 'Gold': 999, 'ArenaRank': 7,
                       'BaseStrength': 8, 'CurrentHP': 50, 'MaxEnergy': 28, 'CurrentEnergy': 5,
                       'Equipment': {'Chest': {'Name': 'Tunic', 'Type': 1, 'Rarity': 0, 'Armor': 10},
                                     'Weapon': {'Name': 'Gladius', 'Type': 0, 'Rarity': 3, 'MinDamage': 9, 'MaxDamage': 15},
                                     'Head': {'Name': 'Misplaced', 'Type': 4}},
                       'Inventory': [{'Name': 'Health Potion', 'Type': 8, 'HealAmount': 50, 'Price': 20},
                                     {'Name': '<b>x</b>', 'Type': 2, 'Rarity': 4, 'Armor': 5},
                                     {'Name': 'Bad', 'Type': 99, 'Rarity': True}]},
            'ArenaLadder': [{'Id': 'arena_%d' % (i + 1), 'Rank': i + 1, 'Name': 'Flavius' if i == 4 else 'N'} for i in range(20)],
            'Dungeons': [{'Id': 1, 'CurrentStage': 2, 'IsCompleted': False}],
            'PlayerGuild': {'HasGuild': True, 'Name': 'Old', 'TrainingGroundLevel': 1, 'LibraryLevel': 3},
            'LastHPRegen': '/Date(1700000000000)/',
            'IronStash': 3,
        }
        state = normalize_state(legacy, START)
        p = state['Player']
        self.assertEqual((p['Equipment']['Weapon']['Type'], p['Equipment']['Weapon']['Rarity']), ('Weapon', 'Epic'))
        self.assertEqual([i['Type'] for i in p['Inventory']], ['Ring', 'Potion', 'Helmet', 'Material'])  # misplaced ring moved to bag
        self.assertEqual(unique_ranks(state), 21)
        self.assertEqual(next(o for o in state['ArenaLadder'] if o['Id'] == 'arena_5')['Name'], 'Priscus')
        self.assertEqual(state['DungeonProgress']['1']['CurrentStage'], 2)
        self.assertEqual(state['PlayerGuild']['Buildings'], {'TrainingGrounds': 0, 'Library': 2, 'Villa': 0})
        self.assertEqual(state['LastHPRegen'], START)
        self.assertEqual(state['IronStash'], 3)

    def test_garbage_saves_start_a_new_game(self):
        for raw in (None, [], 'x', {'Player': 5}, {'Player': {'Level': 'abc', 'Equipment': 'nope', 'Inventory': {}}}):
            state = normalize_state(raw, START)
            json.dumps(state)
            self.assertGreaterEqual(state['Player']['Level'], 1)

    def test_store_writes_atomically_and_backs_up_corrupt_saves(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = SaveStore(tmp)
            self.assertEqual(store.load(), (None, None))
            game, _ = make_game()
            store.save(game.state)
            raw, warning = store.load()
            self.assertEqual(raw['Player']['Name'], 'Flavius')
            self.assertIsNone(warning)
            with open(store.path, 'w') as f:
                f.write('{broken')
            raw, warning = store.load()
            self.assertIsNone(raw)
            self.assertIn('could not be read', warning)
            backups = [n for n in os.listdir(tmp) if n.startswith('save.corrupt-')]
            self.assertEqual(len(backups), 1)
            with open(os.path.join(tmp, backups[0])) as f:
                self.assertEqual(f.read(), '{broken')

    def test_single_instance_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = SaveStore(tmp), SaveStore(tmp)
            self.assertTrue(first.acquire_lock())
            self.assertFalse(second.acquire_lock())
            first._lock_file.close()


class ApiTests(unittest.TestCase):
    def test_actions_save_and_return_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            util.rng.seed(4)
            store = SaveStore(tmp)
            api = Api(Game(clock=Clock()), store)
            response = api.start_expedition(0, 1)
            self.assertIn('view', response)
            self.assertIsNotNone(response['result'])
            with open(store.path) as f:
                self.assertEqual(json.load(f)['Player']['CurrentEnergy'], 23)
            second = api.get_view()
            self.assertGreater(second['view']['seq'], response['view']['seq'])
            json.dumps(second)

    def test_errors_become_notices(self):
        api = Api(Game(clock=Clock()))
        api._game.start_expedition = lambda *a: 1 / 0
        response = api.start_expedition(0, 0)
        self.assertTrue(any('Something went wrong' in n for n in response['notices']))

    def test_export_and_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            api = Api(Game(clock=Clock()))
            api._game.player['Gold'] = 4242
            path = os.path.join(tmp, 'out.json')
            api._run(api._export_to, path)
            api._game.reset()
            self.assertEqual(api._game.player['Gold'], 250)
            response = api._run(api._import_from, path)
            self.assertEqual(response['view']['state']['Player']['Gold'], 4242)
            with open(os.path.join(tmp, 'bad.json'), 'w', encoding='utf-8') as f:
                f.write('﻿{"not": "a save"}')
            response = api._run(api._import_from, os.path.join(tmp, 'bad.json'))
            self.assertIn('That file is not an Aeterna Roma save.', response['notices'])

    def test_tick_only_sends_view_on_change(self):
        clock = Clock()
        api = Api(Game(clock=clock))
        self.assertEqual(api.tick(), {'change': 'none'})
        api._game.player['CurrentHP'] = 10
        clock.now += 120000
        self.assertEqual(api.tick()['change'], 'sidebar')


class SetAndTreasureTests(unittest.TestCase):
    def test_set_bonuses_apply_when_enough_pieces_are_worn(self):
        from aeterna.items import make_set_piece
        from aeterna.rules import all_effects, set_counts, recalc_stats
        game, _ = make_game()
        p = game.player
        armor_before = total_armor(p)
        pieces = data.SETS['legion']['Pieces']
        for item_type in sorted(pieces):
            piece = make_set_piece('legion', 5, item_type)
            self.assertEqual((piece['SetId'], piece['Rarity'], piece['Name']), ('legion', 'Epic', pieces[item_type][0]))
            p['Equipment'][data.SLOT_FOR_TYPE[item_type]] = piece
        recalc_stats(p)
        self.assertEqual(set_counts(p), {'legion': 4})
        effects = all_effects(game.state)
        self.assertEqual((effects['ArmorPct'], effects['HPPct'], effects['BlockBonus']), (10, 10, 5))
        raw_armor = sum(i['Armor'] for i in p['Equipment'].values() if i)
        self.assertEqual(total_armor(p), int(raw_armor * 1.1))
        self.assertGreater(total_armor(p), armor_before)
        self.assertEqual(game.achievement_progress(next(a for a in data.ACHIEVEMENTS if a['Stat'] == 'FullSet'))[0], 1)

    def test_every_set_and_unique_is_obtainable(self):
        sources = {k for area in LOCATIONS + DUNGEONS for k in area.get('Sets', [])} | {'murmillo'}
        self.assertEqual(sources, set(data.SETS))
        bosses = {d['Stages'][-1]['Monster']['Name'] for d in DUNGEONS}
        self.assertTrue(set(data.UNIQUES) <= bosses)
        for set_id, definition in data.SETS.items():
            for item_type, (name, icon) in definition['Pieces'].items():
                self.assertIn(item_type, data.SLOT_FOR_TYPE)
            for needed, effects in definition['Bonuses']:
                self.assertTrue(set(effects) <= set(data.EFFECTS))
                self.assertLessEqual(needed, len(definition['Pieces']))

    def test_mythic_treasure_first_conquest_and_life_steal(self):
        from aeterna import combat
        from aeterna.rules import all_effects
        game, _ = make_game(3)
        make_strong(game)
        game.player['Level'] = 20
        game.player['CurrentEnergy'] = 999
        game.player['Inventory'] = []
        dungeon = next(i for i, d in enumerate(DUNGEONS) if d['Stages'][-1]['Monster']['Name'] == 'Lich Lord Cassius')
        for _ in DUNGEONS[dungeon]['Stages']:
            game.player['CurrentHP'] = game.player['MaxHP']
            game.enter_dungeon(dungeon)
        crowns = [i for i in game.player['Inventory'] if i['Rarity'] == 'Mythic']
        self.assertEqual([c['Name'] for c in crowns], ['Crown of Cassius'])
        self.assertEqual(game.state['Stats']['UniquesFound'], 1)
        game.player['Equipment']['Head'] = crowns[0]
        self.assertEqual(all_effects(game.state)['LifeSteal'], 5)
        # Life steal heals the attacker during a fight.
        game.player['CurrentHP'] = game.player['MaxHP'] // 2
        monster = combat.scale_monster(LOCATIONS[0]['Monsters'][0], 20, 1)
        result = combat.run_fight(game.state, 't', combat.monster_combatant(monster))
        self.assertTrue(result['IsVictory'])
        self.assertGreater(game.player['CurrentHP'], game.player['MaxHP'] // 2)

    def test_effect_caps(self):
        from aeterna.rules import all_effects
        game, _ = make_game()
        for slot in SLOTS:
            item = generate_item(5, next(t for t, s in data.SLOT_FOR_TYPE.items() if s == slot), 'Mythic')
            item['Effects'] = {'LifeSteal': 20, 'CritBonus': 20}
            game.player['Equipment'][slot] = item
        effects = all_effects(game.state)
        self.assertEqual(effects['LifeSteal'], data.EFFECT_CAPS['LifeSteal'])
        self.assertEqual(effects['CritBonus'], data.EFFECT_CAPS['CritBonus'])


class TempleHonorLaurelTests(unittest.TestCase):
    def test_blessing_costs_gold_and_wears_off(self):
        from aeterna.rules import all_effects
        game, _ = make_game()
        make_strong(game)
        game.player['Gold'] = 10_000
        game.player['CurrentEnergy'] = 99
        game.buy_blessing('mars')
        self.assertEqual(game.player['Gold'], 10_000 - data.blessing_cost(1))
        self.assertEqual(all_effects(game.state)['DamagePct'], 15)
        for _ in range(data.BLESSINGS['mars']['Fights']):
            game.player['CurrentHP'] = game.player['MaxHP']
            game.start_expedition(0, 0)
        self.assertIsNone(game.state['Blessing'])
        self.assertNotIn('DamagePct', all_effects(game.state))
        game.player['Gold'] = 0
        game.buy_blessing('mars')
        self.assertIsNone(game.state['Blessing'])
        game.buy_blessing('nope')

    def test_gold_blessing_increases_fight_gold(self):
        game, _ = make_game()
        result = {'GoldGained': 0, 'XPGained': 0, 'LevelsGained': 0, 'Notes': []}
        game.grant_rewards(result, 0, 100, {'GoldPct': 30})
        self.assertEqual(result['GoldGained'], 130)

    def test_honor_shop(self):
        game, _ = make_game()
        p = game.player
        p['Honor'] = 100_000
        capacity = p['InventoryCapacity']
        for _ in range(data.HONOR_SHOP['satchel']['Max'] + 2):
            game.buy_honor('satchel')
        self.assertEqual(p['InventoryCapacity'], capacity + data.HONOR_SHOP['satchel']['Max'] * data.SATCHEL_SLOTS)
        strength = p['BaseStrength']
        game.buy_honor('favor')
        self.assertEqual(p['BaseStrength'], strength + 1)
        game.buy_honor('tribute')
        self.assertEqual(p['Inventory'][-1]['SetId'], 'murmillo')
        rubies = p['Rubies']
        game.buy_honor('ruby')
        self.assertEqual(p['Rubies'], rubies + 1)
        self.assertGreater(game.state['Stats']['HonorSpent'], 0)
        p['Honor'] = 0
        game.buy_honor('ruby')
        self.assertEqual(p['Rubies'], rubies + 1)

    def test_achievements_unlock_once_and_pay_rubies(self):
        game, _ = make_game()
        make_strong(game)
        game.player['CurrentEnergy'] = 99
        rubies = game.player['Rubies']
        game.start_expedition(0, 0)
        unlocked = game.check_achievements()
        self.assertIn('first_blood', [a['Id'] for a in unlocked])
        self.assertGreaterEqual(game.player['Rubies'], rubies + 1)
        self.assertEqual(game.check_achievements(), [])
        self.assertEqual(game.state['Bestiary'][LOCATIONS[0]['Monsters'][0]['Name']], 1)

    def test_view_has_new_sections(self):
        game, _ = make_game()
        v = build_view(game)
        self.assertEqual(len(v['bestiary']), len(data.BESTIARY))
        self.assertEqual(len(v['achievements']), len(data.ACHIEVEMENTS))
        self.assertEqual({w['key'] for w in v['honorShop']}, set(data.HONOR_SHOP))
        self.assertEqual({b['key'] for b in v['temple']['blessings']}, set(data.BLESSINGS))
        self.assertTrue(all('energy' in d and 'treasure' in d for d in v['dungeons']))
        json.dumps(v)


class ProgressionTests(unittest.TestCase):
    def test_xp_curve(self):
        from aeterna.rules import xp_to_next
        self.assertEqual([xp_to_next(n) for n in (1, 2, 3)], [100, 150, 225])
        needs = [xp_to_next(n) for n in range(1, 60)]
        self.assertTrue(all(b > a for a, b in zip(needs, needs[1:])))
        self.assertLess(xp_to_next(50), 1_000_000)  # late levels stay reachable

    def test_bestiary_covers_every_monster(self):
        names = ({m['Name'] for l in LOCATIONS for m in l['Monsters']} | {s['Monster']['Name'] for d in DUNGEONS for s in d['Stages']}
                 | {labor['Monster']['Name'] for labor in data.LABORS})
        self.assertEqual(names, set(data.BESTIARY))

    def test_version_3_save_migrates(self):
        game, _ = make_game()
        raw = json.loads(json.dumps(game.state))
        for key in ('Blessing', 'HonorShop', 'Achievements', 'Bestiary'):
            raw.pop(key, None)
        raw['SaveVersion'] = 3
        raw['Player']['Equipment']['Weapon']['Effects'] = {'LifeSteal': 999, 'Bogus': 3}
        state = normalize_state(raw, START)
        self.assertEqual(state['HonorShop'], {k: 0 for k in data.HONOR_SHOP})
        self.assertEqual((state['Achievements'], state['Bestiary'], state['Blessing']), ([], {}, None))
        self.assertEqual(state['Player']['Equipment']['Weapon']['Effects'], {'LifeSteal': data.EFFECT_CAPS['LifeSteal']})

    def test_balance_entry_level_is_winnable(self):
        from aeterna import balance
        util.rng.seed(2)
        for location in LOCATIONS:
            for monster in location['Monsters']:
                rate = balance.win_rate(monster, location['ReqLevel'], location['ReqLevel'], 30)
                self.assertGreater(rate, 0.4, '%s in %s' % (monster['Name'], location['Name']))


DAY_MS = 86_400_000


class LaborTests(unittest.TestCase):
    def test_labors_in_order_with_permanent_boons(self):
        from aeterna.rules import all_effects
        game, _ = make_game()
        make_strong(game)
        p = game.player
        p['Level'] = 5
        self.assertIsNone(game.attempt_labor(0))  # level 6 needed
        from aeterna.rules import xp_to_next
        p['Level'], p['MaxXP'] = 50, xp_to_next(50)
        self.assertIsNone(game.attempt_labor(1))  # must start with the first
        self.assertIn('in order', game.take_notices()[-1])
        rubies = p['Rubies']
        p['CurrentEnergy'] = p['MaxEnergy']
        result = game.attempt_labor(0)
        self.assertTrue(result['IsVictory'])
        self.assertEqual(p['Labors'], ['labor1'])
        self.assertEqual(p['CurrentEnergy'], p['MaxEnergy'] - data.LABOR_ENERGY_COST)
        self.assertGreaterEqual(p['Rubies'], rubies + data.LABORS[0]['Rubies'])
        self.assertEqual(all_effects(game.state).get('ArmorPct'), 5)
        self.assertIsNone(game.attempt_labor(0))  # can't repeat
        self.assertIn('labor_1', [a['Id'] for a in game.check_achievements()])

    def test_all_labors_grant_the_club(self):
        game, _ = make_game()
        make_strong(game)
        game.player['Level'] = 50
        for i in range(len(data.LABORS)):
            game.player['CurrentHP'] = game.player['MaxHP']
            game.player['CurrentEnergy'] = game.player['MaxEnergy']
            self.assertTrue(game.attempt_labor(i)['IsVictory'])
        self.assertIsNone(game.next_labor_index())
        club = [i for i in game.player['Inventory'] if i['Name'] == data.LABORS_COMPLETE_REWARD['Name']]
        self.assertEqual(len(club), 1)
        self.assertEqual(club[0]['Rarity'], 'Mythic')

    def test_labor_boons_are_capped_and_stack(self):
        from aeterna.rules import labor_effects
        player = {'Labors': [labor['Id'] for labor in data.LABORS]}
        effects = labor_effects(player)
        self.assertEqual(effects['DamagePct'], 10)
        self.assertEqual(effects['HPPct'], 10)

    def test_labors_are_tough_but_fair(self):
        from aeterna import balance
        util.rng.seed(4)
        for labor in data.LABORS[::3]:
            at_entry = balance.labor_win_rate(labor, labor['ReqLevel'], 60)
            later = balance.labor_win_rate(labor, labor['ReqLevel'] + 6, 60)
            self.assertTrue(0.2 < at_entry < 0.8, (labor['Title'], at_entry))
            self.assertGreater(later, at_entry)


class SeriesTests(unittest.TestCase):
    def test_series_fights_until_done(self):
        game, _ = make_game()
        make_strong(game)
        game.player['CurrentEnergy'] = 20
        report = game.start_series(0, 0, 5)
        self.assertTrue(report['Series'])
        self.assertEqual((report['Wins'], len(report['Fights'])), (5, 5))
        self.assertEqual(game.player['CurrentEnergy'], 15)
        self.assertEqual(report['GoldGained'], sum(f['Gold'] for f in report['Fights']))
        self.assertEqual(game.state['Stats']['BestSeries'], 5)

    def test_series_stops_when_energy_runs_out(self):
        game, _ = make_game()
        make_strong(game)
        game.player['CurrentEnergy'] = 2
        report = game.start_series(0, 0, 5)
        self.assertEqual(len(report['Fights']), 2)
        self.assertIn('energy', report['StopReason'])

    def test_series_stops_at_first_defeat(self):
        game, _ = make_game()
        game.player['Level'] = 3
        game.player['CurrentEnergy'] = 20
        report = game.start_series(1, 2, 10)  # a Mountain Troll is too much for a fresh gladiator
        self.assertFalse(report['IsVictory'])
        self.assertFalse(report['Fights'][-1]['IsVictory'])
        self.assertTrue(all(f['IsVictory'] for f in report['Fights'][:-1]))

    def test_series_rejects_bad_sizes(self):
        game, _ = make_game()
        self.assertIsNone(game.start_series(0, 0, 7))
        self.assertIsNone(game.start_series(0, 0, 'x'))


class DailyTests(unittest.TestCase):
    def test_streak_and_rewards(self):
        game, clock = make_game()
        p = game.player
        gold = p['Gold']
        game.claim_daily()
        self.assertEqual(p['Gold'], gold + 120)
        game.claim_daily()  # only once a day
        self.assertEqual(p['Gold'], gold + 120)
        for day in range(2, 8):
            clock.now += DAY_MS
            game.claim_daily()
            self.assertEqual(game.state['Daily']['Streak'], day)
        self.assertTrue(any(i['Rarity'] == 'Epic' for i in p['Inventory']))  # day 7
        self.assertEqual(game.state['Stats']['BestDailyStreak'], 7)
        self.assertIn('daily_7', [a['Id'] for a in game.check_achievements()])

    def test_missing_a_day_restarts(self):
        game, clock = make_game()
        game.claim_daily()
        clock.now += DAY_MS
        game.claim_daily()
        clock.now += 3 * DAY_MS
        self.assertEqual(game.daily_status(), (True, 1))
        game.claim_daily()
        self.assertEqual(game.state['Daily']['Streak'], 1)

    def test_tick_announces_a_new_day(self):
        game, clock = make_game()
        game.claim_daily()
        self.assertEqual(game.tick(), 'none')
        clock.now += DAY_MS
        self.assertEqual(game.tick(), 'all')


class ForgeAndBagTests(unittest.TestCase):
    def _base_stats(self, item):
        """Stats with the current affixes' bonuses taken out."""
        from aeterna.items import _affix_amount
        stats = {a: item[a] for a in data.ATTRIBUTES}
        for names, field in ((PREFIXES, 'Prefix'), (SUFFIXES, 'Suffix')):
            affix = next((a for a in names if a['Name'] == item[field]), None)
            for stat, weight in (affix['Stats'].items() if affix else ()):
                stats[stat] -= weight * _affix_amount(item)
        return stats

    def test_reforge_rerolls_affixes_without_touching_base_stats(self):
        game, _ = make_game(9)
        p, s = game.player, game.state
        item = generate_item(8, 'Amulet', 'Epic')
        p['Inventory'].append(item)
        base = self._base_stats(item)
        p['Gold'], s['RubyStash'], s['BronzeStash'] = 10 ** 6, 100, 100
        for _ in range(30):
            game.reforge(1, len(p['Inventory']) - 1)
            self.assertTrue(item['Prefix'] or item['Suffix'])
            self.assertEqual(self._base_stats(item), base)
        self.assertEqual(s['Stats']['ItemsReforged'], 30)
        self.assertEqual(s['RubyStash'], 70)

    def test_reforge_refuses_sets_mythics_and_poor_smiths(self):
        from aeterna.items import make_set_piece, make_unique
        game, _ = make_game()
        p = game.player
        p['Gold'] = 10 ** 6
        game.state['RubyStash'] = 50
        for item in (make_set_piece('legion', 5), make_unique('Scylla', 5)):
            p['Inventory'].append(item)
            before = dict(item)
            game.reforge(1, len(p['Inventory']) - 1)
            self.assertEqual(item, before)
        p['Inventory'].append(generate_item(5, 'Ring', 'Rare'))
        p['Gold'] = 0
        game.reforge(1, len(p['Inventory']) - 1)
        self.assertEqual(game.state['Stats']['ItemsReforged'], 0)

    def test_no_repeated_words_in_names(self):
        util.rng.seed(3)
        for _ in range(400):
            item = generate_item(5, 'Amulet')
            words = display_name(item).lower().split()
            self.assertEqual(words.count('imperial'), 1 if 'imperial' in words else 0)

    def test_locked_items_are_protected(self):
        game, _ = make_game()
        p = game.player
        p['Inventory'] = [generate_item(1, 'Ring', 'Common')]
        game.toggle_lock(0)
        gold = p['Gold']
        game.sell(0)
        game.smelt(0)
        game.sell_junk()
        self.assertEqual((len(p['Inventory']), p['Gold']), (1, gold))
        game.toggle_lock(0)
        game.sell(0)
        self.assertEqual(p['Inventory'], [])

    def test_sort_inventory(self):
        game, _ = make_game()
        p = game.player
        p['Inventory'] = [make_potion({'Name': 'P', 'HealAmount': 5}), generate_item(1, 'Ring', 'Common'),
                          generate_item(3, 'Weapon', 'Rare'), generate_item(1, 'Weapon', 'Legendary')]
        game.sort_inventory()
        self.assertEqual([(i['Type'], i['Rarity']) for i in p['Inventory']],
                         [('Weapon', 'Legendary'), ('Weapon', 'Rare'), ('Ring', 'Common'), ('Potion', 'Common')])


class ThreatTests(unittest.TestCase):
    def test_estimate_tracks_simulated_fights(self):
        from aeterna import balance, combat
        util.rng.seed(8)
        errors = []
        for location in LOCATIONS[::2]:
            monster = location['Monsters'][-1]
            for offset in (0, 4):
                level = location['ReqLevel'] + offset
                game = balance.typical_game(level)
                enemy = combat.monster_combatant(combat.scale_monster(monster, level, location['ReqLevel']))
                estimate = combat.win_estimate(game.state, enemy)
                wins = sum(combat.run_fight(copy.deepcopy(game.state), 't', dict(enemy))['IsVictory'] for _ in range(80))
                errors.append(abs(estimate - wins / 80))
        self.assertLess(sum(errors) / len(errors), 0.12)

    def test_labels(self):
        from aeterna import combat
        game, _ = make_game()
        weak = combat.monster_combatant(LOCATIONS[0]['Monsters'][0])
        strong = combat.monster_combatant(data.LABORS[-1]['Monster'])
        self.assertIn(combat.threat(game.state, weak)['label'], ('Trivial', 'Easy'))
        self.assertEqual(combat.threat(game.state, strong)['label'], 'Deadly')


class MigrationV5Tests(unittest.TestCase):
    def test_version_4_save_migrates(self):
        game, _ = make_game()
        raw = json.loads(json.dumps(game.state))
        raw.pop('Daily')
        raw['Player'].pop('Labors')
        raw['SaveVersion'] = 4
        state = normalize_state(raw, START)
        self.assertEqual((state['Player']['Labors'], state['Daily']), ([], {'LastDay': -1, 'Streak': 0}))
        self.assertFalse(state['Player']['Inventory'][0]['Locked'])

    def test_labor_list_keeps_only_the_completed_prefix(self):
        game, _ = make_game()
        raw = json.loads(json.dumps(game.state))
        raw['Player']['Labors'] = ['labor1', 'labor3', 'bogus']
        raw['Player']['Inventory'][0]['Locked'] = True
        state = normalize_state(raw, START)
        self.assertEqual(state['Player']['Labors'], ['labor1'])
        self.assertTrue(state['Player']['Inventory'][0]['Locked'])

    def test_level_up_keeps_extra_energy(self):
        game, _ = make_game()
        p = game.player
        p['CurrentEnergy'] = p['MaxEnergy']
        game.gain_xp(p['MaxXP'])
        self.assertEqual(p['CurrentEnergy'], p['MaxEnergy'])


class BagTests(unittest.TestCase):
    def _game(self):
        game, _ = make_game()
        game.player['Inventory'] = []
        return game

    def test_items_take_space_by_type(self):
        from aeterna import bag
        game = self._game()
        p = game.player
        self.assertEqual(bag.dims(p), (data.BAG_COLS, 9))
        armor = generate_item(1, 'Armor', 'Common')
        self.assertTrue(bag.add(p, armor))
        self.assertEqual(armor['Pos'], [0, 0])
        ring = generate_item(1, 'Ring', 'Common')
        bag.add(p, ring)
        self.assertEqual(ring['Pos'], [2, 0])  # next to the 2x3 armor
        self.assertFalse(bag.fits_at(p, generate_item(1, 'Shield', 'Common'), 1, 1))  # overlaps the armor
        self.assertFalse(bag.fits_at(p, generate_item(1, 'Weapon', 'Common'), 0, 7))  # 1x3 runs off the bottom

    def test_a_full_bag_refuses_loot(self):
        from aeterna import bag
        game = self._game()
        p = game.player
        while bag.add(p, generate_item(1, 'Armor', 'Common')):
            pass
        self.assertEqual(len(p['Inventory']), 12)  # four 2x3 pieces per 8x3 band, three bands in 9 rows
        result = {'Loot': [], 'Notes': []}
        while bag.can_add(p, {'Type': 'Ring'}):
            bag.add(p, generate_item(1, 'Ring', 'Common'))
        self.assertFalse(game.give_loot(result, generate_item(1, 'Ring', 'Common')))
        self.assertIn('no room', result['Notes'][0])

    def test_move_equip_and_unequip_to_a_cell(self):
        game = self._game()
        p = game.player
        helm = generate_item(1, 'Helmet', 'Rare')
        game.state['Player']['Inventory'].append(helm)
        game.move_item(0, 6, 7)
        self.assertEqual(helm['Pos'], [6, 7])
        game.move_item(0, 7, 7)  # would stick out of the bag
        self.assertEqual(helm['Pos'], [6, 7])
        game.equip(0)
        self.assertIs(p['Equipment']['Head'], helm)
        self.assertIsNone(helm['Pos'])
        game.unequip('Head', 2, 3)
        self.assertEqual(helm['Pos'], [2, 3])

    def test_swapping_gear_puts_the_old_piece_where_the_new_one_was(self):
        game = self._game()
        p = game.player
        worn = p['Equipment']['Weapon']
        sword = generate_item(1, 'Weapon', 'Rare')
        p['Inventory'].append(sword)
        game.move_item(0, 5, 2)
        game.equip(0)
        self.assertIs(p['Equipment']['Weapon'], sword)
        self.assertEqual(worn['Pos'], [5, 2])

    def test_buy_into_a_chosen_cell(self):
        game = self._game()
        p = game.player
        p['Gold'] = 10 ** 6
        game.buy('Alchemist', 0, 7, 8)
        self.assertEqual(p['Inventory'][-1]['Pos'], [7, 8])
        game.buy('Alchemist', 0, 7, 8)  # taken: goes to the first free cell instead
        self.assertEqual(p['Inventory'][-1]['Pos'], [0, 0])

    def test_sort_packs_the_bag(self):
        from aeterna import bag
        game = self._game()
        p = game.player
        for t, x, y in (('Ring', 7, 8), ('Armor', 4, 5), ('Weapon', 0, 6)):
            item = generate_item(1, t, 'Common')
            item['Pos'] = [x, y]
            p['Inventory'].append(item)
        game.sort_inventory()
        self.assertEqual([(i['Type'], i['Pos']) for i in p['Inventory']], [('Weapon', [0, 0]), ('Armor', [1, 0]), ('Ring', [3, 0])])
        self.assertEqual(bag.overflow(p), [])

    def test_old_saves_get_positions_and_overflow_is_kept(self):
        from aeterna import bag
        game, _ = make_game()
        raw = json.loads(json.dumps(game.state))
        raw['Player']['Inventory'] = [dict(generate_item(1, 'Armor', 'Common'), Pos=None) for _ in range(14)]
        state = normalize_state(raw, START)
        inv = state['Player']['Inventory']
        self.assertEqual(len(inv), 14)
        self.assertEqual(sum(1 for i in inv if i['Pos']), 12)
        self.assertEqual(len(bag.overflow(state['Player'])), 2)

    def test_satchel_adds_a_row(self):
        from aeterna import bag
        game = self._game()
        p = game.player
        p['Honor'] = 10 ** 6
        rows = bag.dims(p)[1]
        game.buy_honor('satchel')
        self.assertEqual(bag.dims(p)[1], rows + 1)


class ContentTests(unittest.TestCase):
    def test_every_recipe_and_dungeon_is_reachable(self):
        for recipe in RECIPES:
            self.assertIn(recipe['ResultType'], data.SLOT_FOR_TYPE)
        for dungeon in DUNGEONS:
            self.assertTrue(dungeon['Stages'][-1]['IsBoss'])

    def test_new_game_state_is_valid_input(self):
        state = new_game_state(START)
        self.assertEqual(normalize_state(json.loads(json.dumps(state)), START)['Player'], state['Player'])


if __name__ == '__main__':
    unittest.main()
