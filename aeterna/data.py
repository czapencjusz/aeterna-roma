"""Static game data and tuning constants for Aeterna Roma."""

ITEM_TYPES = ['Weapon', 'Armor', 'Helmet', 'Shield', 'Ring', 'Amulet', 'Gloves', 'Shoes', 'Potion', 'Material']
EQUIP_TYPES = ITEM_TYPES[:8]
RARITIES = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Mythic']  # Mythic: unique boss treasures only
RANDOM_RARITIES = RARITIES[:5]
SLOTS = ['Head', 'Chest', 'Gloves', 'Shoes', 'Weapon', 'Shield', 'Ring', 'Amulet']
SLOT_FOR_TYPE = {
    'Weapon': 'Weapon', 'Armor': 'Chest', 'Helmet': 'Head', 'Shield': 'Shield',
    'Ring': 'Ring', 'Amulet': 'Amulet', 'Gloves': 'Gloves', 'Shoes': 'Shoes',
}
ATTRIBUTES = ['Strength', 'Dexterity', 'Agility', 'Constitution', 'Charisma', 'Intelligence']

# --- Tuning -----------------------------------------------------------------
ENERGY_REGEN_PER_MIN = 2
ARENA_COOLDOWN_MS = 5 * 60 * 1000
DUNGEON_ENERGY_COST = 2
MIN_FIGHT_HP_RATIO = 0.10
MAX_TURNS = 30
LOOT_CHANCE = 0.55
SHIELD_BLOCK_BONUS = 0.08
GUILD_COST = 500
WORK_GOLD_PER_HOUR = 110
WORK_XP_PER_HOUR = 25
WORK_OPTIONS = [1, 2, 4, 8]
LADDER_SIZE = 21  # 20 rival gladiators + the player
SELL_RATIO = 0.5  # merchants pay half an item's value
MAX_ENHANCE = 5
QUEST_SLOTS = 3
QUEST_ABANDON_WAIT_MS = 5 * 60 * 1000
RUBY_COST = {'refillEnergy': 2, 'skipArena': 1, 'restock': 1}
ARENA_MILESTONES = [  # first time reaching these ranks pays rubies
    {'Rank': 5, 'Rubies': 2},
    {'Rank': 3, 'Rubies': 3},
    {'Rank': 1, 'Rubies': 5},
]
COMBAT_SPEEDS = {'Instant': 0, 'Fast': 60, 'Normal': 220}  # ms per combat log line

# Experience needed for the next level: the classic x1.5 curve up to level 10, then a steady
# quadratic curve so levels past the teens stay reachable (x1.5 forever needs millions of XP by 30).
XP_EARLY_LEVELS = 10
XP_LATE_GROWTH = 0.25

# How much tougher expedition/dungeon monsters get for each level the player is above the area.
# Gentle on purpose: out-levelling an area should make it easier, not harder (checked with
# `python -m aeterna.balance`). HP is a fraction of the monster's base HP; the rest are flat.
MONSTER_SCALING = {'HP': 0.05, 'MinDamage': 1, 'MaxDamage': 2, 'Armor': 2, 'Dexterity': 1, 'Agility': 1,
                   'XPReward': 12, 'MinGold': 10, 'MaxGold': 20}

GUILD_BUILDINGS = {
    'TrainingGrounds': {'Name': 'Training Grounds', 'Icon': '🏋️', 'PerLevel': 5,
                        'Effect': 'Attribute training costs {pct}% less'},
    'Library': {'Name': 'Library of Minerva', 'Icon': '📜', 'PerLevel': 5, 'Effect': '+{pct}% experience from fights and quests'},
    'Villa': {'Name': 'Guild Villa', 'Icon': '🏛️', 'PerLevel': 10, 'Effect': '+{pct}% villa work pay and HP regeneration'},
}
GUILD_BUILDING_MAX = 5
GUILD_DONATIONS = [100, 500, 1000]

# Prefixes/suffixes grant real attribute bonuses (amount scales with item level and rarity).
PREFIXES = [
    {'Name': 'Praetorian', 'Stats': {'Constitution': 1}},
    {'Name': 'Centurion', 'Stats': {'Strength': 1}},
    {'Name': 'Imperial', 'Stats': {'Charisma': 1}},
    {'Name': 'Olympian', 'Stats': {'Intelligence': 1}},
    {'Name': 'Invictus', 'Stats': {'Agility': 1}},
    {'Name': 'Titan', 'Stats': {'Strength': 1, 'Constitution': 1}},
]
SUFFIXES = [
    {'Name': 'of Valor', 'Stats': {'Dexterity': 1}},
    {'Name': 'of Jupiter', 'Stats': {'Intelligence': 1, 'Charisma': 1}},
    {'Name': 'of Mars', 'Stats': {'Strength': 1, 'Dexterity': 1}},
    {'Name': 'of Blood', 'Stats': {'Strength': 2}},
    {'Name': 'of Victory', 'Stats': {'Agility': 1, 'Charisma': 1}},
]
AFFIX_CHANCE = 0.5

THEMES = {
    'DarkImperial': 'Dark Imperial',
    'RomanParchment': 'Roman Parchment',
    'ColosseumCrimson': 'Colosseum Crimson',
    'LegionEmerald': 'Legion Emerald',
    'TyrianPurple': 'Tyrian Purple',
}

VENDOR_DEFS = {
    'Weaponsmith': {'Name': 'Marcus the Blacksmith', 'Label': '⚔️ Weaponsmith', 'Stock': ['Weapon', 'Shield']},
    'Armorer': {'Name': 'Flavius Armorsmith', 'Label': '🛡️ Armorer', 'Stock': ['Armor', 'Helmet', 'Gloves', 'Shoes']},
    'General': {'Name': 'Gaius Goods Trader', 'Label': '💍 General Merchant', 'Stock': ['Ring', 'Amulet']},
    'Alchemist': {'Name': 'Cornelia the Apothecary', 'Label': '🧪 Apothecary', 'Stock': None},
}
VENDOR_STOCK_SIZE = 6
ALCHEMIST_ITEMS = [
    {'Name': 'Small Health Potion', 'HealAmount': 40, 'Price': 15, 'IconSvg': 'potion_red'},
    {'Name': 'Large Health Potion', 'HealAmount': 100, 'Price': 35, 'IconSvg': 'potion_red'},
    {'Name': 'Stamina Elixir', 'EnergyAmount': 10, 'Price': 50, 'IconSvg': 'potion_blue'},
    {'Name': 'Greater Health Potion', 'HealAmount': 300, 'Price': 90, 'IconSvg': 'potion_red'},
    {'Name': 'Greater Stamina Elixir', 'EnergyAmount': 25, 'Price': 120, 'IconSvg': 'potion_blue'},
    {'Name': 'Elixir of Life', 'HealAmount': 800, 'Price': 220, 'IconSvg': 'potion_green'},
    {'Name': 'Ambrosia', 'HealAmount': 5000, 'EnergyAmount': 40, 'Price': 600, 'IconSvg': 'potion_gold'},
]

# Random loot / merchant item names for each item type.
BASE_NAMES = {
    'Weapon': ['Gladius', 'Spatha', 'Pugio Dagger', 'Trident', 'Halberd', 'Centurion Sword', 'Sica', 'Falcata', 'Pilum',
               'Mace'],
    'Helmet': ['Galea Helmet', 'Centurion Crest', 'Legionary Helm', 'Gladiator Mask', 'Thracian Helm', 'Montefortino Helm'],
    'Armor': ['Lorica Segmentata', 'Lorica Hamata', 'Gladiator Cuirass', 'Bronze Breastplate', 'Lorica Squamata',
              'Linothorax'],
    'Shield': ['Scutum Shield', 'Parma Round Shield', 'Tower Shield', 'Gladiator Buckler', 'Hoplite Aspis',
               'Dacian Oval Shield'],
    'Ring': ['Signet Ring', 'Iron Legion Ring', 'Serpent Ring'],
    'Amulet': ['Imperial Amulet', 'Bulla Pendant', 'Golden Torc'],
    'Gloves': ['Leather Gauntlets', 'Manica Arm Guard'],
    'Shoes': ['Caligae Sandals', 'Bronze Greaves'],
}

# Item name -> matching icon, so a "Trident" looks like a trident.
ICON_BY_NAME = {
    'Gladius': 'weapon_1', 'Centurion Gladius': 'weapon_1', 'Spatha': 'weapon_2', 'Centurion Sword': 'weapon_2',
    'Spatha of Victory': 'weapon_2', 'Pugio Dagger': 'weapon_3', 'Trident': 'weapon_4', 'Halberd': 'weapon_5',
    'Sica': 'weapon_6', 'Falcata': 'weapon_6', 'Sica of the Thracian': 'weapon_6', 'Pilum': 'weapon_7', 'Mace': 'weapon_8',
    'Galea Helmet': 'helmet_1', 'Legionary Helm': 'helmet_1', 'Golden Galea Helmet': 'helmet_1', 'Montefortino Helm': 'helmet_1',
    'Centurion Crest': 'helmet_2', 'Gladiator Mask': 'helmet_3', 'Thracian Helm': 'helmet_4', 'Thracian Champion Helm': 'helmet_4',
    'Lorica Segmentata': 'armor_1', 'Imperial Lorica Segmentata': 'armor_1', 'Lorica Hamata': 'armor_2',
    'Gladiator Cuirass': 'armor_3', 'Bronze Breastplate': 'armor_3', 'Linothorax': 'armor_3',
    'Lorica Squamata': 'armor_4', 'Lorica Squamata of Mars': 'armor_4',
    'Scutum Shield': 'shield_1', 'Tower Shield': 'shield_1', 'Scutum of Mars': 'shield_1',
    'Parma Round Shield': 'shield_2', 'Aegis of Minerva': 'shield_2', 'Hoplite Aspis': 'shield_2', 'Aspis of Olympus': 'shield_2',
    'Gladiator Buckler': 'shield_3', 'Dacian Oval Shield': 'shield_4',
    'Signet Ring': 'ring_1', 'Iron Legion Ring': 'ring_1', 'Serpent Ring': 'ring_2',
    'Imperial Amulet': 'amulet_1', 'Bulla Pendant': 'amulet_1', 'Golden Torc': 'amulet_2', 'Torc of Boudica': 'amulet_2',
    'Leather Gauntlets': 'gloves_1', 'Manica Arm Guard': 'gloves_2',
    'Caligae Sandals': 'shoes_1', 'Bronze Greaves': 'shoes_2', 'Greaves of Achilles': 'shoes_2',
}

# --- Special effects ------------------------------------------------------------
# Gear sets, Mythic items and temple blessings grant these effects (all whole numbers):
EFFECTS = {
    'DamagePct': '+{v}% damage',
    'ArmorPct': '+{v}% armor',
    'HPPct': '+{v}% max HP',
    'CritBonus': '+{v}% critical strike chance',
    'BlockBonus': '+{v}% block chance',
    'LifeSteal': 'Heal {v}% of the damage you deal',
    'RegenPct': '+{v}% HP regeneration',
    'GoldPct': '+{v}% gold from fights',
    'XPPct': '+{v}% experience from fights',
}
EFFECT_CAPS = {'CritBonus': 30, 'BlockBonus': 30, 'LifeSteal': 25}  # upper limits on the combined totals


def _set(name, pieces, bonuses, sources):
    return {'Name': name, 'Pieces': pieces, 'Bonuses': bonuses, 'Sources': sources}


# Gear sets: wearing several pieces of the same set unlocks its bonuses.
# Pieces are {item type: (name, icon)}; bonuses are [(pieces needed, effects)].
SETS = {
    'legion': _set("Legionary's Panoply",
                   {'Helmet': ('Legion Galea', 'helmet_1'), 'Armor': ('Legion Segmentata', 'armor_1'),
                    'Shield': ('Legion Scutum', 'shield_1'), 'Weapon': ('Legion Gladius', 'weapon_1')},
                   [(2, {'ArmorPct': 10}), (4, {'HPPct': 10, 'BlockBonus': 5})],
                   'Barbarian Camp, Dacian Frontier, Britannia, Teutoburg Forest, Slopes of Olympus'),
    'murmillo': _set('Murmillo of Capua',
                     {'Helmet': ('Murmillo Fish-Helm', 'helmet_3'), 'Shield': ('Murmillo Scutum', 'shield_1'),
                      'Gloves': ('Murmillo Manica', 'gloves_2'), 'Shoes': ('Murmillo Greaves', 'shoes_2')},
                     [(2, {'CritBonus': 4}), (4, {'DamagePct': 12})],
                     'Arena victories and the Honor shop'),
    'pharaoh': _set('Regalia of the Pharaoh',
                    {'Helmet': ('Nemes of Ra', 'helmet_5'), 'Armor': ('Gilded Linothorax', 'armor_3'),
                     'Amulet': ('Scarab Pectoral', 'amulet_1'), 'Ring': ('Ring of Osiris', 'ring_2')},
                    [(2, {'RegenPct': 25}), (4, {'XPPct': 15, 'HPPct': 8})],
                    'Sands of Aegyptus, Tomb of the Pharaoh, Gates of Avernus'),
    'vulcan': _set("Vulcan's Forgework",
                   {'Weapon': ('Forgefire Mace', 'weapon_8'), 'Armor': ('Forgefire Squamata', 'armor_4'),
                    'Gloves': ('Forgefire Gauntlets', 'gloves_2')},
                   [(2, {'DamagePct': 8}), (3, {'ArmorPct': 15, 'CritBonus': 5})],
                   'Forge of Vulcan, Slopes of Olympus'),
    'mercury': _set("Mercury's Swiftness",
                    {'Shoes': ('Winged Sandals', 'shoes_1'), 'Gloves': ("Messenger's Wraps", 'gloves_1'),
                     'Ring': ('Caduceus Ring', 'ring_2')},
                    [(2, {'GoldPct': 20}), (3, {'BlockBonus': 6, 'CritBonus': 4})],
                    'Port of Ostia, Parthian Steppe, Slopes of Olympus'),
    'neptune': _set("Tidecaller's Raiment",
                    {'Helmet': ('Coral Crown', 'helmet_4'), 'Armor': ('Scale of Leviathan', 'armor_4'),
                     'Shield': ('Nautilus Aspis', 'shield_2'), 'Amulet': ('Pearl of the Deep', 'amulet_1')},
                    [(2, {'HPPct': 8}), (4, {'RegenPct': 40, 'LifeSteal': 4})],
                    'Port of Ostia, Sunken Temple of Neptune, Gates of Avernus'),
}
SET_DROP_CHANCE = 0.12  # share of loot drops that are set pieces, in areas that have sets
ARENA_SET_DROP_CHANCE = 0.10  # chance of a Murmillo piece after an arena win

# Mythic treasures: one per dungeon boss. Guaranteed on the first conquest, rare afterwards.
UNIQUES = {
    'Lich Lord Cassius': {'Name': 'Crown of Cassius', 'Type': 'Helmet', 'IconSvg': 'helmet_6',
                          'Effects': {'LifeSteal': 5, 'CritBonus': 3}},
    'Minotaur Emperor': {'Name': 'Labrys of Minos', 'Type': 'Weapon', 'IconSvg': 'weapon_9',
                         'Effects': {'DamagePct': 12}},
    'Avatar of Vulcan': {'Name': 'Hammer of Vulcan', 'Type': 'Weapon', 'IconSvg': 'weapon_8',
                         'Effects': {'CritBonus': 8, 'DamagePct': 6}},
    'Scylla': {'Name': 'Pearl of Scylla', 'Type': 'Amulet', 'IconSvg': 'amulet_1',
               'Effects': {'RegenPct': 50, 'HPPct': 10}},
    'Pharaoh Ascendant': {'Name': 'Khopesh of Ra', 'Type': 'Weapon', 'IconSvg': 'weapon_6',
                          'Effects': {'LifeSteal': 8, 'DamagePct': 5}},
    'Hades, Lord of the Dead': {'Name': 'Helm of Darkness', 'Type': 'Helmet', 'IconSvg': 'helmet_3',
                                'Effects': {'BlockBonus': 10, 'CritBonus': 5, 'HPPct': 5}},
}
UNIQUE_REPEAT_CHANCE = 0.12

# Temple of the gods: one blessing at a time, lasting a number of fights.
BLESSINGS = {
    'mars': {'Name': 'Blessing of Mars', 'Icon': '⚔️', 'Effects': {'DamagePct': 15}, 'Fights': 5},
    'minerva': {'Name': 'Wisdom of Minerva', 'Icon': '🦉', 'Effects': {'CritBonus': 8, 'XPPct': 10}, 'Fights': 5},
    'juno': {'Name': 'Aegis of Juno', 'Icon': '🛡️', 'Effects': {'BlockBonus': 8, 'ArmorPct': 10}, 'Fights': 5},
    'mercury': {'Name': 'Favor of Mercury', 'Icon': '🪽', 'Effects': {'GoldPct': 30}, 'Fights': 8},
    'apollo': {'Name': 'Light of Apollo', 'Icon': '☀️', 'Effects': {'XPPct': 25, 'RegenPct': 50}, 'Fights': 8},
}


def blessing_cost(level):
    return 60 + level * 30


# Honor shop: Honor from arena wins buys permanent upgrades and treasures.
HONOR_SHOP = {
    'satchel': {'Name': 'Larger Satchel', 'Icon': '🎒', 'Desc': '+4 inventory slots', 'Max': 6, 'Base': 150, 'Step': 125},
    'favor': {'Name': "Emperor's Favor", 'Icon': '👑', 'Desc': '+1 to all six attributes, permanently', 'Max': 10,
              'Base': 200, 'Step': 150},
    'tribute': {'Name': "Gladiator's Tribute", 'Icon': '🎁', 'Desc': 'A random Murmillo of Capua set piece at your level',
                'Max': None, 'Base': 300, 'Step': 0},
    'ruby': {'Name': 'Imperial Ruby', 'Icon': '💎', 'Desc': 'Trade Honor for a ruby', 'Max': None, 'Base': 120, 'Step': 0},
}
SATCHEL_SLOTS = 4


def _ach(id_, name, desc, stat, goal, rubies):
    return {'Id': id_, 'Name': name, 'Desc': desc, 'Stat': stat, 'Goal': goal, 'Rubies': rubies}


# Achievements unlock automatically and pay rubies. 'Stat' is a lifetime statistic or one of the
# special checks: Level, BestArenaRank (reach rank Goal or better), FullSet, BestiaryPct.
ACHIEVEMENTS = [
    _ach('first_blood', 'First Blood', 'Win your first fight', 'FightsWon', 1, 1),
    _ach('slayer_100', 'Beast Slayer', 'Slay 100 monsters', 'MonstersSlain', 100, 2),
    _ach('slayer_500', 'Monster Bane', 'Slay 500 monsters', 'MonstersSlain', 500, 5),
    _ach('slayer_2000', 'Scourge of the Wilds', 'Slay 2,000 monsters', 'MonstersSlain', 2000, 10),
    _ach('arena_10', 'Crowd Favorite', 'Win 10 arena bouts', 'ArenaWins', 10, 2),
    _ach('arena_100', 'Darling of the Colosseum', 'Win 100 arena bouts', 'ArenaWins', 100, 8),
    _ach('champion', 'Champion of Rome', 'Reach arena rank #1', 'BestArenaRank', 1, 10),
    _ach('dungeon_1', 'Delver', 'Conquer a dungeon', 'DungeonsConquered', 1, 2),
    _ach('dungeon_10', 'Tomb Raider', 'Conquer 10 dungeons', 'DungeonsConquered', 10, 6),
    _ach('quests_10', 'Devout', 'Complete 10 divine tasks', 'QuestsCompleted', 10, 2),
    _ach('quests_50', 'Chosen of the Gods', 'Complete 50 divine tasks', 'QuestsCompleted', 50, 6),
    _ach('gold_10k', 'Merchant Prince', 'Earn 10,000 gold', 'GoldEarned', 10000, 2),
    _ach('gold_250k', 'Crassus Reborn', 'Earn 250,000 gold', 'GoldEarned', 250000, 8),
    _ach('crafter', "Vulcan's Apprentice", 'Forge 10 items', 'ItemsCrafted', 10, 3),
    _ach('enhancer', 'Master Smith', 'Make 25 enhancements', 'ItemsEnhanced', 25, 4),
    _ach('level_10', 'Seasoned', 'Reach level 10', 'Level', 10, 2),
    _ach('level_20', 'Veteran of the Legions', 'Reach level 20', 'Level', 20, 4),
    _ach('level_30', 'Legend of the Arena', 'Reach level 30', 'Level', 30, 6),
    _ach('level_40', 'Demigod', 'Reach level 40', 'Level', 40, 10),
    _ach('set_full', 'Fully Kitted', 'Wear a complete gear set', 'FullSet', 1, 5),
    _ach('mythic', 'Treasure of the Gods', 'Find a Mythic item', 'UniquesFound', 1, 3),
    _ach('bestiary_half', 'Naturalist', 'Defeat half of all creature types', 'BestiaryPct', 50, 3),
    _ach('bestiary_all', 'Pliny the Elder', 'Defeat every creature type', 'BestiaryPct', 100, 10),
    _ach('labor_1', 'In the Footsteps of Hercules', 'Complete a Labor of Hercules', 'Labors', 1, 2),
    _ach('labor_6', 'Half a Hero', 'Complete six Labors of Hercules', 'Labors', 6, 5),
    _ach('labor_12', 'Heir of Hercules', 'Complete all twelve Labors of Hercules', 'Labors', 12, 15),
    _ach('daily_7', 'Creature of Habit', 'Answer the Imperial Decree 7 days in a row', 'BestDailyStreak', 7, 3),
    _ach('series_10', 'Relentless', 'Win a battle series of 10 fights without a loss', 'BestSeries', 10, 3),
]


def _m(id_, name, level, hp, mn, mx, armor, dex, agi, xp, gmin, gmax):
    return {'Id': id_, 'Name': name, 'Level': level, 'MaxHP': hp, 'MinDamage': mn, 'MaxDamage': mx, 'Armor': armor,
            'Dexterity': dex, 'Agility': agi, 'XPReward': xp, 'MinGold': gmin, 'MaxGold': gmax}


def _gen(id_, name, level, hp=1.0, dmg=1.0, armor=1.0, dex=1.0, agi=1.0, reward=1.0):
    """Monster stats from the standard difficulty curve (calibrated with `python -m aeterna.balance`).

    HP grows linearly so fights stay a similar length; damage grows a little faster to keep up with
    the player's armor. The keyword arguments make a monster tankier, harder-hitting, quicker, etc.
    """
    min_damage = round((0.08 * level * level + 2.8 * level) * dmg)
    gold = round(2.6 * level * level * reward)
    return _m(id_, name, level, round((45 * level + 60) * hp), min_damage, round(min_damage * 1.55),
              round(2.6 * level * armor), round(2.4 * level * dex), round(1.8 * level * agi),
              round(2.8 * level * level * reward), gold, round(gold * 1.55))


LOCATIONS = [
    {'Id': 1, 'Name': 'Suburbs of Rome', 'ReqLevel': 1, 'EnergyCost': 1,
     'Description': 'Outskirts of the Eternal City, overrun by rabid wolves, runaway slaves, and mountain bandits.',
     'Monsters': [
         _m('m1', 'Wild Boar', 1, 45, 3, 7, 2, 4, 4, 15, 10, 25),
         _m('m2', 'Stray Hound', 1, 35, 2, 6, 1, 6, 6, 12, 8, 20),
         _m('m3', 'Highway Bandit', 2, 65, 5, 11, 4, 8, 6, 25, 20, 45),
     ]},
    {'Id': 2, 'Name': 'Mist Mountains', 'ReqLevel': 3, 'EnergyCost': 2,
     'Description': 'Treacherous jagged peaks guarded by fierce Harpies, Stone Trolls, and Shadow Lynx.',
     'Monsters': [
         _m('m4', 'Mountain Lynx', 3, 90, 8, 14, 6, 12, 14, 40, 35, 70),
         _m('m5', 'Screeching Harpy', 4, 110, 10, 18, 8, 15, 16, 55, 50, 90),
         _m('m6', 'Mountain Troll', 5, 160, 14, 24, 15, 8, 5, 75, 70, 130),
     ]},
    {'Id': 7, 'Name': 'Port of Ostia', 'ReqLevel': 4, 'EnergyCost': 2, 'Sets': ['mercury', 'neptune'],
     'Description': "Rome's bustling harbor, where smugglers, pirates and the Rat King of the sewers rule the night.",
     'Monsters': [
         _m('m18', 'Dock Thug', 4, 115, 9, 16, 8, 11, 10, 50, 45, 80),
         _m('m19', 'Cilician Pirate', 5, 140, 12, 20, 9, 15, 14, 65, 60, 110),
         _m('m20', 'Rat King', 6, 150, 13, 22, 6, 18, 20, 80, 70, 130),
     ]},
    {'Id': 3, 'Name': 'Ancient Forest', 'ReqLevel': 6, 'EnergyCost': 2,
     'Description': 'Deep mystical woods harboring rogue Centaurs, Werewolves, and Ancient Treants.',
     'Monsters': [
         _m('m7', 'Centaur Scout', 6, 190, 16, 26, 12, 18, 18, 100, 90, 160),
         _m('m8', 'Timber Werewolf', 7, 230, 20, 32, 14, 22, 20, 130, 120, 210),
         _m('m9', 'Corrupted Treant', 8, 300, 24, 38, 22, 10, 8, 170, 150, 280),
     ]},
    {'Id': 4, 'Name': 'Barbarian Camp', 'ReqLevel': 9, 'EnergyCost': 3, 'Sets': ['legion'],
     'Description': 'Fierce hostile war camp of Northern Barbarian Warriors and Chieftains.',
     'Monsters': [
         _m('m10', 'Barbarian Berserker', 9, 360, 28, 45, 18, 24, 22, 220, 200, 350),
         _m('m11', 'Warlord Chieftain', 10, 480, 35, 58, 25, 28, 24, 300, 300, 500),
     ]},
    {'Id': 5, 'Name': 'Sands of Aegyptus', 'ReqLevel': 12, 'EnergyCost': 3, 'Sets': ['pharaoh'],
     'Description': 'Scorching dunes along the Nile where giant scorpions lurk and ancient tombs guard their secrets.',
     'Monsters': [
         _m('m12', 'Giant Scorpion', 12, 520, 38, 60, 28, 30, 24, 380, 380, 600),
         _m('m13', 'Tomb Guardian', 13, 600, 42, 66, 36, 26, 20, 450, 450, 700),
         _m('m14', 'Riddling Sphinx', 14, 700, 48, 74, 32, 34, 28, 540, 520, 820),
     ]},
    {'Id': 6, 'Name': 'Dacian Frontier', 'ReqLevel': 16, 'EnergyCost': 4, 'Sets': ['legion'],
     'Description': "Wild mountain borderlands where King Decebalus' warriors and wolf-cult priests defy the legions.",
     'Monsters': [
         _m('m15', 'Dacian Falxman', 16, 840, 56, 86, 40, 38, 30, 700, 650, 1000),
         _m('m16', 'Wolf Priest', 17, 920, 60, 92, 38, 42, 34, 800, 720, 1100),
         _m('m17', 'Champion of Decebalus', 18, 1080, 66, 102, 48, 44, 32, 950, 850, 1300),
     ]},
    {'Id': 8, 'Name': 'Britannia', 'ReqLevel': 20, 'EnergyCost': 4, 'Sets': ['legion'],
     'Description': "Beyond Hadrian's Wall, painted Pictish raiders, cave bears and grove druids haunt the misty moors.",
     'Monsters': [
         _gen('m21', 'Pictish Raider', 20, dex=1.1),
         _gen('m22', 'Caledonian Bear', 21, hp=1.3, dmg=1.1, dex=0.8, agi=0.6),
         _gen('m23', 'Druid of the Grove', 22, hp=0.85, dmg=1.2, dex=1.2),
     ]},
    {'Id': 9, 'Name': 'Parthian Steppe', 'ReqLevel': 24, 'EnergyCost': 5, 'Sets': ['mercury'],
     'Description': 'Endless eastern plains where horse archers never miss and armored cataphracts charge like thunder.',
     'Monsters': [
         _gen('m24', 'Parthian Horse Archer', 24, hp=0.85, dex=1.3, agi=1.4),
         _gen('m25', 'Cataphract', 25, hp=1.15, armor=1.6, agi=0.6),
         _gen('m26', 'Sand Wraith', 26, hp=0.9, dmg=1.15, armor=0.5, agi=1.4),
     ]},
    {'Id': 10, 'Name': 'Teutoburg Forest', 'ReqLevel': 28, 'EnergyCost': 5, 'Sets': ['legion'],
     'Description': 'The cursed woods where three legions vanished. Germanic warbands, giant aurochs and restless ghosts remain.',
     'Monsters': [
         _gen('m27', 'Germanic Warlord', 28, dmg=1.1),
         _gen('m28', 'Great Aurochs', 29, hp=1.3, dmg=1.1, agi=0.5),
         _gen('m29', 'Ghost of the Lost Legion', 30, armor=1.3, dex=1.1),
     ]},
    {'Id': 11, 'Name': 'Gates of Avernus', 'ReqLevel': 32, 'EnergyCost': 6, 'Sets': ['neptune', 'pharaoh'],
     'Description': "The volcanic lake at the entrance to the Underworld, watched by Charon's shades, the Furies and Cerberus.",
     'Monsters': [
         _gen('m30', 'Shade of Charon', 32, armor=0.8, agi=1.2),
         _gen('m31', 'Fury of Tisiphone', 33, hp=0.85, dmg=1.15, dex=1.3, agi=1.3),
         _gen('m32', 'Cerberus', 35, hp=1.1, dmg=1.05),
     ]},
    {'Id': 12, 'Name': 'Slopes of Olympus', 'ReqLevel': 38, 'EnergyCost': 6, 'Sets': ['vulcan', 'mercury', 'legion'],
     'Description': "The home of the gods. Bronze-feathered birds, the invulnerable lion of Nemea and the Titans' last sentinel bar the way.",
     'Monsters': [
         _gen('m33', 'Stymphalian Bird', 38, hp=0.8, dex=1.2, agi=1.4),
         _gen('m34', 'Nemean Lion', 39, hp=0.95, armor=1.5),
         _gen('m35', 'Titan Sentinel', 41, hp=1.2, dmg=1.05, agi=0.6),
     ]},
]


def _stage(name, is_boss, monster):
    monster = dict(monster)
    monster.pop('Id')
    return {'Name': name, 'IsBoss': is_boss, 'Monster': monster}


DUNGEONS = [
    {'Id': 1, 'Name': 'Catacombs of Rome', 'ReqLevel': 4,
     'Description': 'Underground ancient tombs occupied by Undead Centurions and the Necromancer Master.',
     'Stages': [
         _stage('Catacomb Guard', False, _m('', 'Skeleton Legionary', 4, 120, 10, 16, 8, 12, 10, 60, 50, 90)),
         _stage('Crypt Tomb', False, _m('', 'Crypt Wight', 5, 170, 14, 22, 12, 15, 12, 90, 80, 130)),
         _stage('Necromancer Chamber', True, _m('', 'Lich Lord Cassius', 6, 280, 20, 32, 18, 20, 18, 200, 250, 450)),
     ]},
    {'Id': 2, 'Name': 'Labyrinth of the Minotaur', 'ReqLevel': 8,
     'Description': 'Winding maze of stone corridors guarded by mythical beasts and the monstrous Minotaur.',
     'Stages': [
         _stage('Maze Entrance', False, _m('', 'Gorgon Sentinel', 8, 260, 22, 36, 16, 22, 20, 160, 150, 250)),
         _stage('Labyrinth Center', True, _m('', 'Minotaur Emperor', 10, 500, 38, 60, 28, 25, 22, 400, 500, 900)),
     ]},
    {'Id': 3, 'Name': 'Forge of Vulcan', 'ReqLevel': 13, 'Sets': ['vulcan'],
     'Description': "Beneath Mount Etna, the smith-god's servants guard the fires where the weapons of the gods are made.",
     'Stages': [
         _stage('Lava Tunnels', False, _m('', 'Fire Salamander', 13, 560, 42, 64, 30, 32, 26, 420, 420, 650)),
         _stage('Cyclops Smithy', False, _m('', 'Cyclops Smith', 14, 720, 50, 78, 40, 26, 18, 520, 500, 800)),
         _stage('Heart of the Mountain', True, _m('', 'Avatar of Vulcan', 16, 1000, 58, 90, 46, 36, 28, 900, 1000, 1600)),
     ]},
    {'Id': 4, 'Name': 'Sunken Temple of Neptune', 'ReqLevel': 18, 'EnergyCost': 3, 'Sets': ['neptune'],
     'Description': "A drowned temple beneath the Bay of Naples, where sirens sing and Scylla guards Neptune's treasury.",
     'Stages': [
         _stage('Flooded Portico', False, _gen('', 'Siren', 18, hp=0.85, dex=1.3, agi=1.2)),
         _stage('Hall of Tides', False, _gen('', 'Triton Guard', 19, armor=1.4)),
         _stage("Scylla's Grotto", True, _gen('', 'Scylla', 21, hp=1.3, dmg=1.2, reward=1.5)),
     ]},
    {'Id': 5, 'Name': 'Tomb of the Pharaoh', 'ReqLevel': 24, 'EnergyCost': 3, 'Sets': ['pharaoh'],
     'Description': 'A sealed pyramid in the Valley of Kings. Its priests still serve a Pharaoh who refuses to stay dead.',
     'Stages': [
         _stage('Hall of Offerings', False, _gen('', 'Mummy Priest', 24, dmg=1.1)),
         _stage('Chamber of Scarabs', False, _gen('', 'Scarab Colossus', 25, hp=1.2, armor=1.8, agi=0.5)),
         _stage('Burial Chamber', True, _gen('', 'Pharaoh Ascendant', 27, hp=1.3, dmg=1.25, reward=1.5)),
     ]},
    {'Id': 6, 'Name': 'Depths of Tartarus', 'ReqLevel': 34, 'EnergyCost': 4, 'Sets': ['neptune', 'pharaoh', 'vulcan'],
     'Description': 'The deepest pit of the Underworld, where the Titans are chained and Hades himself holds court.',
     'Stages': [
         _stage('River of Fire', False, _gen('', 'Lamia', 34, hp=0.9, dex=1.3, agi=1.3)),
         _stage('Prison of the Titans', False, _gen('', 'Hundred-Handed Warden', 35, hp=1.3, dmg=1.1, agi=0.6)),
         _stage('Throne of the Dead', True, _gen('', 'Hades, Lord of the Dead', 37, hp=1.3, dmg=1.2, reward=1.6)),
     ]},
]


def _recipe(id_, name, rtype, rarity, iron, bronze, ruby, leather, level, icon):
    return {'Id': id_, 'Name': name, 'ResultType': rtype, 'ResultRarity': rarity, 'ReqIron': iron, 'ReqBronze': bronze,
            'ReqRuby': ruby, 'ReqLeather': leather, 'ReqLevel': level, 'IconSvg': icon}


RECIPES = [
    _recipe('r1', 'Centurion Gladius', 'Weapon', 'Uncommon', 5, 2, 0, 2, 2, 'weapon_1'),
    _recipe('r2', 'Imperial Lorica Segmentata', 'Armor', 'Rare', 8, 5, 1, 5, 4, 'armor_1'),
    _recipe('r3', 'Scutum of Mars', 'Shield', 'Epic', 10, 8, 3, 4, 6, 'shield_1'),
    _recipe('r4', 'Golden Galea Helmet', 'Helmet', 'Legendary', 15, 12, 5, 8, 8, 'helmet_1'),
    _recipe('r5', 'Signet of Minerva', 'Ring', 'Rare', 2, 6, 1, 0, 3, 'ring_1'),
    _recipe('r6', 'Gauntlets of Hercules', 'Gloves', 'Rare', 4, 3, 1, 6, 5, 'gloves_1'),
    _recipe('r7', 'Sandals of Mercury', 'Shoes', 'Rare', 3, 3, 1, 7, 5, 'shoes_1'),
    _recipe('r8', 'Amulet of Apollo', 'Amulet', 'Epic', 3, 10, 3, 2, 7, 'amulet_1'),
    _recipe('r9', 'Spatha of Victory', 'Weapon', 'Epic', 14, 8, 3, 4, 10, 'weapon_2'),
    _recipe('r10', 'Aegis of Minerva', 'Shield', 'Legendary', 20, 16, 6, 10, 14, 'shield_2'),
    _recipe('r11', 'Lorica Squamata of Mars', 'Armor', 'Epic', 18, 12, 3, 10, 16, 'armor_4'),
    _recipe('r12', 'Thracian Champion Helm', 'Helmet', 'Legendary', 22, 16, 6, 8, 20, 'helmet_4'),
    _recipe('r13', 'Sica of the Thracian', 'Weapon', 'Legendary', 28, 14, 7, 10, 24, 'weapon_6'),
    _recipe('r14', 'Greaves of Achilles', 'Shoes', 'Legendary', 24, 20, 8, 14, 28, 'shoes_2'),
    _recipe('r15', 'Torc of Boudica', 'Amulet', 'Legendary', 10, 30, 10, 6, 32, 'amulet_2'),
    _recipe('r16', 'Aspis of Olympus', 'Shield', 'Legendary', 34, 28, 12, 16, 36, 'shield_2'),
]

ARENA_TITLES = [
    {'MaxRank': 1, 'Title': 'Champion of Rome'},
    {'MaxRank': 3, 'Title': 'Hero of the Colosseum'},
    {'MaxRank': 10, 'Title': 'Veteran Gladiator'},
    {'MaxRank': LADDER_SIZE, 'Title': 'Tiro (Recruit)'},
]

ARENA_NAMES = [
    'Tiberius', 'Cassius', 'Brutus', 'Varro', 'Priscus',
    'Septimius', 'Valerius', 'Hadrian', 'Claudius', 'Lucius',
    'Aurelius', 'Commodus', 'Cornelius', 'Severus', 'Domitian',
    'Titus', 'Vespian', 'Trajan', 'Marcus Antonius', 'Spartacus',
]

def _labor(id_, number, title, level, monster, boon, story, gold, rubies):
    return {'Id': id_, 'Number': number, 'Title': title, 'ReqLevel': level, 'Monster': monster, 'Boon': boon,
            'Story': story, 'Gold': gold, 'Rubies': rubies}


# The Twelve Labors of Hercules: one-off boss challenges, done in order. Each grants a permanent boon
# (added to the gladiator's special effects). The monsters do not scale, so out-levelling them helps.
LABOR_ENERGY_COST = 4
LABORS = [
    _labor('labor1', 'I', 'The Nemean Lion', 6, _gen('L1', 'Lion of Nemea', 7, hp=2.59, dmg=1.81, armor=2.0),
           {'ArmorPct': 5}, 'Its golden hide turns every blade. Strangle it and wear its pelt.', 600, 1),
    _labor('labor2', 'II', 'The Lernaean Hydra', 9, _gen('L2', 'Lernaean Hydra', 10, hp=2.38, dmg=1.19),
           {'RegenPct': 20}, 'Cut off one head and two grow back. Burn the stumps.', 1100, 1),
    _labor('labor3', 'III', 'The Ceryneian Hind', 12, _gen('L3', 'Ceryneian Hind', 13, hp=1.43, dmg=1.1, dex=1.3, agi=1.8),
           {'CritBonus': 2}, "Artemis' golden-horned hind outruns arrows. Hunt it for a year if you must.", 1800, 1),
    _labor('labor4', 'IV', 'The Erymanthian Boar', 15, _gen('L4', 'Erymanthian Boar', 16, hp=2.24, dmg=1.52, agi=0.7),
           {'HPPct': 5}, 'Drive the great boar into the snowfields and take it alive.', 2600, 2),
    _labor('labor5', 'V', 'The Augean Stables', 18, _gen('L5', 'Alpheus the River God', 19, hp=1.65, dmg=1.03, armor=1.3),
           {'GoldPct': 10}, 'King Augeas will pay a tenth of his herds if you divert a river through his stables.', 3500, 2),
    _labor('labor6', 'VI', 'The Stymphalian Birds', 21, _gen('L6', 'Stymphalian Flock', 22, hp=1.39, dmg=1.09, dex=1.3, agi=1.5),
           {'DamagePct': 4}, 'Rattle the bronze krotala of Athena and shoot the man-eating birds out of the sky.', 4500, 2),
    _labor('labor7', 'VII', 'The Cretan Bull', 24, _gen('L7', 'Cretan Bull', 25, hp=2.03, dmg=1.43, agi=0.6),
           {'BlockBonus': 3}, "Poseidon's white bull is ravaging Crete. Wrestle it to the ground.", 5600, 2),
    _labor('labor8', 'VIII', 'The Mares of Diomedes', 27, _gen('L8', 'Mares of Diomedes', 28, hp=1.57, dmg=1.31, dex=1.2),
           {'LifeSteal': 2}, 'The Thracian king feeds his horses on human flesh. Tame them.', 6800, 3),
    _labor('labor9', 'IX', 'The Girdle of Hippolyta', 30, _gen('L9', 'Hippolyta, Amazon Queen', 31, hp=1.32, dmg=1.13, dex=1.4, agi=1.4),
           {'XPPct': 10}, 'Bring back the war-belt of the Amazon queen, a gift from Ares himself.', 8000, 3),
    _labor('labor10', 'X', 'The Cattle of Geryon', 33, _gen('L10', 'Geryon', 34, hp=1.6, dmg=1.06, armor=1.3, agi=0.7),
           {'ArmorPct': 5}, 'At the edge of the world, the three-bodied giant guards his red cattle.', 9600, 3),
    _labor('labor11', 'XI', 'The Apples of the Hesperides', 36, _gen('L11', 'Ladon', 37, hp=1.36, dmg=0.94, armor=1.4),
           {'HPPct': 5}, 'The hundred-headed dragon coils around the tree of golden apples.', 11500, 4),
    _labor('labor12', 'XII', 'The Capture of Cerberus', 40, _gen('L12', 'Cerberus Unchained', 41, hp=1.36, dmg=0.93, armor=1.3),
           {'DamagePct': 6}, 'Descend to the Underworld and carry its three-headed guardian into the light, unarmed.', 15000, 5),
]
LABORS_COMPLETE_REWARD = {'Name': 'Club of Hercules', 'Type': 'Weapon', 'IconSvg': 'weapon_9',
                          'Effects': {'DamagePct': 12, 'CritBonus': 4, 'LifeSteal': 4}}

# Battle series: fight the same expedition monster several times in a row.
SERIES_SIZES = [3, 5, 10]

# The Imperial Decree: a daily reward with a 7-day cycle. Missing a day restarts the cycle.
DAILY_REWARDS = [
    {'Day': 1, 'Icon': '🪙', 'Text': 'A purse of gold', 'Gold': 3},
    {'Day': 2, 'Icon': '⚡', 'Text': 'Full energy and gold', 'Gold': 2, 'Energy': True},
    {'Day': 3, 'Icon': '⛏️', 'Text': 'Forge materials', 'Materials': {'IronStash': 6, 'BronzeStash': 5, 'LeatherStash': 6}},
    {'Day': 4, 'Icon': '💰', 'Text': 'A heavy purse of gold', 'Gold': 5},
    {'Day': 5, 'Icon': '💎', 'Text': 'A ruby and raw rubies for the forge', 'Rubies': 1,
     'Materials': {'RubyStash': 3}},
    {'Day': 6, 'Icon': '🎁', 'Text': 'A Rare piece of gear', 'Item': 'Rare'},
    {'Day': 7, 'Icon': '👑', 'Text': "The Emperor's gift: 3 rubies and an Epic piece of gear", 'Rubies': 3, 'Item': 'Epic'},
]

# Reforging rerolls an item's prefix and suffix.
def reforge_cost(level):
    return {'Gold': 60 + 20 * level, 'Bronze': 3, 'Ruby': 1}


STAT_KEYS = ['FightsWon', 'FightsLost', 'MonstersSlain', 'ArenaWins', 'ArenaLosses', 'DungeonFloorsCleared',
             'DungeonsConquered', 'GoldEarned', 'ItemsLooted', 'ItemsCrafted', 'ItemsEnhanced', 'QuestsCompleted',
             'RubiesEarned', 'SetPiecesFound', 'UniquesFound', 'BlessingsReceived', 'HonorSpent',
             'ItemsReforged', 'DailyClaims', 'BestDailyStreak', 'BestSeries']

QUEST_KINDS = ['expedition', 'monster', 'arena', 'dungeon']

SAVE_VERSION = 5

# Every creature that can be fought, for the Bestiary (in area order).
BESTIARY = ([m['Name'] for loc in sorted(LOCATIONS, key=lambda l: l['ReqLevel']) for m in loc['Monsters']]
            + [st['Monster']['Name'] for d in DUNGEONS for st in d['Stages']]
            + [labor['Monster']['Name'] for labor in LABORS])
