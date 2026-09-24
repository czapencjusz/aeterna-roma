"""Turn-based combat: formulas, combatants and the fight loop."""

import math

from .data import MAX_TURNS, SHIELD_BLOCK_BONUS
from .rules import has_shield, max_damage, min_damage, total_armor, total_stat
from .util import clamp, rand_int, roll


# --- Formulas (shared with the Hidden Stats panel) ------------------------------

def hit_chance(att_dex, def_agi):
    return clamp(att_dex / max(1, att_dex + def_agi) * 1.15, 0.15, 0.95)


def block_chance(def_agi, def_str, shield_bonus):
    return min(0.30, def_agi * 0.005 + def_str * 0.003) + shield_bonus


def crit_chance(att_dex, def_agi, att_int):
    return min(0.40, 0.05 + att_dex / max(1, att_dex + def_agi) * 0.12 + att_int * 0.003)


def crit_multiplier(att_int):
    return 1.5 + att_int * 0.015


def armor_penetration(att_str):
    return math.floor(att_str * 0.5)


def mitigation(effective_armor):
    return 100 / (100 + effective_armor * 0.45)


def double_strike_chance(att_cha, def_cha):
    return clamp(att_cha / max(1, att_cha + def_cha) * 0.22, 0.02, 0.30)


# --- Combatants -------------------------------------------------------------------

def player_combatant(player):
    return {
        'name': player['Name'], 'is_player': True, 'hp': player['CurrentHP'],
        'str': total_stat(player, 'Strength'), 'dex': total_stat(player, 'Dexterity'),
        'agi': total_stat(player, 'Agility'), 'cha': total_stat(player, 'Charisma'),
        'int': total_stat(player, 'Intelligence'),
        'armor': total_armor(player), 'min_dmg': min_damage(player), 'max_dmg': max_damage(player),
        'shield_bonus': SHIELD_BLOCK_BONUS if has_shield(player) else 0,
    }


def monster_combatant(monster):
    level = monster['Level']
    return {
        'name': monster['Name'], 'is_player': False, 'hp': monster['MaxHP'],
        'str': level * 3, 'dex': monster['Dexterity'] or level * 3, 'agi': monster['Agility'] or level * 3,
        'cha': level * 2, 'int': level * 2,
        'armor': monster['Armor'], 'min_dmg': monster['MinDamage'], 'max_dmg': monster['MaxDamage'],
        'shield_bonus': 0,
    }


def arena_combatant(opponent):
    return {
        'name': opponent['Name'], 'is_player': False, 'hp': opponent['MaxHP'],
        'str': opponent['Strength'], 'dex': opponent['Dexterity'], 'agi': opponent['Agility'],
        'cha': opponent['Charisma'], 'int': opponent['Intelligence'],
        'armor': opponent['Armor'], 'min_dmg': opponent['MinDamage'], 'max_dmg': opponent['MaxDamage'],
        'shield_bonus': 0,
    }


def scale_monster(monster, player_level, area_req_level):
    """Expedition/dungeon monsters grow with the player once they out-level the area."""
    delta = max(0, player_level - area_req_level)
    scaled = dict(monster)
    if delta == 0:
        return scaled
    scaled.update({
        'Level': monster['Level'] + delta,
        'MaxHP': math.floor(monster['MaxHP'] * (1 + delta * 0.22)),
        'MinDamage': monster['MinDamage'] + delta * 3,
        'MaxDamage': monster['MaxDamage'] + delta * 5,
        'Armor': monster['Armor'] + delta * 3,
        'Dexterity': monster['Dexterity'] + delta * 2,
        'Agility': monster['Agility'] + delta * 2,
        'XPReward': monster['XPReward'] + delta * 12,
        'MinGold': monster['MinGold'] + delta * 10,
        'MaxGold': monster['MaxGold'] + delta * 20,
    })
    return scaled


def arena_opponent_stats(opponent, player):
    """Arena rivals are levelled relative to the player: higher ranks are tougher."""
    level = max(1, player['Level'] + 6 - opponent['Rank'])
    return {
        'Name': opponent['Name'], 'Rank': opponent['Rank'], 'Level': level,
        'Strength': 5 + level * 3, 'Dexterity': 5 + level * 3, 'Agility': 5 + level * 3,
        'Constitution': 5 + level * 3, 'Charisma': level * 3, 'Intelligence': level * 2,
        'MaxHP': 100 + level * 35, 'MinDamage': 4 + level * 4, 'MaxDamage': 8 + level * 5, 'Armor': level * 5,
    }


# --- Fight loop ---------------------------------------------------------------------

def execute_turn(turn_num, att, dfn, turns):
    player = att if att['is_player'] else dfn
    enemy = dfn if att['is_player'] else att

    def log(kind, damage, message):
        # Every log line records both fighters' HP so the report can animate the health bars.
        turns.append({'Turn': turn_num, 'AttackerIsPlayer': att['is_player'], 'Type': kind, 'Damage': damage,
                      'PHP': max(0, player['hp']), 'EHP': max(0, enemy['hp']), 'Message': message})

    if roll() > hit_chance(att['dex'], dfn['agi']):
        log('Miss', 0, '💨 %s attacks %s but MISSES!' % (att['name'], dfn['name']))
        return

    if roll() < block_chance(dfn['agi'], dfn['str'], dfn['shield_bonus']):
        log('Block', 0, "🛡️ %s BLOCKS %s's strike completely!" % (dfn['name'], att['name']))
        return

    damage = rand_int(att['min_dmg'], att['max_dmg'])
    is_crit = roll() < crit_chance(att['dex'], dfn['agi'], att['int'])
    if is_crit:
        damage = math.floor(damage * crit_multiplier(att['int']))

    effective_armor = max(0, dfn['armor'] - armor_penetration(att['str']))
    reduction = mitigation(effective_armor)
    final = max(1, math.floor(damage * reduction))
    dfn['hp'] -= final
    if is_crit:
        log('Critical', final, '💥 CRITICAL HIT! %s strikes %s for %d damage!' % (att['name'], dfn['name'], final))
    else:
        log('Hit', final, '⚔️ %s hits %s for %d damage.' % (att['name'], dfn['name'], final))

    if dfn['hp'] > 0 and roll() < double_strike_chance(att['cha'], dfn['cha']):
        extra = max(1, math.floor(rand_int(att['min_dmg'], att['max_dmg']) * reduction))
        dfn['hp'] -= extra
        log('DoubleStrike', extra,
            "⚡ %s's high Charisma triggers a DOUBLE STRIKE dealing %d extra damage!" % (att['name'], extra))


def run_fight(state, title, enemy):
    """Plays out a whole fight. Updates the player's HP and win/loss statistics."""
    player = state['Player']
    pc = player_combatant(player)
    result = {
        'Title': title, 'PlayerName': player['Name'], 'EnemyName': enemy['name'], 'EnemyArt': '', 'Turns': [],
        'PlayerMaxHP': player['MaxHP'], 'PlayerStartHP': pc['hp'], 'EnemyMaxHP': enemy['hp'],
        'IsVictory': False, 'XPGained': 0, 'GoldGained': 0, 'RubiesGained': 0, 'Loot': [], 'LevelsGained': 0,
        'Notes': [],
    }

    turn = 1
    while pc['hp'] > 0 and enemy['hp'] > 0 and turn <= MAX_TURNS:
        execute_turn(turn, pc, enemy, result['Turns'])
        if enemy['hp'] <= 0:
            break
        execute_turn(turn, enemy, pc, result['Turns'])
        turn += 1

    result['IsVictory'] = pc['hp'] > 0 and enemy['hp'] <= 0
    if not result['IsVictory'] and pc['hp'] > 0:
        result['Notes'].append('After %d rounds the crowd declared %s the winner.' % (MAX_TURNS, enemy['name']))
    player['CurrentHP'] = max(1, pc['hp'])  # defeat leaves you badly hurt, never dead
    state['Stats']['FightsWon' if result['IsVictory'] else 'FightsLost'] += 1
    return result
