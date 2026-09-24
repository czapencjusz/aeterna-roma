"""Game-state creation, Pantheon quest generation and save-file migration.

The state is a plain JSON-compatible dict. It uses the same field names as the
earlier browser version, so save files exported from that version (or the even
older C# server version) can be imported.
"""

import math
import re

from .data import (ACHIEVEMENTS, ALCHEMIST_ITEMS, ARENA_COOLDOWN_MS, ARENA_MILESTONES, ARENA_NAMES, ATTRIBUTES,
                   BESTIARY, BLESSINGS, COMBAT_SPEEDS, DUNGEONS, GUILD_BUILDING_MAX, GUILD_BUILDINGS, HONOR_SHOP,
                   LADDER_SIZE, LOCATIONS, QUEST_ABANDON_WAIT_MS, QUEST_KINDS, QUEST_SLOTS, SAVE_VERSION, SLOT_FOR_TYPE,
                   SLOTS, STAT_KEYS, THEMES, VENDOR_DEFS, VENDOR_STOCK_SIZE, WORK_OPTIONS)
from .items import blank_item, generate_item, make_potion, normalize_item
from .rules import guild_level_from_buildings, recalc_stats, work_rates, xp_to_next
from .util import clamp, is_number, pick, rand_int, roll, text, to_int, uid


# --- New-game building blocks --------------------------------------------------------

def new_player():
    return {
        'Name': 'Flavius', 'Level': 1, 'XP': 0, 'MaxXP': 100,
        'Gold': 250, 'Rubies': 10, 'Honor': 50, 'ArenaRank': 10,
        'BaseStrength': 5, 'BaseDexterity': 5, 'BaseAgility': 5,
        'BaseConstitution': 5, 'BaseCharisma': 5, 'BaseIntelligence': 5,
        'CurrentHP': 0, 'MaxHP': 0, 'CurrentEnergy': 24, 'MaxEnergy': 24,
        'Equipment': {slot: None for slot in SLOTS}, 'Inventory': [], 'InventoryCapacity': 24,
    }


def new_guild():
    return {'HasGuild': False, 'Name': '', 'Tag': '', 'Level': 0, 'GoldVault': 0,
            'Buildings': {key: 0 for key in GUILD_BUILDINGS}, 'Log': []}


def new_stats():
    stats = {key: 0 for key in STAT_KEYS}
    stats['BestArenaRank'] = LADDER_SIZE
    return stats


def idle_work():
    return {'IsWorking': False, 'DurationHours': 0, 'StartTime': 0, 'ExpectedGold': 0, 'ExpectedXP': 0}


def new_quest_slots():
    return [{'Quest': None, 'NextAt': 0} for _ in range(QUEST_SLOTS)]


def build_ladder(player_rank):
    """20 named rivals holding every rank from 1 to 21 except the player's."""
    ladder = []
    rank = 1
    for i, name in enumerate(ARENA_NAMES):
        if rank == player_rank:
            rank += 1
        ladder.append({'Id': 'arena_%d' % (i + 1), 'Name': name, 'Rank': rank, 'IconSvg': 'gladiator_%d' % (i % 4 + 1)})
        rank += 1
    return ladder


def is_ladder_valid(ladder, player_rank):
    if not isinstance(ladder, list) or len(ladder) != len(ARENA_NAMES):
        return False
    seen = {player_rank}
    for opponent in ladder:
        if not opponent or not isinstance(opponent.get('Id'), str) or not isinstance(opponent.get('Name'), str):
            return False
        rank = opponent.get('Rank')
        if not isinstance(rank, int) or rank < 1 or rank > LADDER_SIZE or rank in seen:
            return False
        seen.add(rank)
    return True


def stock_vendor(key, level):
    definition = VENDOR_DEFS[key]
    if not definition['Stock']:
        # The apothecary's fixed potion list, with stable ids.
        return [make_potion(dict(item, Id='alchemist_%d' % i)) for i, item in enumerate(ALCHEMIST_ITEMS)]
    return [generate_item(level, pick(definition['Stock'])) for _ in range(VENDOR_STOCK_SIZE)]


def dungeon_key(dungeon):
    """Dungeon progress is stored under string keys (JSON object keys are always strings)."""
    return str(dungeon['Id'])


def new_game_state(now):
    player = new_player()
    player['Equipment']['Weapon'] = dict(blank_item(), Name='Iron Gladius', Type='Weapon', MinDamage=4, MaxDamage=8,
                                         Price=45, IconSvg='weapon_1', SmeltIron=2, SmeltBronze=1, SmeltLeather=1)
    player['Equipment']['Chest'] = dict(blank_item(), Name='Tunic of Rome', Type='Armor', Armor=10, Price=45,
                                        IconSvg='armor_1', SmeltIron=1, SmeltBronze=1, SmeltLeather=2)
    player['Inventory'].append(make_potion({'Name': 'Health Potion', 'HealAmount': 50, 'Price': 20, 'IconSvg': 'potion_red'}))
    recalc_stats(player)
    player['CurrentHP'] = player['MaxHP']

    state = {
        'Version': SAVE_VERSION,
        'Player': player,
        'Vendors': {key: {'Items': stock_vendor(key, player['Level'])} for key in VENDOR_DEFS},
        'ArenaLadder': build_ladder(player['ArenaRank']),
        'DungeonProgress': {dungeon_key(d): {'CurrentStage': 1, 'IsCompleted': False, 'Conquests': 0} for d in DUNGEONS},
        'ActiveWork': idle_work(),
        'PlayerGuild': new_guild(),
        'IronStash': 10, 'BronzeStash': 10, 'RubyStash': 5, 'LeatherStash': 10,
        'LastHPRegen': now,
        'LastEnergyRegen': now,
        'ArenaCooldownUntil': 0,
        'ArenaMilestonesClaimed': [],
        'QuestSlots': new_quest_slots(),
        'Stats': new_stats(),
        'Blessing': None,  # {'Key': <data.BLESSINGS key>, 'FightsLeft': n}
        'HonorShop': {key: 0 for key in HONOR_SHOP},  # how many of each Honor-shop ware were bought
        'Achievements': [],  # ids of unlocked achievements
        'Bestiary': {},  # creature name -> times defeated
        'Settings': {'ThemeMode': 'DarkImperial', 'AudioMuted': False, 'CombatSpeed': 'Fast'},
    }
    for slot in state['QuestSlots']:
        slot['Quest'] = generate_quest(player)
    state['Stats']['BestArenaRank'] = player['ArenaRank']
    return state


# --- Pantheon quests -------------------------------------------------------------------

def find_monster_by_id(monster_id):
    for location in LOCATIONS:
        for monster in location['Monsters']:
            if monster['Id'] == monster_id:
                return monster
    return None


def _quest_reward(goal, level, low_gold, low_xp, factor):
    """Per-goal rewards: the old linear formula early on, and a share of a typical fight's reward later."""
    gold = max(low_gold, 0.8 * 2.6 * level * level)
    xp = max(low_xp, 0.8 * 2.8 * level * level)
    return math.floor(goal * gold * factor), math.floor(goal * xp * factor)


def generate_quest(player):
    level = player['Level']
    kinds = ['expedition', 'expedition', 'monster', 'monster', 'arena']
    if any(level >= d['ReqLevel'] for d in DUNGEONS):
        kinds.append('dungeon')
    kind = pick(kinds)
    quest = {'Id': uid(), 'Kind': kind, 'Target': '', 'Goal': 1, 'Progress': 0,
             'RewardGold': 0, 'RewardXP': 0, 'RewardRubies': 0}
    if kind == 'expedition':
        quest['Goal'] = rand_int(3, 6)
        quest['RewardGold'], quest['RewardXP'] = _quest_reward(quest['Goal'], level, 15 + level * 12, 10 + level * 6, 1)
    elif kind == 'monster':
        # Hunt a monster from one of the three highest regions the player can enter.
        open_regions = [loc for loc in LOCATIONS if level >= loc['ReqLevel']]
        location = pick(sorted(open_regions, key=lambda loc: loc['ReqLevel'])[-3:])
        quest['Target'] = pick(location['Monsters'])['Id']
        quest['Goal'] = rand_int(2, 4)
        quest['RewardGold'], quest['RewardXP'] = _quest_reward(quest['Goal'], level, 15 + level * 12, 10 + level * 6, 1.3)
    elif kind == 'arena':
        quest['Goal'] = rand_int(1, 3)
        quest['RewardGold'], quest['RewardXP'] = _quest_reward(quest['Goal'], level, 40 + level * 20, 20 + level * 8, 1.5)
    else:  # dungeon
        quest['Goal'] = rand_int(1, 2)
        quest['RewardGold'], quest['RewardXP'] = _quest_reward(quest['Goal'], level, 80 + level * 30, 40 + level * 10, 2)
    quest['RewardRubies'] = 1 if roll() < (0.5 if kind == 'dungeon' else 0.25) else 0
    return quest


def normalize_quest(raw):
    if not isinstance(raw, dict) or raw.get('Kind') not in QUEST_KINDS:
        return None
    if raw['Kind'] == 'monster' and not find_monster_by_id(raw.get('Target')):
        return None
    goal = clamp(to_int(raw.get('Goal'), 1), 1, 20)
    return {
        'Id': raw['Id'][:60] if isinstance(raw.get('Id'), str) else uid(),
        'Kind': raw['Kind'],
        'Target': raw['Target'] if raw['Kind'] == 'monster' else '',
        'Goal': goal,
        'Progress': clamp(to_int(raw.get('Progress'), 0), 0, goal),
        'RewardGold': clamp(to_int(raw.get('RewardGold'), 0), 0, 10000000),
        'RewardXP': clamp(to_int(raw.get('RewardXP'), 0), 0, 10000000),
        'RewardRubies': clamp(to_int(raw.get('RewardRubies'), 0), 0, 3),
    }


def quest_description(quest):
    goal = quest['Goal']
    if quest['Kind'] == 'expedition':
        return 'Win %d expedition fights' % goal
    if quest['Kind'] == 'monster':
        return 'Defeat the %s %d times' % (find_monster_by_id(quest['Target'])['Name'], goal)
    if quest['Kind'] == 'arena':
        return 'Win %d arena bout%s' % (goal, 's' if goal > 1 else '')
    return 'Clear %d dungeon floor%s' % (goal, 's' if goal > 1 else '')


# --- Save migration ----------------------------------------------------------------------

def _normalize_player(state, raw_player):
    player = state['Player']
    rp = raw_player
    if isinstance(rp.get('Name'), str) and rp['Name'].strip():
        player['Name'] = rp['Name'].strip()[:24]
    player['Level'] = clamp(to_int(rp.get('Level'), player['Level']), 1, 100)
    player['MaxXP'] = xp_to_next(player['Level'])  # always follows the current XP curve
    player['XP'] = clamp(to_int(rp.get('XP'), 0), 0, player['MaxXP'] - 1)
    for key in ('Gold', 'Rubies', 'Honor'):
        player[key] = max(0, to_int(rp.get(key), player[key]))
    player['ArenaRank'] = clamp(to_int(rp.get('ArenaRank'), player['ArenaRank']), 1, LADDER_SIZE)
    for attr in ATTRIBUTES:
        player['Base' + attr] = max(1, to_int(rp.get('Base' + attr), player['Base' + attr]))
    player['MaxEnergy'] = max(1, to_int(rp.get('MaxEnergy'), player['MaxEnergy']))
    player['CurrentEnergy'] = to_int(rp.get('CurrentEnergy'), player['MaxEnergy'])
    player['InventoryCapacity'] = clamp(to_int(rp.get('InventoryCapacity'), player['InventoryCapacity']), 1, 100)

    player['Inventory'] = []
    raw_equipment = rp.get('Equipment') if isinstance(rp.get('Equipment'), dict) else {}
    for slot in SLOTS:
        item = normalize_item(raw_equipment.get(slot))
        player['Equipment'][slot] = None
        if not item:
            continue
        if SLOT_FOR_TYPE.get(item['Type']) == slot:
            player['Equipment'][slot] = item
        else:
            player['Inventory'].append(item)  # item was in the wrong slot; move it to the bag
    if isinstance(rp.get('Inventory'), list):
        player['Inventory'].extend(item for item in map(normalize_item, rp['Inventory']) if item)

    recalc_stats(player)
    player['CurrentHP'] = to_int(rp.get('CurrentHP'), player['MaxHP'])
    recalc_stats(player)


def _normalize_ladder(raw_ladder, player_rank):
    if not isinstance(raw_ladder, list):
        return build_ladder(player_rank)
    ladder = []
    for opponent in raw_ladder:
        if not isinstance(opponent, dict):
            ladder.append(None)
            continue
        opp_id = text(opponent.get('Id'), 40)
        name = text(opponent.get('Name'), 40)
        # Built-in rivals always use the current roster name (the old "Flavius" rival is now "Priscus").
        match = re.fullmatch(r'arena_(\d+)', opp_id)
        if match and 1 <= int(match.group(1)) <= len(ARENA_NAMES):
            name = ARENA_NAMES[int(match.group(1)) - 1]
        ladder.append({'Id': opp_id, 'Name': name, 'Rank': to_int(opponent.get('Rank'), 0),
                       'IconSvg': text(opponent.get('IconSvg'), 40)})
    return ladder if is_ladder_valid(ladder, player_rank) else build_ladder(player_rank)


def _normalize_guild(raw_guild):
    guild = new_guild()
    if not isinstance(raw_guild, dict) or raw_guild.get('HasGuild') is not True:
        return guild
    guild['HasGuild'] = True
    guild['Name'] = text(raw_guild.get('Name'), 24) or 'Guild'
    guild['Tag'] = text(raw_guild.get('Tag'), 5)
    guild['GoldVault'] = max(0, to_int(raw_guild.get('GoldVault'), 0))
    raw_buildings = raw_guild.get('Buildings') if isinstance(raw_guild.get('Buildings'), dict) else None
    # Old C# saves stored TrainingGroundLevel / LibraryLevel / VillaLevel, starting at level 1 with no effect.
    legacy = {'TrainingGrounds': raw_guild.get('TrainingGroundLevel'), 'Library': raw_guild.get('LibraryLevel'),
              'Villa': raw_guild.get('VillaLevel')}
    for key in guild['Buildings']:
        if raw_buildings is not None and key in raw_buildings:
            value = to_int(raw_buildings[key], 0)
        else:
            value = to_int(legacy[key], 0) - (0 if raw_buildings is not None else 1)
        guild['Buildings'][key] = clamp(value, 0, GUILD_BUILDING_MAX)
    guild['Level'] = guild_level_from_buildings(guild['Buildings'])
    if isinstance(raw_guild.get('Log'), list):
        guild['Log'] = [entry[:200] for entry in raw_guild['Log'] if isinstance(entry, str)][-50:]
    return guild


def normalize_state(raw, now):
    """Builds a valid game state from any save format, filling in defaults for anything missing."""
    state = new_game_state(now)
    if not isinstance(raw, dict) or not isinstance(raw.get('Player'), dict):
        return state

    _normalize_player(state, raw['Player'])
    player = state['Player']

    # Vendors (the apothecary always has its fixed potion list)
    raw_vendors = raw.get('Vendors') if isinstance(raw.get('Vendors'), dict) else {}
    for key, definition in VENDOR_DEFS.items():
        raw_vendor = raw_vendors.get(key)
        if definition['Stock'] and isinstance(raw_vendor, dict) and isinstance(raw_vendor.get('Items'), list):
            items = [item for item in map(normalize_item, raw_vendor['Items']) if item]
            if items:
                state['Vendors'][key] = {'Items': items}

    state['ArenaLadder'] = _normalize_ladder(raw.get('ArenaLadder'), player['ArenaRank'])

    # Dungeon progress (newer saves: DungeonProgress map; C# saves: Dungeons list)
    raw_progress = raw.get('DungeonProgress') if isinstance(raw.get('DungeonProgress'), dict) else {}
    raw_dungeons = raw.get('Dungeons') if isinstance(raw.get('Dungeons'), list) else []
    for dungeon in DUNGEONS:
        entry = raw_progress.get(dungeon_key(dungeon))
        if not isinstance(entry, dict):
            entry = next((d for d in raw_dungeons if isinstance(d, dict) and to_int(d.get('Id'), -1) == dungeon['Id']), None)
        if isinstance(entry, dict):
            completed = entry.get('IsCompleted') is True
            state['DungeonProgress'][dungeon_key(dungeon)] = {
                'CurrentStage': clamp(to_int(entry.get('CurrentStage'), 1), 1, len(dungeon['Stages'])),
                'IsCompleted': completed,
                'Conquests': max(1 if completed else 0, to_int(entry.get('Conquests'), 0)),
            }

    # Villa work
    raw_work = raw.get('ActiveWork')
    if (isinstance(raw_work, dict) and raw_work.get('IsWorking') is True
            and to_int(raw_work.get('DurationHours'), 0) in WORK_OPTIONS and is_number(raw_work.get('StartTime'))):
        hours = to_int(raw_work['DurationHours'], 0)
        gold_rate, xp_rate = work_rates(player['Level'])
        base_gold, _ = work_rates(1)
        max_gold = math.floor(hours * gold_rate * (1 + GUILD_BUILDING_MAX * 0.10))
        state['ActiveWork'] = {
            'IsWorking': True, 'DurationHours': hours, 'StartTime': min(int(raw_work['StartTime']), now),
            'ExpectedGold': clamp(to_int(raw_work.get('ExpectedGold'), 0), hours * base_gold, max_gold),
            'ExpectedXP': clamp(to_int(raw_work.get('ExpectedXP'), 0), hours * work_rates(1)[1], hours * xp_rate),
        }

    state['PlayerGuild'] = _normalize_guild(raw.get('PlayerGuild'))

    for key in ('IronStash', 'BronzeStash', 'RubyStash', 'LeatherStash'):
        state[key] = max(0, to_int(raw.get(key), state[key]))

    # Timers are epoch milliseconds. C# saves used .NET date strings: those restart from now.
    def timestamp(value):
        return value if is_number(value) and value <= now else now
    state['LastHPRegen'] = timestamp(raw.get('LastHPRegen'))
    state['LastEnergyRegen'] = timestamp(raw.get('LastEnergyRegen'))
    cooldown = raw.get('ArenaCooldownUntil')
    state['ArenaCooldownUntil'] = clamp(int(cooldown), 0, now + ARENA_COOLDOWN_MS) if is_number(cooldown) else 0

    raw_settings = raw.get('Settings')
    if isinstance(raw_settings, dict):
        if raw_settings.get('ThemeMode') in THEMES:
            state['Settings']['ThemeMode'] = raw_settings['ThemeMode']
        state['Settings']['AudioMuted'] = raw_settings.get('AudioMuted') is True
        if raw_settings.get('CombatSpeed') in COMBAT_SPEEDS:
            state['Settings']['CombatSpeed'] = raw_settings['CombatSpeed']

    # Lifetime statistics
    if isinstance(raw.get('Stats'), dict):
        for key in STAT_KEYS:
            state['Stats'][key] = max(0, to_int(raw['Stats'].get(key), 0))
        state['Stats']['BestArenaRank'] = clamp(to_int(raw['Stats'].get('BestArenaRank'), player['ArenaRank']), 1, LADDER_SIZE)
    state['Stats']['BestArenaRank'] = min(state['Stats']['BestArenaRank'], player['ArenaRank'])

    if isinstance(raw.get('ArenaMilestonesClaimed'), list):
        claimed = raw['ArenaMilestonesClaimed']
        state['ArenaMilestonesClaimed'] = [m['Rank'] for m in ARENA_MILESTONES if m['Rank'] in claimed]

    # Quest slots: keep valid quests, replace anything unrecognised with a fresh one
    raw_slots = raw.get('QuestSlots') if isinstance(raw.get('QuestSlots'), list) else []
    slots = []
    for i in range(QUEST_SLOTS):
        raw_slot = raw_slots[i] if i < len(raw_slots) else None
        if not isinstance(raw_slot, dict):
            slots.append({'Quest': generate_quest(player), 'NextAt': 0})
            continue
        quest = normalize_quest(raw_slot.get('Quest'))
        if quest:
            slots.append({'Quest': quest, 'NextAt': 0})
            continue
        next_at = to_int(raw_slot.get('NextAt'), 0)
        if raw_slot.get('Quest') is None and next_at > now:
            slots.append({'Quest': None, 'NextAt': min(next_at, now + QUEST_ABANDON_WAIT_MS)})
        else:
            slots.append({'Quest': generate_quest(player), 'NextAt': 0})
    state['QuestSlots'] = slots

    # Blessing, Honor shop, achievements and Bestiary (added in save version 4)
    blessing = raw.get('Blessing')
    if isinstance(blessing, dict) and blessing.get('Key') in BLESSINGS:
        fights = clamp(to_int(blessing.get('FightsLeft'), 0), 0, BLESSINGS[blessing['Key']]['Fights'])
        state['Blessing'] = {'Key': blessing['Key'], 'FightsLeft': fights} if fights else None
    if isinstance(raw.get('HonorShop'), dict):
        for key, ware in HONOR_SHOP.items():
            state['HonorShop'][key] = clamp(to_int(raw['HonorShop'].get(key), 0), 0, ware['Max'] or 1000000)
    if isinstance(raw.get('Achievements'), list):
        state['Achievements'] = [a['Id'] for a in ACHIEVEMENTS if a['Id'] in raw['Achievements']]
    if isinstance(raw.get('Bestiary'), dict):
        state['Bestiary'] = {name: max(0, to_int(raw['Bestiary'].get(name), 0)) for name in BESTIARY
                             if to_int(raw['Bestiary'].get(name), 0) > 0}
    return state
