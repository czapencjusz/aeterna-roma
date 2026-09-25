"""Item creation, naming, pricing and save-file normalization."""

import math

from .data import (AFFIX_CHANCE, BASE_NAMES, EFFECT_CAPS, EFFECTS, EQUIP_TYPES, ICON_BY_NAME, ITEM_TYPES, MAX_ENHANCE,
                   PREFIXES, RARITIES, SELL_RATIO, SETS, SLOT_FOR_TYPE, SUFFIXES, UNIQUES)
from .util import clamp, is_number, pick, rand_int, roll, text, to_int, uid

ITEM_TEMPLATE = {
    'Id': '', 'Name': '', 'Prefix': '', 'Suffix': '', 'Type': 'Material', 'Rarity': 'Common',
    'LevelRequirement': 1, 'Price': 0, 'MinDamage': 0, 'MaxDamage': 0, 'Armor': 0,
    'Strength': 0, 'Dexterity': 0, 'Agility': 0, 'Constitution': 0, 'Charisma': 0, 'Intelligence': 0,
    'HealAmount': 0, 'EnergyAmount': 0, 'IconSvg': '', 'Upgrade': 0,
    'SmeltIron': 0, 'SmeltBronze': 0, 'SmeltRuby': 0, 'SmeltLeather': 0,
    'SetId': '',     # gear set this item belongs to (see data.SETS), '' for none
    'Effects': {},   # special effects of Mythic items (see data.EFFECTS)
    'Locked': False,  # locked items can't be sold or smelted
    'Pos': None,      # top-left cell [x, y] in the bag grid (see bag.py); None when equipped or not placed
}
ITEM_NUMERIC_FIELDS = [k for k, v in ITEM_TEMPLATE.items() if isinstance(v, int) and not isinstance(v, bool)]


def blank_item():
    item = dict(ITEM_TEMPLATE)
    item['Id'] = uid()
    item['Effects'] = {}
    return item


def make_potion(definition):
    item = blank_item()
    item.update({'Type': 'Potion', 'Rarity': 'Common', 'LevelRequirement': 1})
    item.update(definition)
    return item


def display_name(item):
    name = ' '.join(part for part in (item['Prefix'], item['Name'], item['Suffix']) if part)
    return name + (' +%d' % item['Upgrade'] if item['Upgrade'] else '')


def sell_price(item):
    return max(1, math.floor(item['Price'] * SELL_RATIO))


def is_equipment(item):
    return item['Type'] in SLOT_FOR_TYPE


def _apply_affix(item, affix, level, mult):
    amount = 1 + level // 4 + (mult - 1)
    for stat, weight in affix['Stats'].items():
        item[stat] += weight * amount


def _affix_choices(affixes, item):
    """Affixes that don't repeat a word of the item's name (no "Imperial Imperial Amulet")."""
    words = set(item['Name'].lower().split())
    return [a for a in affixes if not words & set(a['Name'].lower().split()) - {'of'}] or affixes


def roll_rarity():
    r = roll()
    if r > 0.95:
        return 'Legendary'
    if r > 0.85:
        return 'Epic'  # Mythic is never rolled: it is reserved for boss treasures
    if r > 0.65:
        return 'Rare'
    if r > 0.35:
        return 'Uncommon'
    return 'Common'


def generate_item(level, item_type=None, rarity=None):
    """Creates a random piece of equipment for the given level."""
    item_type = item_type or pick(EQUIP_TYPES)
    rarity = rarity or roll_rarity()
    mult = RARITIES.index(rarity) + 1

    item = blank_item()
    item['Type'] = item_type
    item['Rarity'] = rarity
    item['LevelRequirement'] = level

    base_name = pick(BASE_NAMES[item_type]) if item_type in BASE_NAMES else 'Roman Gear'
    if item_type == 'Weapon':
        item['MinDamage'] = level * 3 + rand_int(1, 4) * mult
        item['MaxDamage'] = item['MinDamage'] + rand_int(3, 7) * mult
        item['IconSvg'] = 'weapon_%d' % rand_int(1, 3)
    elif item_type == 'Helmet':
        item['Armor'] = level * 4 + rand_int(2, 5) * mult
        item['IconSvg'] = 'helmet_%d' % rand_int(1, 2)
    elif item_type == 'Armor':
        item['Armor'] = level * 8 + rand_int(5, 11) * mult
        item['IconSvg'] = 'armor_%d' % rand_int(1, 2)
    elif item_type == 'Shield':
        item['Armor'] = level * 5 + rand_int(3, 6) * mult
        item['IconSvg'] = 'shield_%d' % rand_int(1, 2)
    elif item_type == 'Ring':
        item['Strength'] = rand_int(1, 2) * mult
        item['Agility'] = rand_int(1, 2) * mult
        item['IconSvg'] = 'ring_1'
    elif item_type == 'Amulet':
        item['Constitution'] = rand_int(1, 3) * mult
        item['Charisma'] = rand_int(1, 3) * mult
        item['IconSvg'] = 'amulet_1'
    elif item_type == 'Gloves':
        item['Armor'] = level * 2 + mult
        item['Dexterity'] = rand_int(1, 2) * mult
        item['IconSvg'] = 'gloves_1'
    elif item_type == 'Shoes':
        item['Armor'] = level * 2 + mult
        item['Agility'] = rand_int(1, 2) * mult
        item['IconSvg'] = 'shoes_1'

    item['Name'] = base_name
    item['IconSvg'] = ICON_BY_NAME.get(base_name, item['IconSvg'])
    if roll() < AFFIX_CHANCE:
        prefix = pick(_affix_choices(PREFIXES, item))
        item['Prefix'] = prefix['Name']
        _apply_affix(item, prefix, level, mult)
    if roll() < AFFIX_CHANCE:
        suffix = pick(_affix_choices(SUFFIXES, item))
        item['Suffix'] = suffix['Name']
        _apply_affix(item, suffix, level, mult)

    item['Price'] = (level * 25 + 20) * mult
    item['SmeltIron'] = rand_int(1, 3) * mult
    item['SmeltBronze'] = rand_int(1, 2) * mult
    item['SmeltRuby'] = rand_int(1, 2) if RARITIES.index(rarity) >= RARITIES.index('Rare') else 0
    item['SmeltLeather'] = rand_int(1, 3) * mult
    return item


def make_set_piece(set_id, level, item_type=None):
    """A piece of a gear set: Epic stats, no random affixes, set name and icon."""
    pieces = SETS[set_id]['Pieces']
    item_type = item_type if item_type in pieces else pick(sorted(pieces))
    item = generate_item(level, item_type, 'Epic')
    name, icon = pieces[item_type]
    item.update(Name=name, Prefix='', Suffix='', IconSvg=icon, SetId=set_id)
    item['Price'] = math.floor(item['Price'] * 1.5)
    return item


def make_mythic(definition, level):
    """A Mythic item ({'Name', 'Type', 'IconSvg', 'Effects'}): Mythic-strength stats plus special effects."""
    item = generate_item(level, definition['Type'], 'Mythic')
    item.update(Name=definition['Name'], Prefix='', Suffix='', IconSvg=definition['IconSvg'],
                Effects=dict(definition['Effects']))
    return item


def make_unique(boss_name, level):
    """A dungeon boss's Mythic treasure."""
    return make_mythic(UNIQUES[boss_name], level)


def _affix_amount(item):
    return 1 + item['LevelRequirement'] // 4 + RARITIES.index(item['Rarity'])


def reroll_affixes(item):
    """Removes an item's prefix and suffix bonuses and rolls new ones. At least one is guaranteed."""
    for names, field in ((PREFIXES, 'Prefix'), (SUFFIXES, 'Suffix')):
        affix = next((a for a in names if a['Name'] == item[field]), None)
        if affix:
            for stat, weight in affix['Stats'].items():
                item[stat] = max(0, item[stat] - weight * _affix_amount(item))
        item[field] = ''
    rolls = [roll() < AFFIX_CHANCE, roll() < AFFIX_CHANCE]
    if not any(rolls):
        rolls[rand_int(0, 1)] = True
    for wanted, names, field in zip(rolls, (PREFIXES, SUFFIXES), ('Prefix', 'Suffix')):
        if wanted:
            affix = pick(_affix_choices(names, item))
            item[field] = affix['Name']
            for stat, weight in affix['Stats'].items():
                item[stat] += weight * _affix_amount(item)


def _enum_value(value, names):
    """Old C# saves stored enums as numbers; newer saves store their names."""
    if is_number(value):
        index = int(value)
        return names[index] if 0 <= index < len(names) else None
    return value if value in names else None


def normalize_item(raw):
    """Converts one item from any save format into a clean item dict (or None)."""
    if not isinstance(raw, dict):
        return None
    item = blank_item()
    for key in ITEM_NUMERIC_FIELDS:
        item[key] = max(0, to_int(raw.get(key), 0))
    for key in ('Name', 'Prefix', 'Suffix', 'IconSvg'):
        item[key] = text(raw.get(key), 60)
    if isinstance(raw.get('Id'), str) and raw['Id']:
        item['Id'] = raw['Id'][:60]
    item['Type'] = _enum_value(raw.get('Type'), ITEM_TYPES) or 'Material'
    item['Rarity'] = _enum_value(raw.get('Rarity'), RARITIES) or 'Common'
    item['LevelRequirement'] = max(1, item['LevelRequirement'])
    item['Upgrade'] = clamp(item['Upgrade'], 0, MAX_ENHANCE)
    item['SetId'] = raw.get('SetId') if raw.get('SetId') in SETS else ''
    item['Locked'] = raw.get('Locked') is True
    pos = raw.get('Pos')
    item['Pos'] = [pos[0], pos[1]] if (isinstance(pos, list) and len(pos) == 2
                                      and all(isinstance(v, int) and not isinstance(v, bool) for v in pos)) else None
    raw_effects = raw.get('Effects') if isinstance(raw.get('Effects'), dict) else {}
    item['Effects'] = {key: clamp(to_int(value, 0), 0, EFFECT_CAPS.get(key, 100))
                       for key, value in raw_effects.items() if key in EFFECTS and to_int(value, 0) > 0}
    if not item['Name']:
        item['Name'] = 'Unknown Item'
    return item
