using System;
using System.Collections.Generic;

namespace GladiatusOffline
{
    public class CombatTurn
    {
        public int TurnNumber { get; set; }
        public string AttackerName { get; set; }
        public string DefenderName { get; set; }
        public string ActionType { get; set; } // Hit, Miss, Critical, Block, DoubleStrike
        public int Damage { get; set; }
        public int AttackerHP { get; set; }
        public int DefenderHP { get; set; }
        public string Message { get; set; }
        public bool AttackerIsPlayer { get; set; }
    }

    public class CombatResult
    {
        public bool IsVictory { get; set; }
        public string WinnerName { get; set; }
        public List<CombatTurn> Turns { get; set; }
        public int XPGained { get; set; }
        public int GoldGained { get; set; }
        public List<Item> Loot { get; set; }
        public int InitialPlayerHP { get; set; }
        public int InitialEnemyHP { get; set; }
        public string CombatType { get; set; }

        public CombatResult()
        {
            Turns = new List<CombatTurn>();
            Loot = new List<Item>();
        }
    }

    public static class CombatEngine
    {
        private static Random rand = new Random();

        public static CombatResult FightMonster(Gladiator player, Monster monster)
        {
            CombatResult result = new CombatResult();
            result.CombatType = "Expedition: " + monster.Name;
            result.InitialPlayerHP = player.CurrentHP;
            result.InitialEnemyHP = monster.MaxHP;

            int pHP = player.CurrentHP;
            int eHP = monster.MaxHP;
            int turn = 1;

            int pDex = player.GetTotalDexterity();
            int pAgi = player.GetTotalAgility();
            int pCha = player.GetTotalCharisma();
            int pArmor = player.GetTotalArmor();

            bool hasShield = player.Equipment.ContainsKey("Shield") && player.Equipment["Shield"] != null;

            while (pHP > 0 && eHP > 0 && turn <= 25)
            {
                // Player turn
                ExecuteTurn(turn, player.Name, monster.Name, pDex, monster.Agility, pCha, player.GetMinDamage(), player.GetMaxDamage(), monster.Armor, false, ref eHP, ref pHP, true, result.Turns);
                if (eHP <= 0) break;

                // Monster turn
                ExecuteTurn(turn, monster.Name, player.Name, monster.Dexterity, pAgi, 5, monster.MinDamage, monster.MaxDamage, pArmor, hasShield, ref pHP, ref eHP, false, result.Turns);
                if (pHP <= 0) break;

                turn++;
            }

            player.CurrentHP = Math.Max(0, pHP);
            if (pHP > 0 && eHP <= 0)
            {
                result.IsVictory = true;
                result.WinnerName = player.Name;
                result.XPGained = monster.XPReward;
                result.GoldGained = rand.Next(monster.MinGold, monster.MaxGold + 1);

                // Add XP & Gold to player
                player.Gold += result.GoldGained;
                player.XP += result.XPGained;

                // Check Level Up
                if (player.XP >= player.MaxXP)
                {
                    player.XP -= player.MaxXP;
                    player.Level++;
                    player.MaxXP = (int)(player.MaxXP * 1.35) + 50;
                    player.BaseStrength += 2;
                    player.BaseDexterity += 2;
                    player.BaseAgility += 2;
                    player.BaseConstitution += 2;
                    player.BaseCharisma += 2;
                    player.BaseIntelligence += 2;
                    player.RecalculateStats();
                    player.CurrentHP = player.MaxHP;
                }

                // Chance to drop item (35% chance)
                if (rand.NextDouble() < 0.35)
                {
                    Item drop = GenerateRandomItem(monster.Level);
                    result.Loot.Add(drop);
                    if (player.Inventory.Count < player.InventoryCapacity)
                    {
                        player.Inventory.Add(drop);
                    }
                }
            }
            else
            {
                result.IsVictory = false;
                result.WinnerName = monster.Name;
                result.XPGained = (int)(monster.XPReward * 0.15);
                result.GoldGained = 0;
                player.XP += result.XPGained;
            }

            return result;
        }

        public static CombatResult FightArena(Gladiator player, ArenaOpponent opponent)
        {
            CombatResult result = new CombatResult();
            result.CombatType = "Arena Challenge: " + opponent.Name;
            result.InitialPlayerHP = player.CurrentHP;
            result.InitialEnemyHP = opponent.MaxHP;

            int pHP = player.CurrentHP;
            int eHP = opponent.MaxHP;
            int turn = 1;

            int pDex = player.GetTotalDexterity();
            int pAgi = player.GetTotalAgility();
            int pCha = player.GetTotalCharisma();
            int pArmor = player.GetTotalArmor();

            bool hasShield = player.Equipment.ContainsKey("Shield") && player.Equipment["Shield"] != null;

            while (pHP > 0 && eHP > 0 && turn <= 25)
            {
                ExecuteTurn(turn, player.Name, opponent.Name, pDex, opponent.Agility, pCha, player.GetMinDamage(), player.GetMaxDamage(), opponent.Armor, false, ref eHP, ref pHP, true, result.Turns);
                if (eHP <= 0) break;

                ExecuteTurn(turn, opponent.Name, player.Name, opponent.Dexterity, pAgi, 8, opponent.MinDamage, opponent.MaxDamage, pArmor, hasShield, ref pHP, ref eHP, false, result.Turns);
                if (pHP <= 0) break;

                turn++;
            }

            player.CurrentHP = Math.Max(0, pHP);

            if (pHP > 0 && eHP <= 0)
            {
                result.IsVictory = true;
                result.WinnerName = player.Name;
                result.XPGained = opponent.Level * 12 + 10;
                result.GoldGained = opponent.Level * 25 + rand.Next(15, 50);

                player.Gold += result.GoldGained;
                player.XP += result.XPGained;
                player.Honor += 15;
                player.ArenaWins++;

                // Swap Arena Rank if player rank > opponent rank
                if (player.ArenaRank > opponent.Rank)
                {
                    int oldRank = player.ArenaRank;
                    player.ArenaRank = opponent.Rank;
                    opponent.Rank = oldRank;
                }
            }
            else
            {
                result.IsVictory = false;
                result.WinnerName = opponent.Name;
                result.XPGained = 5;
                result.GoldGained = 0;
                player.ArenaLosses++;
                player.Honor = Math.Max(0, player.Honor - 5);
            }

            return result;
        }

        private static void ExecuteTurn(int turnNum, string attackerName, string defenderName, int attDex, int defAgi, int attCha, int minDmg, int maxDmg, int defArmor, bool defHasShield, ref int defenderHP, ref int attackerHP, bool attIsPlayer, List<CombatTurn> turns)
        {
            double hitChance = 0.75 + ((attDex - defAgi) * 0.015);
            hitChance = Math.Max(0.20, Math.Min(0.95, hitChance));

            if (rand.NextDouble() > hitChance)
            {
                turns.Add(new CombatTurn
                {
                    TurnNumber = turnNum,
                    AttackerName = attackerName,
                    DefenderName = defenderName,
                    ActionType = "Miss",
                    Damage = 0,
                    AttackerHP = attackerHP,
                    DefenderHP = defenderHP,
                    Message = string.Format("{0} swings at {1} but misses completely!", attackerName, defenderName),
                    AttackerIsPlayer = attIsPlayer
                });
                return;
            }

            if (defHasShield && rand.NextDouble() < (defAgi * 0.008))
            {
                turns.Add(new CombatTurn
                {
                    TurnNumber = turnNum,
                    AttackerName = attackerName,
                    DefenderName = defenderName,
                    ActionType = "Block",
                    Damage = 0,
                    AttackerHP = attackerHP,
                    DefenderHP = defenderHP,
                    Message = string.Format("{0} blocks {1}'s attack with a heavy shield!", defenderName, attackerName),
                    AttackerIsPlayer = attIsPlayer
                });
                return;
            }

            int baseDmg = rand.Next(minDmg, maxDmg + 1);
            bool isCrit = rand.NextDouble() < (0.05 + attCha * 0.006);
            if (isCrit) baseDmg = (int)(baseDmg * 1.65);

            double mitigation = 100.0 / (100.0 + (defArmor * 0.45));
            int finalDmg = Math.Max(1, (int)(baseDmg * mitigation));

            defenderHP -= finalDmg;

            string msg = isCrit
                ? string.Format("{0} strikes {1} CRITICALLY for {2} damage!", attackerName, defenderName, finalDmg)
                : string.Format("{0} hits {1} for {2} damage.", attackerName, defenderName, finalDmg);

            turns.Add(new CombatTurn
            {
                TurnNumber = turnNum,
                AttackerName = attackerName,
                DefenderName = defenderName,
                ActionType = isCrit ? "Critical" : "Hit",
                Damage = finalDmg,
                AttackerHP = attackerHP,
                DefenderHP = Math.Max(0, defenderHP),
                Message = msg,
                AttackerIsPlayer = attIsPlayer
            });
        }

        public static Item GenerateRandomItem(int level)
        {
            Array types = Enum.GetValues(typeof(ItemType));
            ItemType type = (ItemType)types.GetValue(rand.Next(0, types.Length - 2)); // exclude potion/material

            ItemRarity rarity = ItemRarity.Common;
            double rRoll = rand.NextDouble();
            if (rRoll > 0.95) rarity = ItemRarity.Legendary;
            else if (rRoll > 0.85) rarity = ItemRarity.Epic;
            else if (rRoll > 0.65) rarity = ItemRarity.Rare;
            else if (rRoll > 0.35) rarity = ItemRarity.Uncommon;

            int rarityMultiplier = (int)rarity + 1;

            Item item = new Item();
            item.Type = type;
            item.Rarity = rarity;
            item.LevelRequirement = level;

            string baseName = "Roman Gear";
            if (type == ItemType.Weapon)
            {
                string[] weapons = { "Gladius", "Spatha", "Pugio Dagger", "Trident", "Halberd", "Centurion Sword" };
                baseName = weapons[rand.Next(weapons.Length)];
                item.MinDamage = level * 3 + rand.Next(1, 5) * rarityMultiplier;
                item.MaxDamage = item.MinDamage + rand.Next(3, 8) * rarityMultiplier;
                item.IconSvg = "weapon_" + rand.Next(1, 4);
            }
            else if (type == ItemType.Helmet)
            {
                string[] helms = { "Galea Helmet", "Centurion Crest", "Legionary Helm", "Gladiator Mask" };
                baseName = helms[rand.Next(helms.Length)];
                item.Armor = level * 4 + rand.Next(2, 6) * rarityMultiplier;
                item.IconSvg = "helmet_" + rand.Next(1, 3);
            }
            else if (type == ItemType.Armor)
            {
                string[] armors = { "Lorica Segmentata", "Lorica Hamata", "Gladiator Cuirass", "Bronze Breastplate" };
                baseName = armors[rand.Next(armors.Length)];
                item.Armor = level * 8 + rand.Next(5, 12) * rarityMultiplier;
                item.IconSvg = "armor_" + rand.Next(1, 3);
            }
            else if (type == ItemType.Shield)
            {
                string[] shields = { "Scutum Shield", "Parma Round Shield", "Tower Shield", "Gladiator Buckler" };
                baseName = shields[rand.Next(shields.Length)];
                item.Armor = level * 5 + rand.Next(3, 7) * rarityMultiplier;
                item.IconSvg = "shield_" + rand.Next(1, 3);
            }
            else if (type == ItemType.Ring)
            {
                baseName = "Signet Ring";
                item.Strength = rand.Next(1, 3) * rarityMultiplier;
                item.Agility = rand.Next(1, 3) * rarityMultiplier;
                item.IconSvg = "ring_1";
            }
            else if (type == ItemType.Amulet)
            {
                baseName = "Imperial Amulet";
                item.Constitution = rand.Next(1, 4) * rarityMultiplier;
                item.Charisma = rand.Next(1, 4) * rarityMultiplier;
                item.IconSvg = "amulet_1";
            }
            else if (type == ItemType.Gloves)
            {
                baseName = "Leather Gauntlets";
                item.Armor = level * 2 + rarityMultiplier;
                item.Dexterity = rand.Next(1, 3) * rarityMultiplier;
                item.IconSvg = "gloves_1";
            }
            else if (type == ItemType.Shoes)
            {
                baseName = "Caligae Sandals";
                item.Armor = level * 2 + rarityMultiplier;
                item.Agility = rand.Next(1, 3) * rarityMultiplier;
                item.IconSvg = "shoes_1";
            }

            string[] prefixes = { "", "Praetorian", "Centurion", "Imperial", "Olympian", "Invictus", "Titan" };
            string[] suffixes = { "", "of Valor", "of Jupiter", "of Mars", "of Blood", "of Victory" };

            item.Prefix = prefixes[rand.Next(prefixes.Length)];
            item.Suffix = suffixes[rand.Next(suffixes.Length)];
            item.Name = baseName;

            item.Price = (level * 25 + 20) * rarityMultiplier;
            item.SmeltIron = rand.Next(1, 4) * rarityMultiplier;
            item.SmeltBronze = rand.Next(1, 3) * rarityMultiplier;
            item.SmeltRuby = (rarity >= ItemRarity.Rare) ? rand.Next(1, 3) : 0;
            item.SmeltLeather = rand.Next(1, 4) * rarityMultiplier;

            return item;
        }

        public static Monster GetScaledMonster(Monster m, Gladiator player, ExpeditionLocation loc)
        {
            if (m == null || player == null) return m;

            int locReq = (loc != null) ? loc.ReqLevel : 1;
            int levelDelta = Math.Max(0, player.Level - locReq);

            if (levelDelta == 0) return m;

            int scaledLevel = m.Level + levelDelta;
            double scaleFactor = 1.0 + (levelDelta * 0.22);

            return new Monster
            {
                Id = m.Id,
                Name = m.Name,
                Level = scaledLevel,
                MaxHP = (int)(m.MaxHP * scaleFactor),
                MinDamage = m.MinDamage + (levelDelta * 3),
                MaxDamage = m.MaxDamage + (levelDelta * 5),
                Armor = m.Armor + (levelDelta * 3),
                Dexterity = m.Dexterity + (levelDelta * 2),
                Agility = m.Agility + (levelDelta * 2),
                XPReward = m.XPReward + (levelDelta * 12),
                MinGold = m.MinGold + (levelDelta * 10),
                MaxGold = m.MaxGold + (levelDelta * 20),
                LocationId = m.LocationId,
                IconSvg = m.IconSvg
            };
        }

        public static ArenaOpponent GetScaledArenaOpponent(Gladiator player, ArenaOpponent baseOpp)
        {
            if (baseOpp == null || player == null) return baseOpp;

            int rankOffset = 6 - baseOpp.Rank;
            int lvl = Math.Max(1, player.Level + rankOffset);

            return new ArenaOpponent
            {
                Id = baseOpp.Id,
                Rank = baseOpp.Rank,
                Name = baseOpp.Name,
                Level = lvl,
                Strength = 5 + lvl * 3,
                Dexterity = 5 + lvl * 3,
                Agility = 5 + lvl * 3,
                Constitution = 5 + lvl * 3,
                MaxHP = 100 + lvl * 35,
                MinDamage = 4 + lvl * 4,
                MaxDamage = 8 + lvl * 5,
                Armor = lvl * 5,
                IconSvg = baseOpp.IconSvg
            };
        }

        public static List<ArenaOpponent> GetScaledArenaLadder(Gladiator player, List<ArenaOpponent> baseLadder)
        {
            List<ArenaOpponent> scaledLadder = new List<ArenaOpponent>();
            if (baseLadder == null) return scaledLadder;

            foreach (var opp in baseLadder)
            {
                scaledLadder.Add(GetScaledArenaOpponent(player, opp));
            }
            return scaledLadder;
        }
    }
}
