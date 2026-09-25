"""Balance simulator: plays thousands of fights to measure difficulty.

Run:  python -m aeterna.balance              (full report)
      python -m aeterna.balance --fights 100 (faster, rougher)
      python -m aeterna.balance --calibrate  (fit the threat estimate shown in the interface)

For each region and dungeon it builds a "typical" gladiator at the area's entry
level (and a few levels above it), fights every monster many times, and reports
the win rate. Useful after changing monster stats, gear formulas or scaling.
"""

import argparse
import copy
import math

from . import combat, util
from .data import ATTRIBUTES, DUNGEONS, LABORS, LOCATIONS, MAX_TURNS, SLOT_FOR_TYPE
from .engine import Game
from .items import generate_item
from .rules import recalc_stats

TYPE_FOR_SLOT = {slot: item_type for item_type, slot in SLOT_FOR_TYPE.items()}
TYPICAL_RARITIES = ['Common', 'Uncommon', 'Uncommon', 'Rare']


def typical_game(level):
    """A gladiator of `level` with level-appropriate gear and a little training."""
    game = Game(clock=lambda: 0)
    p = game.player
    p['Level'] = level
    for attr in ('Strength', 'Dexterity', 'Agility', 'Constitution'):
        p['Base' + attr] = 5 + (level - 1) + level // 2  # level-ups plus some training
    for attr in ('Charisma', 'Intelligence'):
        p['Base' + attr] = 5 + level // 3
    for slot in p['Equipment']:
        p['Equipment'][slot] = generate_item(level, TYPE_FOR_SLOT[slot], util.pick(TYPICAL_RARITIES))
    recalc_stats(p)
    p['CurrentHP'] = p['MaxHP']
    return game


def win_rate(monster, player_level, area_level, fights, boss=False):
    wins = 0
    for _ in range(fights):
        game = typical_game(player_level)
        scaled = combat.scale_monster(monster, player_level, area_level)
        if combat.run_fight(game.state, 'sim', combat.monster_combatant(scaled))['IsVictory']:
            wins += 1
    return wins / fights


def arena_win_rate(rank, player_level, fights):
    wins = 0
    for _ in range(fights):
        game = typical_game(player_level)
        rival = combat.arena_opponent_stats({'Name': 'Rival', 'Rank': rank}, game.player)
        if combat.run_fight(game.state, 'sim', combat.arena_combatant(rival))['IsVictory']:
            wins += 1
    return wins / fights


def labor_win_rate(labor, player_level, fights):
    """Labor monsters never scale: out-levelling them makes them easier."""
    wins = 0
    for _ in range(fights):
        game = typical_game(player_level)
        if combat.run_fight(game.state, 'sim', combat.monster_combatant(labor['Monster']))['IsVictory']:
            wins += 1
    return wins / fights


def calibration_samples(fights):
    """(player turns, enemy turns, simulated win rate) over many match-ups, for fitting the threat curve.

    Each match-up keeps one gladiator's gear for all its fights, just as the interface rates fights
    for the player's actual gear.
    """
    matchups = []
    for location in LOCATIONS:
        for monster in location['Monsters']:
            for offset in (-2, 0, 3, 8):
                matchups.append((monster, location['ReqLevel'] + offset, location['ReqLevel']))
    for dungeon in DUNGEONS:
        for stage in dungeon['Stages']:
            for offset in (-2, 0, 3):
                matchups.append((stage['Monster'], dungeon['ReqLevel'] + offset, dungeon['ReqLevel']))
    for labor in LABORS:
        for offset in (-3, 0, 3, 6):
            matchups.append((labor['Monster'], labor['ReqLevel'] + offset, None))
    samples = []
    for monster, level, area_level in matchups:
        level = max(1, level)
        scaled = combat.scale_monster(monster, level, area_level) if area_level else monster
        game = typical_game(level)
        player_turns, enemy_turns = combat.turns_to_win(game.state, combat.monster_combatant(scaled))
        wins = 0
        for _ in range(fights):
            state = copy.deepcopy(game.state)
            wins += combat.run_fight(state, 'sim', combat.monster_combatant(scaled))['IsVictory']
        samples.append((player_turns, enemy_turns, wins / fights))
    return samples


def fit_threat_curve(samples):
    """Grid-search least-squares fit of combat.win_chance_from_turns' three constants."""
    best = None
    for slope in [0.5 + 0.1 * i for i in range(56)]:
        for shift in [-2.0 + 0.04 * i for i in range(63)]:
            duels = [(1 / (1 + math.exp(-max(-60, min(60, slope * (math.log(te / tp) - shift))))), tp, y)
                     for tp, te, y in samples]
            for timeout in (0.15, 0.2, 0.25, 0.3, 0.35, 0.4):
                err = sum((d / (1 + math.exp(-max(-60, min(60, timeout * (MAX_TURNS - tp))))) - y) ** 2
                          for d, tp, y in duels)
                if best is None or err < best[0]:
                    best = (err, slope, shift, timeout)
    return best


def area_rows(fights, offsets=(0, 2, 5)):
    """Yields (area name, monster name, is_boss, {level offset: win rate})."""
    for location in LOCATIONS:
        for monster in location['Monsters']:
            rates = {o: win_rate(monster, location['ReqLevel'] + o, location['ReqLevel'], fights) for o in offsets}
            yield location['Name'], monster['Name'], False, rates
    for dungeon in DUNGEONS:
        for stage in dungeon['Stages']:
            rates = {o: win_rate(stage['Monster'], dungeon['ReqLevel'] + o, dungeon['ReqLevel'], fights) for o in offsets}
            yield dungeon['Name'], stage['Monster']['Name'], stage['IsBoss'], rates


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--fights', type=int, default=300, help='fights per monster and level (default 300)')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--calibrate', action='store_true', help='fit the threat estimate to simulated fights')
    args = parser.parse_args(argv)
    util.rng.seed(args.seed)
    if args.calibrate:
        samples = calibration_samples(args.fights)
        err, slope, shift, timeout = fit_threat_curve(samples)
        rms = math.sqrt(err / len(samples))
        print('THREAT_SLOPE, THREAT_SHIFT, THREAT_TIMEOUT = %.1f, %.2f, %.2f   (%d match-ups, RMS error %.1f%%)'
              % (slope, shift, timeout, len(samples), rms * 100))
        return
    offsets = (0, 2, 5)
    print('Win rate of a typical gladiator (level-appropriate gear, light training)\n')
    print('%-26s %-26s %s' % ('Area', 'Monster', '   '.join('at +%d' % o for o in offsets)))
    for area, name, boss, rates in area_rows(args.fights, offsets):
        print('%-26s %-26s %s' % (area, name + (' (boss)' if boss else ''),
                                  '   '.join('%4d%%' % round(rates[o] * 100) for o in offsets)))
    print('\nLabors of Hercules (monsters do not scale)')
    labor_offsets = (0, 3, 6)
    print('%-26s %-26s %s' % ('Labor', 'Monster', '   '.join('at +%d' % o for o in labor_offsets)))
    for labor in LABORS:
        print('%-26s %-26s %s' % (labor['Title'], labor['Monster']['Name'], '   '.join(
            '%4d%%' % round(labor_win_rate(labor, labor['ReqLevel'] + o, args.fights) * 100) for o in labor_offsets)))
    print('\nArena (rival rank vs. player level)')
    levels = (5, 15, 25, 35, 45)
    print('%-26s %s' % ('Rival rank', '   '.join('L%-4d' % lvl for lvl in levels)))
    for rank in (20, 10, 5, 1):
        print('%-26s %s' % ('#%d' % rank, '   '.join('%4d%%' % round(arena_win_rate(rank, lvl, args.fights) * 100)
                                                      for lvl in levels)))
    print('\nAttributes used: %s' % ', '.join(ATTRIBUTES))


if __name__ == '__main__':
    main()
