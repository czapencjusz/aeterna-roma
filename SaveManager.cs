using System;
using System.IO;
using System.Web.Script.Serialization;
using System.Collections.Generic;

namespace GladiatusOffline
{
    public static class SaveManager
    {
        private static string saveFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "savegame.json");

        public static GameState LoadOrCreate()
        {
            try
            {
                if (File.Exists(saveFilePath))
                {
                    string json = File.ReadAllText(saveFilePath);
                    JavaScriptSerializer serializer = new JavaScriptSerializer();
                    GameState state = serializer.Deserialize<GameState>(json);
                    if (state != null && state.Player != null)
                    {
                        EnsureDefaultData(state);
                        return state;
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Save file load error: " + ex.Message);
            }

            return CreateInitialGameState();
        }

        public static void Save(GameState state)
        {
            try
            {
                JavaScriptSerializer serializer = new JavaScriptSerializer();
                string json = serializer.Serialize(state);
                File.WriteAllText(saveFilePath, json);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Save file error: " + ex.Message);
            }
        }

        public static void ResetSave()
        {
            if (File.Exists(saveFilePath))
            {
                File.Delete(saveFilePath);
            }
        }

        public static GameState CreateInitialGameState()
        {
            GameState state = new GameState();
            state.Player = new Gladiator();
            state.IronStash = 10;
            state.BronzeStash = 10;
            state.RubyStash = 5;
            state.LeatherStash = 10;

            // Starter Equipment
            Item sword = CombatEngine.GenerateRandomItem(1);
            sword.Type = ItemType.Weapon;
            sword.Name = "Iron Gladius";
            sword.Prefix = "";
            sword.Suffix = "";
            sword.MinDamage = 4;
            sword.MaxDamage = 8;
            sword.IconSvg = "weapon_1";
            state.Player.Equipment["Weapon"] = sword;

            Item armor = CombatEngine.GenerateRandomItem(1);
            armor.Type = ItemType.Armor;
            armor.Name = "Tunic of Rome";
            armor.Prefix = "";
            armor.Suffix = "";
            armor.Armor = 10;
            armor.IconSvg = "armor_1";
            state.Player.Equipment["Chest"] = armor;

            // Add some starter potions
            Item healthPot = new Item
            {
                Name = "Health Potion",
                Type = ItemType.Potion,
                Rarity = ItemRarity.Common,
                HealAmount = 50,
                Price = 20,
                IconSvg = "potion_red"
            };
            state.Player.Inventory.Add(healthPot);

            EnsureDefaultData(state);
            Save(state);
            return state;
        }

        public static void EnsureDefaultData(GameState state)
        {
            if (state.Settings == null)
            {
                state.Settings = new UserSettings();
            }

            // Populate Vendors
            if (!state.Vendors.ContainsKey("Weaponsmith"))
            {
                Vendor v = new Vendor { Type = "Weaponsmith", Name = "Marcus the Blacksmith" };
                for (int i = 0; i < 6; i++) v.Items.Add(CombatEngine.GenerateRandomItem(state.Player.Level));
                state.Vendors["Weaponsmith"] = v;
            }

            if (!state.Vendors.ContainsKey("Armorer"))
            {
                Vendor v = new Vendor { Type = "Armorer", Name = "Flavius Armorsmith" };
                for (int i = 0; i < 6; i++) v.Items.Add(CombatEngine.GenerateRandomItem(state.Player.Level));
                state.Vendors["Armorer"] = v;
            }

            if (!state.Vendors.ContainsKey("General"))
            {
                Vendor v = new Vendor { Type = "General", Name = "Gaius Goods Trader" };
                for (int i = 0; i < 6; i++) v.Items.Add(CombatEngine.GenerateRandomItem(state.Player.Level));
                state.Vendors["General"] = v;
            }

            if (!state.Vendors.ContainsKey("Alchemist"))
            {
                Vendor v = new Vendor { Type = "Alchemist", Name = "Cornelia the Apothecary" };
                v.Items.Add(new Item { Name = "Small Health Potion", Type = ItemType.Potion, HealAmount = 40, Price = 15, IconSvg = "potion_red" });
                v.Items.Add(new Item { Name = "Large Health Potion", Type = ItemType.Potion, HealAmount = 100, Price = 35, IconSvg = "potion_red" });
                v.Items.Add(new Item { Name = "Stamina Elixir", Type = ItemType.Potion, EnergyAmount = 10, Price = 50, IconSvg = "potion_blue" });
                state.Vendors["Alchemist"] = v;
            }

            // Populate Expedition Locations
            if (state.Locations == null || state.Locations.Count == 0)
            {
                state.Locations = new List<ExpeditionLocation>
                {
                    new ExpeditionLocation
                    {
                        Id = 1,
                        Name = "Suburbs of Rome",
                        Description = "Outskirts of the Eternal City, overrun by rabid wolves, runaway slaves, and mountain bandits.",
                        ReqLevel = 1,
                        EnergyCost = 1,
                        ThemeColor = "#8C6D46",
                        Monsters = new List<Monster>
                        {
                            new Monster { Id = "m1", Name = "Wild Boar", Level = 1, MaxHP = 45, MinDamage = 3, MaxDamage = 7, Armor = 2, Dexterity = 4, Agility = 4, XPReward = 15, MinGold = 10, MaxGold = 25, IconSvg = "monster_boar" },
                            new Monster { Id = "m2", Name = "Stray Hound", Level = 1, MaxHP = 35, MinDamage = 2, MaxDamage = 6, Armor = 1, Dexterity = 6, Agility = 6, XPReward = 12, MinGold = 8, MaxGold = 20, IconSvg = "monster_wolf" },
                            new Monster { Id = "m3", Name = "Highway Bandit", Level = 2, MaxHP = 65, MinDamage = 5, MaxDamage = 11, Armor = 4, Dexterity = 8, Agility = 6, XPReward = 25, MinGold = 20, MaxGold = 45, IconSvg = "monster_bandit" }
                        }
                    },
                    new ExpeditionLocation
                    {
                        Id = 2,
                        Name = "Mist Mountains",
                        Description = "Treacherous jagged peaks guarded by fierce Harpies, Stone Trolls, and Shadow Lynx.",
                        ReqLevel = 3,
                        EnergyCost = 2,
                        ThemeColor = "#52677A",
                        Monsters = new List<Monster>
                        {
                            new Monster { Id = "m4", Name = "Mountain Lynx", Level = 3, MaxHP = 90, MinDamage = 8, MaxDamage = 14, Armor = 6, Dexterity = 12, Agility = 14, XPReward = 40, MinGold = 35, MaxGold = 70, IconSvg = "monster_cat" },
                            new Monster { Id = "m5", Name = "Screeching Harpy", Level = 4, MaxHP = 110, MinDamage = 10, MaxDamage = 18, Armor = 8, Dexterity = 15, Agility = 16, XPReward = 55, MinGold = 50, MaxGold = 90, IconSvg = "monster_harpy" },
                            new Monster { Id = "m6", Name = "Mountain Troll", Level = 5, MaxHP = 160, MinDamage = 14, MaxDamage = 24, Armor = 15, Dexterity = 8, Agility = 5, XPReward = 75, MinGold = 70, MaxGold = 130, IconSvg = "monster_troll" }
                        }
                    },
                    new ExpeditionLocation
                    {
                        Id = 3,
                        Name = "Ancient Forest",
                        Description = "Deep mystical woods harboring rogue Centaurs, Werewolves, and Ancient Treants.",
                        ReqLevel = 6,
                        EnergyCost = 2,
                        ThemeColor = "#395C37",
                        Monsters = new List<Monster>
                        {
                            new Monster { Id = "m7", Name = "Centaur Scout", Level = 6, MaxHP = 190, MinDamage = 16, MaxDamage = 26, Armor = 12, Dexterity = 18, Agility = 18, XPReward = 100, MinGold = 90, MaxGold = 160, IconSvg = "monster_centaur" },
                            new Monster { Id = "m8", Name = "Timber Werewolf", Level = 7, MaxHP = 230, MinDamage = 20, MaxDamage = 32, Armor = 14, Dexterity = 22, Agility = 20, XPReward = 130, MinGold = 120, MaxGold = 210, IconSvg = "monster_werewolf" },
                            new Monster { Id = "m9", Name = "Corrupted Treant", Level = 8, MaxHP = 300, MinDamage = 24, MaxDamage = 38, Armor = 22, Dexterity = 10, Agility = 8, XPReward = 170, MinGold = 150, MaxGold = 280, IconSvg = "monster_treant" }
                        }
                    },
                    new ExpeditionLocation
                    {
                        Id = 4,
                        Name = "Barbarian Camp",
                        Description = "Fierce hostile war camp of Northern Barbarian Warriors and Chieftains.",
                        ReqLevel = 9,
                        EnergyCost = 3,
                        ThemeColor = "#7A2E2E",
                        Monsters = new List<Monster>
                        {
                            new Monster { Id = "m10", Name = "Barbarian Berserker", Level = 9, MaxHP = 360, MinDamage = 28, MaxDamage = 45, Armor = 18, Dexterity = 24, Agility = 22, XPReward = 220, MinGold = 200, MaxGold = 350, IconSvg = "monster_barbarian" },
                            new Monster { Id = "m11", Name = "Warlord Chieftain", Level = 10, MaxHP = 480, MinDamage = 35, MaxDamage = 58, Armor = 25, Dexterity = 28, Agility = 24, XPReward = 300, MinGold = 300, MaxGold = 500, IconSvg = "monster_chieftain" }
                        }
                    }
                };
            }

            // Populate Arena Ladder Opponents
            if (state.ArenaLadder == null || state.ArenaLadder.Count == 0)
            {
                state.ArenaLadder = new List<ArenaOpponent>();
                string[] names = {
                    "Tiberius", "Cassius", "Brutus", "Varro", "Flavius",
                    "Septimius", "Valerius", "Hadrian", "Claudius", "Lucius",
                    "Aurelius", "Commodus", "Cornelius", "Severus", "Domitian",
                    "Titus", "Vespian", "Trajan", "Marcus Antonius", "Spartacus"
                };

                for (int rank = 1; rank <= 20; rank++)
                {
                    int lvl = 21 - rank;
                    state.ArenaLadder.Add(new ArenaOpponent
                    {
                        Id = "arena_" + rank,
                        Rank = rank,
                        Name = names[rank - 1],
                        Level = lvl,
                        Strength = 5 + lvl * 2,
                        Dexterity = 5 + lvl * 2,
                        Agility = 5 + lvl * 2,
                        Constitution = 5 + lvl * 2,
                        MaxHP = 80 + lvl * 25,
                        MinDamage = 4 + lvl * 3,
                        MaxDamage = 8 + lvl * 4,
                        Armor = lvl * 5,
                        IconSvg = "gladiator_" + (rank % 4 + 1)
                    });
                }
            }

            // Populate Dungeons
            if (state.Dungeons == null || state.Dungeons.Count == 0)
            {
                state.Dungeons = new List<Dungeon>
                {
                    new Dungeon
                    {
                        Id = 1,
                        Name = "Catacombs of Rome",
                        Description = "Underground ancient tombs occupied by Undead Centurions and the Necromancer Master.",
                        ReqLevel = 4,
                        CurrentStage = 1,
                        IsCompleted = false,
                        Stages = new List<DungeonStage>
                        {
                            new DungeonStage { StageNumber = 1, Name = "Catacomb Guard", IsBoss = false, BossOrMonster = new Monster { Id = "d1_1", Name = "Skeleton Legionary", Level = 4, MaxHP = 120, MinDamage = 10, MaxDamage = 16, Armor = 8, Dexterity = 12, Agility = 10, XPReward = 60, MinGold = 50, MaxGold = 90, IconSvg = "monster_skeleton" } },
                            new DungeonStage { StageNumber = 2, Name = "Crypt Tomb", IsBoss = false, BossOrMonster = new Monster { Id = "d1_2", Name = "Crypt Wight", Level = 5, MaxHP = 170, MinDamage = 14, MaxDamage = 22, Armor = 12, Dexterity = 15, Agility = 12, XPReward = 90, MinGold = 80, MaxGold = 130, IconSvg = "monster_wight" } },
                            new DungeonStage { StageNumber = 3, Name = "Necromancer Chamber", IsBoss = true, BossOrMonster = new Monster { Id = "d1_3", Name = "Lich Lord Cassius", Level = 6, MaxHP = 280, MinDamage = 20, MaxDamage = 32, Armor = 18, Dexterity = 20, Agility = 18, XPReward = 200, MinGold = 250, MaxGold = 450, IconSvg = "monster_lich" } }
                        }
                    },
                    new Dungeon
                    {
                        Id = 2,
                        Name = "Labyrinth of the Minotaur",
                        Description = "Winding maze of stone corridors guarded by mythical beasts and the monstrous Minotaur.",
                        ReqLevel = 8,
                        CurrentStage = 1,
                        IsCompleted = false,
                        Stages = new List<DungeonStage>
                        {
                            new DungeonStage { StageNumber = 1, Name = "Maze Entrance", IsBoss = false, BossOrMonster = new Monster { Id = "d2_1", Name = "Gorgon Sentinel", Level = 8, MaxHP = 260, MinDamage = 22, MaxDamage = 36, Armor = 16, Dexterity = 22, Agility = 20, XPReward = 160, MinGold = 150, MaxGold = 250, IconSvg = "monster_gorgon" } },
                            new DungeonStage { StageNumber = 2, Name = "Labyrinth Center", IsBoss = true, BossOrMonster = new Monster { Id = "d2_2", Name = "Minotaur Emperor", Level = 10, MaxHP = 500, MinDamage = 38, MaxDamage = 60, Armor = 28, Dexterity = 25, Agility = 22, XPReward = 400, MinGold = 500, MaxGold = 900, IconSvg = "monster_minotaur" } }
                        }
                    }
                };
            }

            // Populate Recipes
            if (state.Recipes == null || state.Recipes.Count == 0)
            {
                state.Recipes = new List<ForgeRecipe>
                {
                    new ForgeRecipe { Id = "r1", Name = "Centurion Gladius", ResultType = ItemType.Weapon, ResultRarity = ItemRarity.Uncommon, ReqIron = 5, ReqBronze = 2, ReqRuby = 0, ReqLeather = 2, ReqLevel = 2, IconSvg = "weapon_1" },
                    new ForgeRecipe { Id = "r2", Name = "Imperial Lorica Segmentata", ResultType = ItemType.Armor, ResultRarity = ItemRarity.Rare, ReqIron = 8, ReqBronze = 5, ReqRuby = 1, ReqLeather = 5, ReqLevel = 4, IconSvg = "armor_1" },
                    new ForgeRecipe { Id = "r3", Name = "Scutum of Mars", ResultType = ItemType.Shield, ResultRarity = ItemRarity.Epic, ReqIron = 10, ReqBronze = 8, ReqRuby = 3, ReqLeather = 4, ReqLevel = 6, IconSvg = "shield_1" },
                    new ForgeRecipe { Id = "r4", Name = "Golden Galea Helmet", ResultType = ItemType.Helmet, ResultRarity = ItemRarity.Legendary, ReqIron = 15, ReqBronze = 12, ReqRuby = 5, ReqLeather = 8, ReqLevel = 8, IconSvg = "helmet_1" }
                };
            }

            // Populate Mercenary Squad
            if (state.MercenarySquad == null || state.MercenarySquad.Count == 0)
            {
                state.MercenarySquad = new List<Mercenary>
                {
                    new Mercenary { Id = "merc_1", Name = "Valerius", ClassType = "Murmillo", Level = 2, MaxHP = 120, MinDamage = 6, MaxDamage = 10, Armor = 12, Price = 300, IsRecruited = false },
                    new Mercenary { Id = "merc_2", Name = "Drusus", ClassType = "Retiarius", Level = 4, MaxHP = 160, MinDamage = 12, MaxDamage = 18, Armor = 8, Price = 600, IsRecruited = false },
                    new Mercenary { Id = "merc_3", Name = "Felix", ClassType = "Thraex", Level = 6, MaxHP = 220, MinDamage = 18, MaxDamage = 26, Armor = 18, Price = 1200, IsRecruited = false }
                };
            }
        }
    }
}
