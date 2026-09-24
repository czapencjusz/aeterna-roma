"""Gladiator stat formulas and other derived values."""

import math

from .data import (ARENA_TITLES, GUILD_BUILDINGS, MIN_FIGHT_HP_RATIO, SLOTS, WORK_GOLD_PER_HOUR,
                   WORK_XP_PER_HOUR)
from .util import clamp


def equip_bonus(player, stat):
    return sum(item.get(stat, 0) or 0 for item in (player['Equipment'][s] for s in SLOTS) if item)


def total_stat(player, stat):
    return player['Base' + stat] + equip_bonus(player, stat)


def total_armor(player):
    return equip_bonus(player, 'Armor')


def has_shield(player):
    return bool(player['Equipment']['Shield'])


def min_damage(player):
    weapon = player['Equipment']['Weapon']
    return 2 + total_stat(player, 'Strength') // 2 + (weapon['MinDamage'] if weapon else 0)


def max_damage(player):
    weapon = player['Equipment']['Weapon']
    return (5 + total_stat(player, 'Strength') // 2 + total_stat(player, 'Dexterity') // 3
            + (weapon['MaxDamage'] if weapon else 0))


def heal_multiplier(player):
    return 1 + total_stat(player, 'Intelligence') * 0.02


def min_fight_hp(player):
    return math.ceil(player['MaxHP'] * MIN_FIGHT_HP_RATIO)


def recalc_stats(player):
    player['MaxHP'] = 100 + total_stat(player, 'Constitution') * 35
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


def work_pay(state, hours):
    """Gold and XP for a villa shift of `hours` hours."""
    gold = math.floor(hours * WORK_GOLD_PER_HOUR * (1 + guild_bonus_level(state, 'Villa') * 0.10))
    return gold, hours * WORK_XP_PER_HOUR


def hp_regen_per_min(state):
    player = state['Player']
    return (2 + total_stat(player, 'Constitution') * 0.5) * (1 + guild_bonus_level(state, 'Villa') * 0.10)


def training_cost(state, base):
    return math.floor((math.floor(base * base * 2.5) + 15) * (1 - guild_bonus_level(state, 'TrainingGrounds') * 0.05))
