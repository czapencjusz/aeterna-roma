"""Turn-based combat: formulas, combatants and the fight loop."""

import math

from .data import MAX_TURNS, MONSTER_SCALING, SHIELD_BLOCK_BONUS
from .rules import all_effects, has_shield, max_damage, min_damage, total_armor, total_stat
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

def player_combatant(state):
    """The player as a fighter, including gear-set, Mythic and blessing effects."""
    player = state['Player']
    effects = all_effects(state)
    return {
        'name': player['Name'], 'is_player': True, 'hp': player['CurrentHP'], 'max_hp': player['MaxHP'],
        'str': total_stat(player, 'Strength'), 'dex': total_stat(player, 'Dexterity'),
        'agi': total_stat(player, 'Agility'), 'cha': total_stat(player, 'Charisma'),
        'int': total_stat(player, 'Intelligence'),
        'armor': total_armor(player, effects), 'min_dmg': min_damage(player, effects),
        'max_dmg': max_damage(player, effects),
        'shield_bonus': (SHIELD_BLOCK_BONUS if has_shield(player) else 0) + effects.get('BlockBonus', 0) / 100,
        'crit_bonus': effects.get('CritBonus', 0) / 100,
        'life_steal': effects.get('LifeSteal', 0) / 100,
    }


def monster_combatant(monster):
    level = monster['Level']
    return {
        'name': monster['Name'], 'is_player': False, 'hp': monster['MaxHP'], 'max_hp': monster['MaxHP'],
        'str': level * 3, 'dex': monster['Dexterity'] or level * 3, 'agi': monster['Agility'] or level * 3,
        'cha': level * 2, 'int': level * 2,
        'armor': monster['Armor'], 'min_dmg': monster['MinDamage'], 'max_dmg': monster['MaxDamage'],
        'shield_bonus': 0,
    }


def arena_combatant(opponent):
    return {
        'name': opponent['Name'], 'is_player': False, 'hp': opponent['MaxHP'], 'max_hp': opponent['MaxHP'],
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
    scaled['Level'] = monster['Level'] + delta
    scaled['MaxHP'] = math.floor(monster['MaxHP'] * (1 + delta * MONSTER_SCALING['HP']))
    for key in ('MinDamage', 'MaxDamage', 'Armor', 'Dexterity', 'Agility', 'XPReward', 'MinGold', 'MaxGold'):
        scaled[key] = monster[key] + delta * MONSTER_SCALING[key]
    return scaled


def arena_opponent_stats(opponent, player):
    """Arena rivals are levelled relative to the player: higher ranks are tougher."""
    level = max(1, player['Level'] + 6 - opponent['Rank'])
    return {
        'Name': opponent['Name'], 'Rank': opponent['Rank'], 'Level': level,
        'Strength': 5 + level * 5 // 2, 'Dexterity': 5 + level * 5 // 2, 'Agility': 5 + level * 5 // 2,
        'Constitution': 5 + level * 5 // 2, 'Charisma': level * 3, 'Intelligence': level * 2,
        'MaxHP': 100 + level * 35, 'MinDamage': 4 + level * 4, 'MaxDamage': 8 + level * 5, 'Armor': level * 5,
    }


# --- Threat estimate ------------------------------------------------------------------

def expected_damage_per_turn(att, dfn):
    """Average damage `att` deals to `dfn` in one turn, following execute_turn's rules."""
    p_hit = hit_chance(att['dex'], dfn['agi'])
    p_block = min(1.0, block_chance(dfn['agi'], dfn['str'], dfn['shield_bonus']))
    p_crit = min(1.0, crit_chance(att['dex'], dfn['agi'], att['int']) + att.get('crit_bonus', 0))
    reduction = mitigation(max(0, dfn['armor'] - armor_penetration(att['str'])))
    base = max(1.0, (att['min_dmg'] + att['max_dmg']) / 2 * reduction)
    per_hit = base * (1 + p_crit * (crit_multiplier(att['int']) - 1))
    return p_hit * (1 - p_block) * (per_hit + double_strike_chance(att['cha'], dfn['cha']) * base)


# Labels from easiest to hardest, with the lowest estimated win chance each one covers.
THREAT_LEVELS = [(0.95, 'Trivial'), (0.80, 'Easy'), (0.55, 'Fair'), (0.30, 'Risky'), (0.0, 'Deadly')]


def turns_to_win(state, enemy, pc=None):
    """(turns the player needs to beat `enemy`, turns `enemy` needs to beat the player at full health).

    Pass `pc` (from player_combatant) when rating many enemies, to build it only once.
    """
    pc = dict(pc or player_combatant(state), hp=None)
    pc['hp'] = pc['max_hp']
    mine = max(0.01, expected_damage_per_turn(pc, enemy))
    theirs = max(0.01, expected_damage_per_turn(enemy, pc) - mine * pc.get('life_steal', 0))
    return enemy['hp'] / mine, pc['hp'] / theirs


def _sigmoid(x):
    return 1 / (1 + math.exp(-max(-60.0, min(60.0, x))))


# Fitted to simulated fights by `python -m aeterna.balance --calibrate` (RMS error about 3%).
THREAT_SLOPE, THREAT_SHIFT, THREAT_TIMEOUT = 3.4, -0.78, 0.25


def win_chance_from_turns(player_turns, enemy_turns):
    """Win chance from the turn counts: who finishes the other first, and whether the player can
    finish the enemy before the crowd calls the fight after MAX_TURNS rounds."""
    duel = _sigmoid(THREAT_SLOPE * (math.log(enemy_turns / player_turns) - THREAT_SHIFT))
    return duel * _sigmoid(THREAT_TIMEOUT * (MAX_TURNS - player_turns))


def win_estimate(state, enemy, pc=None):
    """Rough chance (0-1) that the player, at full health, beats `enemy`, without simulating the fight."""
    return win_chance_from_turns(*turns_to_win(state, enemy, pc))


def threat(state, enemy, pc=None):
    """{'label', 'win'} for the interface: a difficulty label and the estimated win chance (0-100)."""
    win = win_estimate(state, enemy, pc)
    label = next(name for floor, name in THREAT_LEVELS if win >= floor)
    return {'label': label, 'win': round(win * 100)}


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
    is_crit = roll() < crit_chance(att['dex'], dfn['agi'], att['int']) + att.get('crit_bonus', 0)
    if is_crit:
        damage = math.floor(damage * crit_multiplier(att['int']))

    effective_armor = max(0, dfn['armor'] - armor_penetration(att['str']))
    reduction = mitigation(effective_armor)
    final = max(1, math.floor(damage * reduction))
    dfn['hp'] -= final
    healed = _life_steal(att, final)
    drain = ' (drains %d HP)' % healed if healed else ''
    if is_crit:
        log('Critical', final, '💥 CRITICAL HIT! %s strikes %s for %d damage!%s' % (att['name'], dfn['name'], final, drain))
    else:
        log('Hit', final, '⚔️ %s hits %s for %d damage.%s' % (att['name'], dfn['name'], final, drain))

    if dfn['hp'] > 0 and roll() < double_strike_chance(att['cha'], dfn['cha']):
        extra = max(1, math.floor(rand_int(att['min_dmg'], att['max_dmg']) * reduction))
        dfn['hp'] -= extra
        _life_steal(att, extra)
        log('DoubleStrike', extra,
            "⚡ %s's high Charisma triggers a DOUBLE STRIKE dealing %d extra damage!" % (att['name'], extra))


def _life_steal(att, damage):
    """Heals the attacker by their life-steal share of `damage`. Returns the HP healed."""
    share = att.get('life_steal', 0)
    if not share or att['hp'] <= 0:
        return 0
    healed = min(math.floor(damage * share), att['max_hp'] - att['hp'])
    att['hp'] += max(0, healed)
    return max(0, healed)


def run_fight(state, title, enemy):
    """Plays out a whole fight. Updates the player's HP and win/loss statistics."""
    player = state['Player']
    pc = player_combatant(state)
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
