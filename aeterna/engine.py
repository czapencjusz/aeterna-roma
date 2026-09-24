"""The Game class: every player action and the time-based systems.

Actions never raise for bad input. When something is not allowed they add a
message to `game.notices` (shown to the player as a toast) and leave the state
unchanged. Fights return a combat-result dict for the combat report.
"""

import math

from . import combat
from .data import (ARENA_COOLDOWN_MS, ARENA_MILESTONES, ATTRIBUTES, COMBAT_SPEEDS, DUNGEON_ENERGY_COST, DUNGEONS,
                   ENERGY_REGEN_PER_MIN, GUILD_BUILDING_MAX, GUILD_BUILDINGS, GUILD_COST, GUILD_DONATIONS,
                   LADDER_SIZE, LOCATIONS, LOOT_CHANCE, MAX_ENHANCE, QUEST_ABANDON_WAIT_MS, RECIPES, RUBY_COST,
                   SLOT_FOR_TYPE, SLOTS, THEMES, VENDOR_DEFS, WORK_OPTIONS)
from .items import display_name, generate_item, is_equipment, sell_price
from .rules import (guild_building_cost, guild_level_from_buildings, heal_multiplier, hp_regen_per_min, min_fight_hp,
                    recalc_stats, training_cost, work_pay, xp_multiplier)
from .state import (dungeon_key, generate_quest, idle_work, new_game_state, new_guild, normalize_state,
                    quest_description, stock_vendor)
from .util import now_ms, pick, rand_int, roll, to_int, uid

GLADIATOR_NAME_MIN, GLADIATOR_NAME_MAX = 3, 20
GUILD_NAME_MIN, GUILD_NAME_MAX = 3, 24
GUILD_TAG_MIN, GUILD_TAG_MAX = 2, 5


def _index(value, sequence):
    """Validates an index coming from the UI. Returns an int or None."""
    index = to_int(value, -1)
    return index if 0 <= index < len(sequence) else None


def clean_name(value):
    """Trims and collapses whitespace in a player-entered name."""
    return ' '.join(value.split()) if isinstance(value, str) else ''


class Game:
    def __init__(self, state=None, clock=now_ms):
        self.clock = clock
        self.state = state if state is not None else new_game_state(clock())
        self.notices = []

    @classmethod
    def from_save(cls, raw, clock=now_ms):
        return cls(normalize_state(raw, clock()), clock)

    # ----------------------------------------------------------------- helpers

    @property
    def player(self):
        return self.state['Player']

    def notify(self, message):
        self.notices.append(message)

    def take_notices(self):
        notices, self.notices = self.notices, []
        return notices

    def gain_xp(self, xp):
        """Adds XP and applies level-ups. Returns the number of levels gained."""
        p = self.player
        p['XP'] += xp
        levels = 0
        while p['XP'] >= p['MaxXP']:
            p['XP'] -= p['MaxXP']
            p['Level'] += 1
            p['MaxXP'] = math.floor(p['MaxXP'] * 1.5)
            p['MaxEnergy'] += 2
            p['CurrentEnergy'] = p['MaxEnergy']
            for attr in ('Strength', 'Dexterity', 'Agility', 'Constitution'):
                p['Base' + attr] += 1
            recalc_stats(p)
            p['CurrentHP'] = p['MaxHP']
            levels += 1
        if levels:
            self.restock_vendors()
        return levels

    def restock_vendors(self):
        for key, definition in VENDOR_DEFS.items():
            if definition['Stock']:
                self.state['Vendors'][key] = {'Items': stock_vendor(key, self.player['Level'])}

    def add_guild_log(self, message):
        log = self.state['PlayerGuild']['Log']
        log.append(message)
        del log[:-50]

    def add_rubies(self, amount):
        self.player['Rubies'] += amount
        self.state['Stats']['RubiesEarned'] += amount

    def spend_rubies(self, cost):
        if self.player['Rubies'] < cost:
            self.notify('You need %d rubies. Earn them from dungeon bosses, divine tasks, and arena milestones.' % cost)
            return False
        self.player['Rubies'] -= cost
        return True

    # --------------------------------------------------------- time-based systems

    def apply_regen(self, now):
        """HP and energy regeneration. Unused fractions carry over. Returns True if anything changed."""
        s, p = self.state, self.player
        changed = False

        if not s['LastHPRegen'] <= now:  # also guards against the clock going backwards
            s['LastHPRegen'] = now
        if p['CurrentHP'] >= p['MaxHP']:
            s['LastHPRegen'] = now
        else:
            rate = hp_regen_per_min(s)
            gained = math.floor((now - s['LastHPRegen']) / 60000 * rate)
            if gained > 0:
                p['CurrentHP'] = min(p['MaxHP'], p['CurrentHP'] + gained)
                s['LastHPRegen'] = now if p['CurrentHP'] >= p['MaxHP'] else s['LastHPRegen'] + gained / rate * 60000
                changed = True

        if not s['LastEnergyRegen'] <= now:
            s['LastEnergyRegen'] = now
        if p['CurrentEnergy'] >= p['MaxEnergy']:
            s['LastEnergyRegen'] = now
        else:
            gained = math.floor((now - s['LastEnergyRegen']) / 60000 * ENERGY_REGEN_PER_MIN)
            if gained > 0:
                p['CurrentEnergy'] = min(p['MaxEnergy'], p['CurrentEnergy'] + gained)
                s['LastEnergyRegen'] = (now if p['CurrentEnergy'] >= p['MaxEnergy']
                                        else s['LastEnergyRegen'] + gained / ENERGY_REGEN_PER_MIN * 60000)
                changed = True
        return changed

    def work_end_time(self):
        work = self.state['ActiveWork']
        return work['StartTime'] + work['DurationHours'] * 3600 * 1000

    def complete_work_if_done(self, now):
        """Pays out a finished villa shift. Returns True when a payout happened."""
        work = self.state['ActiveWork']
        if not work['IsWorking'] or now < self.work_end_time():
            return False
        self.player['Gold'] += work['ExpectedGold']
        self.state['Stats']['GoldEarned'] += work['ExpectedGold']
        levels = self.gain_xp(work['ExpectedXP'])
        self.notify('🌾 Villa work finished: +%d gold, +%d XP%s' % (
            work['ExpectedGold'], work['ExpectedXP'],
            ' — you reached level %d!' % self.player['Level'] if levels else ''))
        self.state['ActiveWork'] = idle_work()
        return True

    def refresh_quest_slots(self, now):
        """Offers new quests in empty slots whose wait has passed. Returns True if anything changed."""
        changed = False
        for slot in self.state['QuestSlots']:
            if not slot['Quest'] and slot['NextAt'] <= now:
                slot['Quest'] = generate_quest(self.player)
                slot['NextAt'] = 0
                changed = True
        return changed

    def arena_cooldown_left(self, now):
        return max(0, self.state['ArenaCooldownUntil'] - now)

    def tick(self):
        """Runs the time-based systems.

        Returns 'all' when something needs a save and a full redraw (work paid out,
        new quest offered), 'sidebar' when only HP/energy changed, else 'none'.
        """
        now = self.clock()
        regen = self.apply_regen(now)
        work = self.complete_work_if_done(now)
        quests = self.refresh_quest_slots(now)
        if work or quests:
            return 'all'
        return 'sidebar' if regen else 'none'

    # ----------------------------------------------------------------- fights

    def can_fight(self):
        p = self.player
        if self.state['ActiveWork']['IsWorking']:
            self.notify('You are busy working at the villa. Finish or cancel the work first.')
            return False
        if p['CurrentHP'] < min_fight_hp(p):
            self.notify('You are too wounded to fight (need at least %d HP). Rest or drink a potion.' % min_fight_hp(p))
            return False
        return True

    def grant_rewards(self, result, xp, gold):
        xp = math.floor(xp * xp_multiplier(self.state))
        self.player['Gold'] += gold
        self.state['Stats']['GoldEarned'] += gold
        result['GoldGained'] = gold
        result['XPGained'] = xp
        result['LevelsGained'] = self.gain_xp(xp)

    def roll_loot(self, result):
        if roll() >= LOOT_CHANCE:
            return
        p = self.player
        item = generate_item(p['Level'])
        if len(p['Inventory']) < p['InventoryCapacity']:
            p['Inventory'].append(item)
            result['Loot'].append(item)
            self.state['Stats']['ItemsLooted'] += 1
        else:
            result['Notes'].append('You found %s, but your inventory is full.' % display_name(item))

    def check_arena_milestones(self, result):
        """Pays rubies the first time the player reaches each milestone rank."""
        s, p = self.state, self.player
        s['Stats']['BestArenaRank'] = min(s['Stats']['BestArenaRank'], p['ArenaRank'])
        for milestone in ARENA_MILESTONES:
            if p['ArenaRank'] <= milestone['Rank'] and milestone['Rank'] not in s['ArenaMilestonesClaimed']:
                s['ArenaMilestonesClaimed'].append(milestone['Rank'])
                self.add_rubies(milestone['Rubies'])
                result['RubiesGained'] += milestone['Rubies']
                result['Notes'].append('🏅 Milestone: first time in the top %d! +%d rubies'
                                       % (milestone['Rank'], milestone['Rubies']))

    def progress_quests(self, kind, monster_id, result):
        """Advances matching quests. Expedition wins also count towards "defeat monster X" quests."""
        for slot in self.state['QuestSlots']:
            quest = slot['Quest']
            if not quest or quest['Progress'] >= quest['Goal']:
                continue
            matches = ((quest['Kind'] == kind and kind != 'monster')
                       or (quest['Kind'] == 'monster' and kind == 'expedition' and quest['Target'] == monster_id))
            if not matches:
                continue
            quest['Progress'] += 1
            if quest['Progress'] >= quest['Goal'] and result is not None:
                result['Notes'].append('🏺 Divine task complete: %s. Claim it at the Pantheon!' % quest_description(quest))

    def start_expedition(self, location_index, monster_index):
        li = _index(location_index, LOCATIONS)
        if li is None:
            return None
        location = LOCATIONS[li]
        mi = _index(monster_index, location['Monsters'])
        if mi is None:
            return None
        p = self.player
        if p['Level'] < location['ReqLevel']:
            self.notify('%s requires level %d.' % (location['Name'], location['ReqLevel']))
            return None
        if p['CurrentEnergy'] < location['EnergyCost']:
            self.notify('Not enough energy (%d needed).' % location['EnergyCost'])
            return None
        if not self.can_fight():
            return None

        p['CurrentEnergy'] -= location['EnergyCost']
        monster = combat.scale_monster(location['Monsters'][mi], p['Level'], location['ReqLevel'])
        result = combat.run_fight(self.state, 'Expedition: ' + monster['Name'], combat.monster_combatant(monster))
        result['EnemyArt'] = monster['Name']
        if result['IsVictory']:
            self.state['Stats']['MonstersSlain'] += 1
            self.grant_rewards(result, monster['XPReward'], rand_int(monster['MinGold'], monster['MaxGold']))
            self.roll_loot(result)
            self.progress_quests('expedition', monster['Id'], result)
        return result

    def challenge_arena(self, ladder_index):
        s, p = self.state, self.player
        idx = _index(ladder_index, s['ArenaLadder'])
        if idx is None:
            return None
        opponent = s['ArenaLadder'][idx]
        now = self.clock()
        if self.arena_cooldown_left(now) > 0:
            wait = format_duration(self.arena_cooldown_left(now))
            self.notify('The arena master needs time to prepare the next bout (%s).' % wait)
            return None
        if not self.can_fight():
            return None

        rival = combat.arena_opponent_stats(opponent, p)
        result = combat.run_fight(s, 'Arena Challenge: ' + rival['Name'], combat.arena_combatant(rival))
        result['EnemyArt'] = opponent['IconSvg']
        s['ArenaCooldownUntil'] = now + ARENA_COOLDOWN_MS

        if result['IsVictory']:
            self.grant_rewards(result, rival['Level'] * 15 + 20, rival['Level'] * 45 + rand_int(20, 79))
            honor = 10 + max(0, LADDER_SIZE - opponent['Rank'])
            p['Honor'] += honor
            result['Notes'].append('+%d Honor' % honor)
            if opponent['Rank'] < p['ArenaRank']:
                p['ArenaRank'], opponent['Rank'] = opponent['Rank'], p['ArenaRank']
                result['Notes'].append('You climb the ladder to rank #%d!' % p['ArenaRank'])
            s['Stats']['ArenaWins'] += 1
            self.check_arena_milestones(result)
            self.progress_quests('arena', None, result)
        else:
            s['Stats']['ArenaLosses'] += 1
        return result

    def enter_dungeon(self, dungeon_index):
        di = _index(dungeon_index, DUNGEONS)
        if di is None:
            return None
        dungeon = DUNGEONS[di]
        progress = self.state['DungeonProgress'][dungeon_key(dungeon)]
        p = self.player
        if progress['IsCompleted']:
            self.notify('%s is already conquered.' % dungeon['Name'])
            return None
        if p['Level'] < dungeon['ReqLevel']:
            self.notify('%s requires level %d.' % (dungeon['Name'], dungeon['ReqLevel']))
            return None
        if p['CurrentEnergy'] < DUNGEON_ENERGY_COST:
            self.notify('Not enough energy (%d needed).' % DUNGEON_ENERGY_COST)
            return None
        if not self.can_fight():
            return None

        stage = dungeon['Stages'][progress['CurrentStage'] - 1]
        p['CurrentEnergy'] -= DUNGEON_ENERGY_COST
        monster = combat.scale_monster(stage['Monster'], p['Level'], dungeon['ReqLevel'])
        result = combat.run_fight(self.state, '%s — %s' % (dungeon['Name'], stage['Name']), combat.monster_combatant(monster))
        result['EnemyArt'] = monster['Name']
        if result['IsVictory']:
            stats = self.state['Stats']
            stats['MonstersSlain'] += 1
            stats['DungeonFloorsCleared'] += 1
            self.grant_rewards(result, monster['XPReward'], rand_int(monster['MinGold'], monster['MaxGold']))
            self.roll_loot(result)
            if stage['IsBoss']:
                # Generous on the first conquest; repeat runs only occasionally drop a ruby.
                rubies = rand_int(2, 3) if progress['Conquests'] == 0 else (1 if roll() < 0.2 else 0)
                if rubies:
                    self.add_rubies(rubies)
                    result['RubiesGained'] += rubies
            if progress['CurrentStage'] < len(dungeon['Stages']):
                progress['CurrentStage'] += 1
                result['Notes'].append('You advance to floor %d of %d.' % (progress['CurrentStage'], len(dungeon['Stages'])))
            else:
                progress['IsCompleted'] = True
                progress['Conquests'] += 1
                stats['DungeonsConquered'] += 1
                result['Notes'].append('🏆 %s has been conquered!' % dungeon['Name'])
            self.progress_quests('dungeon', None, result)
        return result

    def restart_dungeon(self, dungeon_index):
        di = _index(dungeon_index, DUNGEONS)
        if di is None:
            return
        progress = self.state['DungeonProgress'][dungeon_key(DUNGEONS[di])]
        progress['CurrentStage'] = 1
        progress['IsCompleted'] = False

    # ------------------------------------------------------------ character & items

    def train(self, attribute_index):
        ai = _index(attribute_index, ATTRIBUTES)
        if ai is None:
            return
        attr = ATTRIBUTES[ai]
        p = self.player
        cost = training_cost(self.state, p['Base' + attr])
        if p['Gold'] < cost:
            self.notify('Training %s costs %d gold.' % (attr, cost))
            return
        p['Gold'] -= cost
        p['Base' + attr] += 1
        recalc_stats(p)

    def equip(self, inventory_index):
        p = self.player
        idx = _index(inventory_index, p['Inventory'])
        if idx is None:
            return
        item = p['Inventory'][idx]
        if item['Type'] == 'Potion':
            self.use_potion(idx)
            return
        slot = SLOT_FOR_TYPE.get(item['Type'])
        if not slot:
            self.notify('This item cannot be equipped.')
            return
        if p['Level'] < item['LevelRequirement']:
            self.notify('You must be level %d to equip this.' % item['LevelRequirement'])
            return
        del p['Inventory'][idx]
        if p['Equipment'][slot]:
            p['Inventory'].append(p['Equipment'][slot])
        p['Equipment'][slot] = item
        recalc_stats(p)

    def use_potion(self, inventory_index):
        p = self.player
        idx = _index(inventory_index, p['Inventory'])
        if idx is None or p['Inventory'][idx]['Type'] != 'Potion':
            return
        item = p['Inventory'][idx]
        heal_wasted = not item['HealAmount'] or p['CurrentHP'] >= p['MaxHP']
        energy_wasted = not item['EnergyAmount'] or p['CurrentEnergy'] >= p['MaxEnergy']
        if heal_wasted and energy_wasted:
            self.notify('You would gain nothing from drinking this right now.')
            return
        del p['Inventory'][idx]
        if item['HealAmount'] > 0:
            heal = math.floor(item['HealAmount'] * heal_multiplier(p))
            p['CurrentHP'] = min(p['MaxHP'], p['CurrentHP'] + heal)
        if item['EnergyAmount'] > 0:
            p['CurrentEnergy'] = min(p['MaxEnergy'], p['CurrentEnergy'] + item['EnergyAmount'])

    def unequip(self, slot):
        p = self.player
        if slot not in SLOTS or not p['Equipment'][slot]:
            return
        if len(p['Inventory']) >= p['InventoryCapacity']:
            self.notify('Your inventory is full.')
            return
        p['Inventory'].append(p['Equipment'][slot])
        p['Equipment'][slot] = None
        recalc_stats(p)

    def sell(self, inventory_index):
        p = self.player
        idx = _index(inventory_index, p['Inventory'])
        if idx is None:
            return
        p['Gold'] += sell_price(p['Inventory'][idx])
        del p['Inventory'][idx]

    def junk_items(self):
        """Common, un-enhanced equipment: what "Sell Common Gear" sells."""
        return [it for it in self.player['Inventory'] if is_equipment(it) and it['Rarity'] == 'Common' and not it['Upgrade']]

    def sell_junk(self):
        junk = self.junk_items()
        if not junk:
            self.notify('No common gear to sell.')
            return
        p = self.player
        p['Gold'] += sum(sell_price(it) for it in junk)
        junk_ids = {id(it) for it in junk}
        p['Inventory'] = [it for it in p['Inventory'] if id(it) not in junk_ids]

    def smelt(self, inventory_index):
        p = self.player
        idx = _index(inventory_index, p['Inventory'])
        if idx is None:
            return
        item = p['Inventory'][idx]
        if item['Type'] == 'Potion':
            self.notify('Potions cannot be smelted.')
            return
        s = self.state
        s['IronStash'] += item['SmeltIron']
        s['BronzeStash'] += item['SmeltBronze']
        s['RubyStash'] += item['SmeltRuby']
        s['LeatherStash'] += item['SmeltLeather']
        del p['Inventory'][idx]
        self.notify('Smelted into %d iron, %d bronze, %d ruby, %d leather.' % (
            item['SmeltIron'], item['SmeltBronze'], item['SmeltRuby'], item['SmeltLeather']))

    def craft(self, recipe_index):
        ri = _index(recipe_index, RECIPES)
        if ri is None:
            return
        recipe = RECIPES[ri]
        s, p = self.state, self.player
        if p['Level'] < recipe['ReqLevel']:
            self.notify('%s requires level %d.' % (recipe['Name'], recipe['ReqLevel']))
            return
        if (s['IronStash'] < recipe['ReqIron'] or s['BronzeStash'] < recipe['ReqBronze']
                or s['RubyStash'] < recipe['ReqRuby'] or s['LeatherStash'] < recipe['ReqLeather']):
            self.notify('Not enough materials. Smelt unwanted gear to gather more.')
            return
        if len(p['Inventory']) >= p['InventoryCapacity']:
            self.notify('Your inventory is full.')
            return
        s['IronStash'] -= recipe['ReqIron']
        s['BronzeStash'] -= recipe['ReqBronze']
        s['RubyStash'] -= recipe['ReqRuby']
        s['LeatherStash'] -= recipe['ReqLeather']
        item = generate_item(p['Level'], recipe['ResultType'], recipe['ResultRarity'])
        item.update(Name=recipe['Name'], Prefix='', Suffix='', IconSvg=recipe['IconSvg'])
        p['Inventory'].append(item)
        s['Stats']['ItemsCrafted'] += 1
        self.notify('🔨 Forged %s!' % item['Name'])

    @staticmethod
    def enhance_cost(item):
        n = item['Upgrade']
        return {'Gold': (n + 1) * 100 + item['LevelRequirement'] * 20, 'Iron': 3 * (n + 1), 'Bronze': 2 * (n + 1),
                'Leather': n + 1, 'Ruby': n - 1 if n >= 2 else 0}

    def can_afford_enhance(self, cost):
        s = self.state
        return (self.player['Gold'] >= cost['Gold'] and s['IronStash'] >= cost['Iron'] and s['BronzeStash'] >= cost['Bronze']
                and s['LeatherStash'] >= cost['Leather'] and s['RubyStash'] >= cost['Ruby'])

    def enhance(self, location, key):
        """location 0 = equipped slot index (into SLOTS), 1 = inventory index."""
        p = self.player
        loc = to_int(location, -1)
        if loc == 0:
            si = _index(key, SLOTS)
            item = p['Equipment'][SLOTS[si]] if si is not None else None
        elif loc == 1:
            ii = _index(key, p['Inventory'])
            item = p['Inventory'][ii] if ii is not None else None
        else:
            item = None
        if not item or not is_equipment(item):
            return
        if item['Upgrade'] >= MAX_ENHANCE:
            self.notify('This item is already fully enhanced.')
            return
        cost = self.enhance_cost(item)
        if not self.can_afford_enhance(cost):
            self.notify('Not enough gold or materials for this enhancement.')
            return
        s = self.state
        p['Gold'] -= cost['Gold']
        s['IronStash'] -= cost['Iron']
        s['BronzeStash'] -= cost['Bronze']
        s['LeatherStash'] -= cost['Leather']
        s['RubyStash'] -= cost['Ruby']

        def grow(value):
            return value + max(1, math.ceil(value * 0.1)) if value > 0 else value
        item['MinDamage'] = grow(item['MinDamage'])
        item['MaxDamage'] = grow(item['MaxDamage'])
        item['Armor'] = grow(item['Armor'])
        if not item['MinDamage'] and not item['Armor']:
            # Jewellery has no damage or armor: strengthen its attribute bonuses instead.
            for attr in ATTRIBUTES:
                if item[attr] > 0:
                    item[attr] += 1
        item['Price'] = math.floor(item['Price'] * 1.2)
        item['Upgrade'] += 1
        s['Stats']['ItemsEnhanced'] += 1
        recalc_stats(p)
        self.notify('✨ %s glows with new strength!' % display_name(item))

    # ---------------------------------------------------------------- merchants

    def buy(self, vendor_key, item_index):
        definition = VENDOR_DEFS.get(vendor_key)
        if not definition:
            return
        vendor = self.state['Vendors'][vendor_key]
        idx = _index(item_index, vendor['Items'])
        if idx is None:
            return
        item = vendor['Items'][idx]
        p = self.player
        if p['Gold'] < item['Price']:
            self.notify('You need %d gold.' % item['Price'])
            return
        if len(p['Inventory']) >= p['InventoryCapacity']:
            self.notify('Your inventory is full.')
            return
        p['Gold'] -= item['Price']
        if definition['Stock']:
            del vendor['Items'][idx]
            p['Inventory'].append(item)
            vendor['Items'].append(generate_item(p['Level'], pick(definition['Stock'])))
        else:
            p['Inventory'].append(dict(item, Id=uid()))  # the apothecary never runs out of potions

    # ----------------------------------------------------------------- villa work

    def start_work(self, hours):
        hours = to_int(hours, 0)
        if hours not in WORK_OPTIONS or self.state['ActiveWork']['IsWorking']:
            return
        gold, xp = work_pay(self.state, hours)
        self.state['ActiveWork'] = {'IsWorking': True, 'DurationHours': hours, 'StartTime': self.clock(),
                                    'ExpectedGold': gold, 'ExpectedXP': xp}

    def cancel_work(self):
        self.state['ActiveWork'] = idle_work()

    # ---------------------------------------------------------------------- guild

    def create_guild(self, name, tag):
        p, s = self.player, self.state
        if s['PlayerGuild']['HasGuild']:
            return
        if p['Gold'] < GUILD_COST:
            self.notify('Founding a guild costs %d gold.' % GUILD_COST)
            return
        name = clean_name(name)
        tag = clean_name(tag).upper()
        if not GUILD_NAME_MIN <= len(name) <= GUILD_NAME_MAX:
            self.notify('The guild name must be %d-%d characters.' % (GUILD_NAME_MIN, GUILD_NAME_MAX))
            return
        if not GUILD_TAG_MIN <= len(tag) <= GUILD_TAG_MAX:
            self.notify('The guild tag must be %d-%d characters.' % (GUILD_TAG_MIN, GUILD_TAG_MAX))
            return
        p['Gold'] -= GUILD_COST
        s['PlayerGuild'] = dict(new_guild(), HasGuild=True, Name=name, Tag=tag, Level=1)
        self.add_guild_log('Guild founded by %s.' % p['Name'])

    def donate(self, option_index):
        oi = _index(option_index, GUILD_DONATIONS)
        guild = self.state['PlayerGuild']
        if oi is None or not guild['HasGuild']:
            return
        amount = GUILD_DONATIONS[oi]
        p = self.player
        if p['Gold'] < amount:
            self.notify('You need %d gold to donate that much.' % amount)
            return
        p['Gold'] -= amount
        guild['GoldVault'] += amount
        self.add_guild_log('%s donated %d gold to the vault.' % (p['Name'], amount))

    def upgrade_building(self, key):
        guild = self.state['PlayerGuild']
        definition = GUILD_BUILDINGS.get(key)
        if not definition or not guild['HasGuild']:
            return
        level = guild['Buildings'][key]
        if level >= GUILD_BUILDING_MAX:
            self.notify('%s is already at maximum level.' % definition['Name'])
            return
        cost = guild_building_cost(level)
        if guild['GoldVault'] < cost:
            self.notify('The guild vault needs %d gold for this upgrade.' % cost)
            return
        guild['GoldVault'] -= cost
        guild['Buildings'][key] = level + 1
        old_level = guild['Level']
        guild['Level'] = guild_level_from_buildings(guild['Buildings'])
        self.add_guild_log('%s upgraded to level %d.' % (definition['Name'], level + 1))
        if guild['Level'] > old_level:
            self.add_guild_log('The guild reached level %d!' % guild['Level'])
        recalc_stats(self.player)

    # --------------------------------------------------------------------- quests

    def claim_quest(self, slot_index):
        slots = self.state['QuestSlots']
        si = _index(slot_index, slots)
        if si is None:
            return
        quest = slots[si]['Quest']
        if not quest or quest['Progress'] < quest['Goal']:
            return
        p = self.player
        xp = math.floor(quest['RewardXP'] * xp_multiplier(self.state))
        p['Gold'] += quest['RewardGold']
        self.state['Stats']['GoldEarned'] += quest['RewardGold']
        levels = self.gain_xp(xp)
        if quest['RewardRubies']:
            self.add_rubies(quest['RewardRubies'])
        self.state['Stats']['QuestsCompleted'] += 1
        slots[si] = {'Quest': generate_quest(p), 'NextAt': 0}
        self.notify('🏺 The gods are pleased: +%d gold, +%d XP%s%s' % (
            quest['RewardGold'], xp, ', +%d ruby' % quest['RewardRubies'] if quest['RewardRubies'] else '',
            ' — you reached level %d!' % p['Level'] if levels else ''))

    def abandon_quest(self, slot_index):
        slots = self.state['QuestSlots']
        si = _index(slot_index, slots)
        if si is None or not slots[si]['Quest']:
            return
        slots[si] = {'Quest': None, 'NextAt': self.clock() + QUEST_ABANDON_WAIT_MS}

    # ------------------------------------------------------------------ ruby shop

    def ruby_refill_energy(self):
        p = self.player
        if p['CurrentEnergy'] >= p['MaxEnergy']:
            self.notify('Your energy is already full.')
            return
        if self.spend_rubies(RUBY_COST['refillEnergy']):
            p['CurrentEnergy'] = p['MaxEnergy']

    def ruby_skip_arena(self):
        if self.arena_cooldown_left(self.clock()) <= 0:
            return
        if self.spend_rubies(RUBY_COST['skipArena']):
            self.state['ArenaCooldownUntil'] = 0

    def ruby_restock(self, vendor_key):
        definition = VENDOR_DEFS.get(vendor_key)
        if not definition or not definition['Stock']:
            return
        if self.spend_rubies(RUBY_COST['restock']):
            self.state['Vendors'][vendor_key] = {'Items': stock_vendor(vendor_key, self.player['Level'])}

    # ------------------------------------------------------------ settings & game

    def rename(self, name):
        name = clean_name(name)
        if not GLADIATOR_NAME_MIN <= len(name) <= GLADIATOR_NAME_MAX:
            self.notify('A gladiator name must be %d-%d characters.' % (GLADIATOR_NAME_MIN, GLADIATOR_NAME_MAX))
            return
        self.player['Name'] = name

    def set_theme(self, key):
        if key in THEMES:
            self.state['Settings']['ThemeMode'] = key

    def set_combat_speed(self, key):
        if key in COMBAT_SPEEDS:
            self.state['Settings']['CombatSpeed'] = key

    def set_audio_muted(self, muted):
        self.state['Settings']['AudioMuted'] = muted is True

    def reset(self, name=None):
        """Starts a new game, keeping the player's settings."""
        settings = self.state['Settings']
        self.state = new_game_state(self.clock())
        self.state['Settings'] = settings
        if name is not None and clean_name(name):
            self.rename(name)

    def load_save(self, raw):
        self.state = normalize_state(raw, self.clock())

    def catch_up(self):
        """Applies everything that happened while the game was closed."""
        now = self.clock()
        self.apply_regen(now)
        self.complete_work_if_done(now)
        self.refresh_quest_slots(now)


def format_duration(ms):
    total = max(0, math.ceil(ms / 1000))
    hours, minutes, seconds = total // 3600, (total % 3600) // 60, total % 60
    if hours:
        return '%d:%02d:%02d' % (hours, minutes, seconds)
    return '%d:%02d' % (minutes, seconds)
