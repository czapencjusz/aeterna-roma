"""Gladiator stat formulas and other derived values."""

import math

from .data import (ARENA_TITLES, BLESSINGS, EFFECT_CAPS, EFFECTS, GUILD_BUILDINGS, MIN_FIGHT_HP_RATIO, SETS, SLOTS,
                   WORK_GOLD_PER_HOUR, WORK_XP_PER_HOUR, XP_EARLY_LEVELS, XP_LATE_GROWTH)
from .util import clamp


def xp_to_next(level):
    """XP needed to go from `level` to `level + 1`."""
    need = 100
    for _ in range(1, min(level, XP_EARLY_LEVELS)):
        need = math.floor(need * 1.5)  # the original x1.5 curve (100, 150, 225, ... 3829 at level 10)
    if level <= XP_EARLY_LEVELS:
        return need
    return math.floor(need * (1 + XP_LATE_GROWTH * (level - XP_EARLY_LEVELS)) ** 2)


# --- Special effects (gear sets, Mythic items, blessings) ---------------------------

def _add_effects(total, effects):
    for key, value in effects.items():
        if key in EFFECTS:
            total[key] = total.get(key, 0) + value


def set_counts(player):
    """How many pieces of each gear set the player is wearing."""
    counts = {}
    for slot in SLOTS:
        item = player['Equipment'][slot]
        if item and item.get('SetId') in SETS:
            counts[item['SetId']] = counts.get(item['SetId'], 0) + 1
    return counts


def gear_effects(player):
    """Effects from equipped Mythic items and active set bonuses."""
    total = {}
    for slot in SLOTS:
        item = player['Equipment'][slot]
        if item and item.get('Effects'):
            _add_effects(total, item['Effects'])
    for set_id, count in set_counts(player).items():
        for needed, effects in SETS[set_id]['Bonuses']:
            if count >= needed:
                _add_effects(total, effects)
    return total


def all_effects(state):
    """Gear effects plus the active temple blessing, with caps applied."""
    total = gear_effects(state['Player'])
    blessing = state.get('Blessing')
    if blessing and blessing.get('Key') in BLESSINGS and blessing.get('FightsLeft', 0) > 0:
        _add_effects(total, BLESSINGS[blessing['Key']]['Effects'])
    for key, cap in EFFECT_CAPS.items():
        if key in total:
            total[key] = min(total[key], cap)
    return total


def has_full_set(player):
    counts = set_counts(player)
    return any(count >= len(SETS[set_id]['Pieces']) for set_id, count in counts.items())


def describe_effects(effects):
    return [EFFECTS[key].format(v=value) for key, value in effects.items() if key in EFFECTS and value]


def equip_bonus(player, stat):
    return sum(item.get(stat, 0) or 0 for item in (player['Equipment'][s] for s in SLOTS) if item)


def total_stat(player, stat):
    return player['Base' + stat] + equip_bonus(player, stat)


def total_armor(player, effects=None):
    effects = gear_effects(player) if effects is None else effects
    return math.floor(equip_bonus(player, 'Armor') * (1 + effects.get('ArmorPct', 0) / 100))


def has_shield(player):
    return bool(player['Equipment']['Shield'])


def _damage_mult(player, effects):
    effects = gear_effects(player) if effects is None else effects
    return 1 + effects.get('DamagePct', 0) / 100


def min_damage(player, effects=None):
    weapon = player['Equipment']['Weapon']
    base = 2 + total_stat(player, 'Strength') // 2 + (weapon['MinDamage'] if weapon else 0)
    return math.floor(base * _damage_mult(player, effects))


def max_damage(player, effects=None):
    weapon = player['Equipment']['Weapon']
    base = (5 + total_stat(player, 'Strength') // 2 + total_stat(player, 'Dexterity') // 3
            + (weapon['MaxDamage'] if weapon else 0))
    return math.floor(base * _damage_mult(player, effects))


def heal_multiplier(player):
    return 1 + total_stat(player, 'Intelligence') * 0.02


def min_fight_hp(player):
    return math.ceil(player['MaxHP'] * MIN_FIGHT_HP_RATIO)


def recalc_stats(player):
    hp_pct = gear_effects(player).get('HPPct', 0)
    player['MaxHP'] = math.floor((100 + total_stat(player, 'Constitution') * 35) * (1 + hp_pct / 100))
    player['CurrentHP'] = clamp(player['CurrentHP'], 0, player['MaxHP'])
    player['CurrentEnergy'] = clamp(player['CurrentEnergy'], 0, player['MaxEnergy'])


def arena_title(rank):
    return next(t['Title'] for t in ARENA_TITLES if rank <= t['MaxRank'])


# --- Guild building bonuses ---------------------------------------------------

def guild_bonus_level(state, key):
    """Level of a guild building (0 when the player has no guild)."""
    guild = state['PlayerGuild']
    return guild['Buildings'][key] if guild['HasGuild'] else 0


def guild_building_cost(level):
    """Vault gold needed to raise a building from `level` to `level + 1`."""
    return 500 * (level + 1) * (level + 1)


def guild_level_from_buildings(buildings):
    return 1 + sum(buildings.values()) // 3


def guild_effect(key, level):
    definition = GUILD_BUILDINGS[key]
    return definition['Effect'].format(pct=level * definition['PerLevel'])


def xp_multiplier(state):
    return 1 + guild_bonus_level(state, 'Library') * 0.05


def work_rates(level):
    """Base villa pay per hour (gold, xp). Grows with level so work stays worth doing."""
    return WORK_GOLD_PER_HOUR + 8 * (level - 1) ** 2, WORK_XP_PER_HOUR + 3 * (level - 1) ** 2


def work_pay(state, hours):
    """Gold and XP for a villa shift of `hours` hours."""
    gold_rate, xp_rate = work_rates(state['Player']['Level'])
    gold = math.floor(hours * gold_rate * (1 + guild_bonus_level(state, 'Villa') * 0.10))
    return gold, hours * xp_rate


def hp_regen_per_min(state):
    player = state['Player']
    regen_pct = all_effects(state).get('RegenPct', 0)
    return ((2 + total_stat(player, 'Constitution') * 0.5) * (1 + guild_bonus_level(state, 'Villa') * 0.10)
            * (1 + regen_pct / 100))


def training_cost(state, base):
    return math.floor((math.floor(base * base * 2.5) + 15) * (1 - guild_bonus_level(state, 'TrainingGrounds') * 0.05))
