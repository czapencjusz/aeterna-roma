"""Static game data and tuning constants for Aeterna Roma."""

ITEM_TYPES = ['Weapon', 'Armor', 'Helmet', 'Shield', 'Ring', 'Amulet', 'Gloves', 'Shoes', 'Potion', 'Material']
EQUIP_TYPES = ITEM_TYPES[:8]
RARITIES = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']
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
]

# Base item names -> matching icon, so a "Trident" looks like a trident.
ICON_BY_NAME = {
    'Gladius': 'weapon_1', 'Centurion Gladius': 'weapon_1', 'Spatha': 'weapon_2', 'Centurion Sword': 'weapon_2',
    'Spatha of Victory': 'weapon_2', 'Pugio Dagger': 'weapon_3', 'Trident': 'weapon_4', 'Halberd': 'weapon_5',
    'Galea Helmet': 'helmet_1', 'Legionary Helm': 'helmet_1', 'Golden Galea Helmet': 'helmet_1',
    'Centurion Crest': 'helmet_2', 'Gladiator Mask': 'helmet_3',
    'Lorica Segmentata': 'armor_1', 'Imperial Lorica Segmentata': 'armor_1', 'Lorica Hamata': 'armor_2',
    'Gladiator Cuirass': 'armor_3', 'Bronze Breastplate': 'armor_3',
    'Scutum Shield': 'shield_1', 'Tower Shield': 'shield_1', 'Scutum of Mars': 'shield_1',
    'Parma Round Shield': 'shield_2', 'Aegis of Minerva': 'shield_2', 'Gladiator Buckler': 'shield_3',
}


def _m(id_, name, level, hp, mn, mx, armor, dex, agi, xp, gmin, gmax):
    return {'Id': id_, 'Name': name, 'Level': level, 'MaxHP': hp, 'MinDamage': mn, 'MaxDamage': mx, 'Armor': armor,
            'Dexterity': dex, 'Agility': agi, 'XPReward': xp, 'MinGold': gmin, 'MaxGold': gmax}


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
    {'Id': 3, 'Name': 'Ancient Forest', 'ReqLevel': 6, 'EnergyCost': 2,
     'Description': 'Deep mystical woods harboring rogue Centaurs, Werewolves, and Ancient Treants.',
     'Monsters': [
         _m('m7', 'Centaur Scout', 6, 190, 16, 26, 12, 18, 18, 100, 90, 160),
         _m('m8', 'Timber Werewolf', 7, 230, 20, 32, 14, 22, 20, 130, 120, 210),
         _m('m9', 'Corrupted Treant', 8, 300, 24, 38, 22, 10, 8, 170, 150, 280),
     ]},
    {'Id': 4, 'Name': 'Barbarian Camp', 'ReqLevel': 9, 'EnergyCost': 3,
     'Description': 'Fierce hostile war camp of Northern Barbarian Warriors and Chieftains.',
     'Monsters': [
         _m('m10', 'Barbarian Berserker', 9, 360, 28, 45, 18, 24, 22, 220, 200, 350),
         _m('m11', 'Warlord Chieftain', 10, 480, 35, 58, 25, 28, 24, 300, 300, 500),
     ]},
    {'Id': 5, 'Name': 'Sands of Aegyptus', 'ReqLevel': 12, 'EnergyCost': 3,
     'Description': 'Scorching dunes along the Nile where giant scorpions lurk and ancient tombs guard their secrets.',
     'Monsters': [
         _m('m12', 'Giant Scorpion', 12, 520, 38, 60, 28, 30, 24, 380, 380, 600),
         _m('m13', 'Tomb Guardian', 13, 600, 42, 66, 36, 26, 20, 450, 450, 700),
         _m('m14', 'Riddling Sphinx', 14, 700, 48, 74, 32, 34, 28, 540, 520, 820),
     ]},
    {'Id': 6, 'Name': 'Dacian Frontier', 'ReqLevel': 16, 'EnergyCost': 4,
     'Description': "Wild mountain borderlands where King Decebalus' warriors and wolf-cult priests defy the legions.",
     'Monsters': [
         _m('m15', 'Dacian Falxman', 16, 840, 56, 86, 40, 38, 30, 700, 650, 1000),
         _m('m16', 'Wolf Priest', 17, 920, 60, 92, 38, 42, 34, 800, 720, 1100),
         _m('m17', 'Champion of Decebalus', 18, 1080, 66, 102, 48, 44, 32, 950, 850, 1300),
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
    {'Id': 3, 'Name': 'Forge of Vulcan', 'ReqLevel': 13,
     'Description': "Beneath Mount Etna, the smith-god's servants guard the fires where the weapons of the gods are made.",
     'Stages': [
         _stage('Lava Tunnels', False, _m('', 'Fire Salamander', 13, 560, 42, 64, 30, 32, 26, 420, 420, 650)),
         _stage('Cyclops Smithy', False, _m('', 'Cyclops Smith', 14, 720, 50, 78, 40, 26, 18, 520, 500, 800)),
         _stage('Heart of the Mountain', True, _m('', 'Avatar of Vulcan', 16, 1000, 58, 90, 46, 36, 28, 900, 1000, 1600)),
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

STAT_KEYS = ['FightsWon', 'FightsLost', 'MonstersSlain', 'ArenaWins', 'ArenaLosses', 'DungeonFloorsCleared',
             'DungeonsConquered', 'GoldEarned', 'ItemsLooted', 'ItemsCrafted', 'ItemsEnhanced', 'QuestsCompleted',
             'RubiesEarned']

QUEST_KINDS = ['expedition', 'monster', 'arena', 'dungeon']

SAVE_VERSION = 3
