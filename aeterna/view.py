"""Builds the data the UI draws from.

Python owns every rule, so the UI never recalculates anything: it receives the
raw state plus all derived numbers (damage, costs, scaled monster levels, ...).
"""

from . import combat
from .data import (ACHIEVEMENTS, ARENA_COOLDOWN_MS, ATTRIBUTES, BESTIARY, BLESSINGS, COMBAT_SPEEDS, DAILY_REWARDS,
                   DUNGEONS, EFFECTS, ENERGY_REGEN_PER_MIN, GUILD_BUILDING_MAX, GUILD_BUILDINGS, GUILD_COST,
                   GUILD_DONATIONS, HONOR_SHOP, LABOR_ENERGY_COST, LABORS, LABORS_COMPLETE_REWARD, LADDER_SIZE,
                   LOCATIONS, MAX_ENHANCE, RECIPES, RUBY_COST, SERIES_SIZES, SETS, SHIELD_BLOCK_BONUS, SLOT_FOR_TYPE,
                   SLOTS, THEMES, UNIQUES, VENDOR_DEFS, WORK_OPTIONS, blessing_cost, reforge_cost)
from .engine import daily_gold, dungeon_energy_cost
from .items import is_equipment, sell_price
from .rules import (all_effects, arena_title, describe_effects, equip_bonus, guild_bonus_level, guild_building_cost,
                    guild_effect, has_shield, hp_regen_per_min, max_damage, min_damage, min_fight_hp, set_counts,
                    total_armor, total_stat, training_cost, work_pay, xp_multiplier)
from .state import dungeon_key, find_monster_by_id, quest_description
from .util import round_half_up

COMPARE_FIELDS = [('MinDamage', 'Min damage'), ('MaxDamage', 'Max damage'), ('Armor', 'Armor')] + [(a, a) for a in ATTRIBUTES]


def _pct(chance):
    return '%.1f%%' % (chance * 100)


def _comparison(player, item):
    """How equipping `item` would change stats compared with what is worn in that slot."""
    if not is_equipment(item):
        return None
    slot = SLOT_FOR_TYPE[item['Type']]
    worn = player['Equipment'][slot]
    if not worn:
        return {'slot': slot, 'worn': False, 'diffs': []}
    diffs = [{'label': label, 'd': (item.get(key) or 0) - (worn.get(key) or 0)} for key, label in COMPARE_FIELDS]
    return {'slot': slot, 'worn': True, 'diffs': [d for d in diffs if d['d'] != 0]}


def _hidden_stats(state):
    p = state['Player']
    effects = all_effects(state)
    strength, dex, agi = total_stat(p, 'Strength'), total_stat(p, 'Dexterity'), total_stat(p, 'Agility')
    con, cha, intel = total_stat(p, 'Constitution'), total_stat(p, 'Charisma'), total_stat(p, 'Intelligence')
    armor, shield, regen = total_armor(p, effects), has_shield(p), hp_regen_per_min(state)
    block_bonus = (SHIELD_BLOCK_BONUS if shield else 0) + effects.get('BlockBonus', 0) / 100
    crit_bonus = effects.get('CritBonus', 0) / 100
    return [
        {'icon': '🛡️', 'title': 'Block Chance',
         'val': _pct(combat.block_chance(agi, strength, block_bonus)),
         'desc': 'From Agility & Strength (max 30%)' + (' + Shield (+8%)' if shield else ' — equip a shield for +8%')
         + (' + %d%% from sets, treasures & blessings' % effects['BlockBonus'] if effects.get('BlockBonus') else '')},
        {'icon': '🎯', 'title': 'Hit Chance', 'val': _pct(combat.hit_chance(dex, agi)),
         'desc': "Your Dexterity vs. the enemy's Agility (15%-95%)"},
        {'icon': '⚡', 'title': 'Critical Strike Chance', 'val': _pct(combat.crit_chance(dex, agi, intel) + crit_bonus),
         'desc': 'From Dexterity & Intelligence (max 40%)'
         + (' + %d%% from sets, treasures & blessings' % effects['CritBonus'] if effects.get('CritBonus') else '')},
        {'icon': '🩸', 'title': 'Life Steal', 'val': '%d%%' % effects.get('LifeSteal', 0),
         'desc': 'Share of your damage returned as HP (from Mythic treasures and sets)'},
        {'icon': '💥', 'title': 'Critical Damage Multiplier', 'val': '%.1f%%' % (combat.crit_multiplier(intel) * 100),
         'desc': '+%.1f%% bonus damage from Intelligence' % (intel * 1.5)},
        {'icon': '⚔️', 'title': 'Double Strike Chance', 'val': _pct(combat.double_strike_chance(cha, cha)),
         'desc': "Your Charisma vs. the enemy's Charisma (2%-30%)"},
        {'icon': '❤️', 'title': 'HP Regeneration Rate', 'val': '+%d HP/h' % round_half_up(regen * 60),
         'desc': '+%.1f HP/min (driven by %d Constitution)' % (regen, con)},
        {'icon': '🔋', 'title': 'Energy Regeneration', 'val': '+%d/min' % ENERGY_REGEN_PER_MIN,
         'desc': 'Energy is spent on expeditions and dungeons'},
        {'icon': '🧪', 'title': 'Healing Potion Bonus', 'val': '+%d%%' % round_half_up(intel * 2),
         'desc': '+2% item healing per Intelligence point'},
        {'icon': '🛡️', 'title': 'Armor Damage Reduction', 'val': _pct(1 - combat.mitigation(armor)),
         'desc': 'Mitigation from %d total Armor (before enemy penetration)' % armor},
        {'icon': '🗡️', 'title': 'Armor Penetration', 'val': '-%d Armor' % combat.armor_penetration(strength),
         'desc': 'Enemy armor bypassed by %d Strength' % strength},
    ]


def _chronicle(stats):
    total = stats['FightsWon'] + stats['FightsLost']
    win_rate = ' (%d%% wins)' % round_half_up(stats['FightsWon'] / total * 100) if total else ''
    return [
        ['⚔️ Fights won / lost', '%d / %d%s' % (stats['FightsWon'], stats['FightsLost'], win_rate)],
        ['🐗 Monsters slain', stats['MonstersSlain']],
        ['🏟️ Arena bouts won / lost', '%d / %d' % (stats['ArenaWins'], stats['ArenaLosses'])],
        ['🏅 Best arena rank', '#%d — %s' % (stats['BestArenaRank'], arena_title(stats['BestArenaRank']))],
        ['🗝️ Dungeon floors cleared', stats['DungeonFloorsCleared']],
        ['🏆 Dungeons conquered', stats['DungeonsConquered']],
        ['🏺 Divine tasks completed', stats['QuestsCompleted']],
        ['💰 Gold earned', '{:,}'.format(stats['GoldEarned'])],
        ['💎 Rubies earned', stats['RubiesEarned']],
        ['🎁 Items looted', stats['ItemsLooted']],
        ['🔨 Items forged', stats['ItemsCrafted']],
        ['✨ Enhancements made', stats['ItemsEnhanced']],
        ['🧩 Set pieces found', stats['SetPiecesFound']],
        ['🌟 Mythic treasures found', stats['UniquesFound']],
        ['🙏 Blessings received', stats['BlessingsReceived']],
        ['🏆 Honor spent', '{:,}'.format(stats['HonorSpent'])],
    ]


def build_view(game, save_path='', seq=0):
    s = game.state
    p = s['Player']
    now = game.clock()
    xp_mult = xp_multiplier(s)

    effects = all_effects(s)
    player = {
        'effects': effects,
        'effectLines': describe_effects(effects),
        'setCounts': set_counts(p),
        'totals': {a: total_stat(p, a) for a in ATTRIBUTES},
        'gearBonus': {a: equip_bonus(p, a) for a in ATTRIBUTES},
        'trainingCosts': [training_cost(s, p['Base' + a]) for a in ATTRIBUTES],
        'minDamage': min_damage(p, effects), 'maxDamage': max_damage(p, effects), 'armor': total_armor(p, effects),
        'title': arena_title(p['ArenaRank']), 'minFightHP': min_fight_hp(p),
    }

    pc = combat.player_combatant(s)

    def rate(enemy):
        return combat.threat(s, enemy, pc)

    inventory = [{'sellPrice': sell_price(item), 'isEquipment': is_equipment(item), 'comparison': _comparison(p, item)}
                 for item in p['Inventory']]

    expeditions = []
    for location in LOCATIONS:
        monsters = []
        for monster in location['Monsters']:
            scaled = combat.scale_monster(monster, p['Level'], location['ReqLevel'])
            monsters.append({'Name': monster['Name'], 'Level': scaled['Level'], 'MaxHP': scaled['MaxHP'],
                             'threat': rate(combat.monster_combatant(scaled))})
        expeditions.append({'Id': location['Id'], 'Name': location['Name'], 'Description': location['Description'],
                            'ReqLevel': location['ReqLevel'], 'EnergyCost': location['EnergyCost'],
                            'locked': p['Level'] < location['ReqLevel'], 'monsters': monsters,
                            'sets': [SETS[k]['Name'] for k in location.get('Sets', [])]})

    dungeons = []
    for dungeon in DUNGEONS:
        progress = s['DungeonProgress'][dungeon_key(dungeon)]
        stage = dungeon['Stages'][progress['CurrentStage'] - 1]
        scaled = combat.scale_monster(stage['Monster'], p['Level'], dungeon['ReqLevel'])
        dungeons.append({'Id': dungeon['Id'], 'Name': dungeon['Name'], 'Description': dungeon['Description'],
                         'ReqLevel': dungeon['ReqLevel'], 'locked': p['Level'] < dungeon['ReqLevel'],
                         'completed': progress['IsCompleted'], 'conquests': progress['Conquests'],
                         'floor': progress['CurrentStage'], 'floors': len(dungeon['Stages']),
                         'stageName': stage['Name'], 'isBoss': stage['IsBoss'],
                         'monster': {'Name': scaled['Name'], 'Level': scaled['Level'], 'MaxHP': scaled['MaxHP'],
                                     'threat': rate(combat.monster_combatant(scaled))},
                         'energy': dungeon_energy_cost(dungeon),
                         'sets': [SETS[k]['Name'] for k in dungeon.get('Sets', [])],
                         'treasure': UNIQUES.get(dungeon['Stages'][-1]['Monster']['Name'], {}).get('Name', '')})

    arena_rows = [{'player': True, 'Rank': p['ArenaRank']}]
    for idx, opponent in enumerate(s['ArenaLadder']):
        rival = combat.arena_opponent_stats(opponent, p)
        arena_rows.append({'player': False, 'idx': idx, 'Name': opponent['Name'], 'Rank': opponent['Rank'],
                           'IconSvg': opponent['IconSvg'], 'Level': rival['Level'],
                           'better': opponent['Rank'] < p['ArenaRank'], 'threat': rate(combat.arena_combatant(rival))})
    arena_rows.sort(key=lambda row: row['Rank'])

    vendors = {key: {'Name': d['Name'], 'Label': d['Label'], 'restocks': bool(d['Stock'])} for key, d in VENDOR_DEFS.items()}

    stash = {'Iron': s['IronStash'], 'Bronze': s['BronzeStash'], 'Ruby': s['RubyStash'], 'Leather': s['LeatherStash']}
    recipes = [dict(r, locked=p['Level'] < r['ReqLevel'],
                    missing=[m for m in stash if stash[m] < r['Req' + m]]) for r in RECIPES]

    enhance = []
    targets = [(item, 0, i, 'Equipped') for i, item in enumerate(p['Equipment'][slot] for slot in SLOTS) if item]
    targets += [(item, 1, i, 'Inventory') for i, item in enumerate(p['Inventory']) if is_equipment(item)]
    for item, location, key, where in targets:
        maxed = item['Upgrade'] >= MAX_ENHANCE
        cost = None if maxed else game.enhance_cost(item)
        reforge = reforge_cost(item['LevelRequirement']) if game.can_reforge(item) else None
        enhance.append({'item': item, 'where': where, 'loc': location,
                        'key': key, 'maxed': maxed, 'next': item['Upgrade'] + 1, 'cost': cost,
                        'affordable': bool(cost) and game.can_afford_enhance(cost),
                        'reforgeCost': reforge,
                        'reforgeAffordable': bool(reforge) and p['Gold'] >= reforge['Gold']
                        and s['BronzeStash'] >= reforge['Bronze'] and s['RubyStash'] >= reforge['Ruby']})

    work = s['ActiveWork']
    work_view = {
        'active': work['IsWorking'], 'endTime': game.work_end_time() if work['IsWorking'] else 0,
        'options': [{'hours': h, 'gold': work_pay(s, h)[0], 'xp': work_pay(s, h)[1]} for h in WORK_OPTIONS],
        'villaBonusPct': guild_bonus_level(s, 'Villa') * 10,
    }

    guild = s['PlayerGuild']
    guild_view = {'cost': GUILD_COST, 'donations': GUILD_DONATIONS, 'buildings': [
        {'key': key, 'Name': d['Name'], 'Icon': d['Icon'], 'level': guild['Buildings'][key], 'max': GUILD_BUILDING_MAX,
         'effect': guild_effect(key, guild['Buildings'][key]) if guild['Buildings'][key] else '',
         'nextEffect': guild_effect(key, guild['Buildings'][key] + 1) if guild['Buildings'][key] < GUILD_BUILDING_MAX else '',
         'cost': guild_building_cost(guild['Buildings'][key])}
        for key, d in GUILD_BUILDINGS.items()]}

    quests = []
    for slot in s['QuestSlots']:
        quest = slot['Quest']
        if not quest:
            quests.append({'empty': True, 'nextAt': slot['NextAt']})
            continue
        if quest['Kind'] == 'monster':
            art = find_monster_by_id(quest['Target'])['Name']
        else:
            art = {'arena': 'gladiator_3', 'dungeon': 'skeleton', 'expedition': 'bandit'}[quest['Kind']]
        quests.append({'empty': False, 'description': quest_description(quest), 'progress': quest['Progress'],
                       'goal': quest['Goal'], 'done': quest['Progress'] >= quest['Goal'], 'art': art,
                       'gold': quest['RewardGold'], 'xp': int(quest['RewardXP'] * xp_mult),
                       'rubies': quest['RewardRubies']})

    next_labor = game.next_labor_index()
    labors = []
    for i, labor in enumerate(LABORS):
        monster = labor['Monster']
        labors.append({'Number': labor['Number'], 'Title': labor['Title'], 'Story': labor['Story'],
                       'ReqLevel': labor['ReqLevel'], 'Gold': labor['Gold'], 'Rubies': labor['Rubies'],
                       'boon': describe_effects(labor['Boon']), 'done': labor['Id'] in p['Labors'],
                       'next': i == next_labor, 'levelLocked': p['Level'] < labor['ReqLevel'],
                       'monster': {'Name': monster['Name'], 'Level': monster['Level'], 'MaxHP': monster['MaxHP']},
                       'threat': rate(combat.monster_combatant(monster))})

    can_claim, streak_day = game.daily_status()
    daily = {'ready': can_claim, 'day': streak_day, 'streak': s['Daily']['Streak'] if not can_claim else streak_day - 1,
             'rewards': [{'Day': r['Day'], 'Icon': r['Icon'], 'Text': r['Text'],
                          'gold': daily_gold(p['Level'], r['Gold']) if r.get('Gold') else 0} for r in DAILY_REWARDS]}

    bestiary_areas = {}
    for location in LOCATIONS:
        for monster in location['Monsters']:
            bestiary_areas[monster['Name']] = location['Name']
    for dungeon in DUNGEONS:
        for stage in dungeon['Stages']:
            bestiary_areas[stage['Monster']['Name']] = dungeon['Name'] + (' (boss)' if stage['IsBoss'] else '')
    for labor in LABORS:
        bestiary_areas[labor['Monster']['Name']] = 'Labor %s of Hercules' % labor['Number']
    bestiary = [{'name': name, 'area': bestiary_areas[name], 'kills': s['Bestiary'].get(name, 0)} for name in BESTIARY]

    achievements = []
    for a in ACHIEVEMENTS:
        value, goal = game.achievement_progress(a)
        achievements.append({'Name': a['Name'], 'Desc': a['Desc'], 'Rubies': a['Rubies'],
                             'done': a['Id'] in s['Achievements'], 'value': min(value, goal), 'goal': goal})

    blessing = s.get('Blessing')
    temple = {
        'cost': blessing_cost(p['Level']),
        'active': dict(blessing, **{k: BLESSINGS[blessing['Key']][k] for k in ('Name', 'Icon')}) if blessing else None,
        'blessings': [{'key': k, 'Name': b['Name'], 'Icon': b['Icon'], 'Fights': b['Fights'],
                       'effects': describe_effects(b['Effects'])} for k, b in BLESSINGS.items()],
    }

    honor_shop = []
    for key, ware in HONOR_SHOP.items():
        bought = s['HonorShop'][key]
        sold_out = ware['Max'] is not None and bought >= ware['Max']
        honor_shop.append({'key': key, 'Name': ware['Name'], 'Icon': ware['Icon'], 'Desc': ware['Desc'],
                           'bought': bought, 'max': ware['Max'], 'soldOut': sold_out,
                           'cost': None if sold_out else game.honor_cost(key)})

    sets = {key: {'Name': d['Name'], 'Sources': d['Sources'],
                  'Pieces': [name for name, _ in d['Pieces'].values()],
                  'Bonuses': [{'pieces': n, 'effects': describe_effects(e)} for n, e in d['Bonuses']]}
            for key, d in SETS.items()}

    return {
        'seq': seq,
        'now': now,
        'bestiary': bestiary,
        'labors': {'list': labors, 'energy': LABOR_ENERGY_COST, 'done': len(p['Labors']),
                   'finalReward': LABORS_COMPLETE_REWARD['Name'],
                   'finalEffects': describe_effects(LABORS_COMPLETE_REWARD['Effects'])},
        'daily': daily,
        'seriesSizes': SERIES_SIZES,
        'achievements': achievements,
        'temple': temple,
        'honorShop': honor_shop,
        'sets': sets,
        'effectText': EFFECTS,
        'state': s,
        'player': player,
        'hiddenStats': _hidden_stats(s),
        'chronicle': _chronicle(s['Stats']),
        'inventory': inventory,
        'expeditions': expeditions,
        'dungeons': dungeons,
        'arena': {'rows': arena_rows, 'cooldownUntil': s['ArenaCooldownUntil'], 'ladderSize': LADDER_SIZE,
                  'cooldownMs': ARENA_COOLDOWN_MS},
        'vendors': vendors,
        'recipes': recipes,
        'enhance': enhance,
        'work': work_view,
        'guild': guild_view,
        'quests': quests,
        'questsReady': sum(1 for q in quests if not q['empty'] and q['done']),
        'rubyCosts': RUBY_COST,
        'themes': THEMES,
        'combatSpeeds': COMBAT_SPEEDS,
        'savePath': save_path,
    }
