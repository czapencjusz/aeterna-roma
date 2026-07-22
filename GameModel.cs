using System;
using System.Collections.Generic;

namespace GladiatusOffline
{
    public enum ItemRarity
    {
        Common = 0,
        Uncommon = 1,
        Rare = 2,
        Epic = 3,
        Legendary = 4
    }

    public enum ItemType
    {
        Helmet,
        Armor,
        Weapon,
        Shield,
        Ring,
        Amulet,
        Gloves,
        Shoes,
        Potion,
        Material
    }

    public class Item
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public ItemType Type { get; set; }
        public ItemRarity Rarity { get; set; }
        public int LevelRequirement { get; set; }
        public int MinDamage { get; set; }
        public int MaxDamage { get; set; }
        public int Armor { get; set; }
        public int Strength { get; set; }
        public int Dexterity { get; set; }
        public int Agility { get; set; }
        public int Constitution { get; set; }
        public int Charisma { get; set; }
        public int Intelligence { get; set; }
        public int HealAmount { get; set; }
        public int EnergyAmount { get; set; }
        public int Price { get; set; }
        public string IconSvg { get; set; }
        public string Prefix { get; set; }
        public string Suffix { get; set; }
        public int SmeltIron { get; set; }
        public int SmeltBronze { get; set; }
        public int SmeltRuby { get; set; }
        public int SmeltLeather { get; set; }

        public Item()
        {
            Id = Guid.NewGuid().ToString("N");
        }

        public string GetDisplayName()
        {
            string name = Name;
            if (!string.IsNullOrEmpty(Prefix)) name = Prefix + " " + name;
            if (!string.IsNullOrEmpty(Suffix)) name = name + " " + Suffix;
            return name;
        }
    }

    public class Gladiator
    {
        public string Name { get; set; }
        public string Title { get; set; }
        public int Level { get; set; }
        public int XP { get; set; }
        public int MaxXP { get; set; }
        public int Gold { get; set; }
        public int Rubies { get; set; }
        public int CurrentHP { get; set; }
        public int MaxHP { get; set; }
        public int CurrentEnergy { get; set; }
        public int MaxEnergy { get; set; }

        // Base attributes
        public int BaseStrength { get; set; }
        public int BaseDexterity { get; set; }
        public int BaseAgility { get; set; }
        public int BaseConstitution { get; set; }
        public int BaseCharisma { get; set; }
        public int BaseIntelligence { get; set; }

        // Equipped items by slot key: Head, Chest, Weapon, Shield, Ring, Amulet, Gloves, Shoes
        public Dictionary<string, Item> Equipment { get; set; }

        // Inventory grid
        public List<Item> Inventory { get; set; }
        public int InventoryCapacity { get; set; }

        // Arena & Stats
        public int Honor { get; set; }
        public int ArenaRank { get; set; }
        public int ArenaWins { get; set; }
        public int ArenaLosses { get; set; }

        // Avatar customizer settings
        public int HelmetStyle { get; set; }
        public int ArmorStyle { get; set; }
        public int HairStyle { get; set; }
        public string SkinColor { get; set; }

        public Gladiator()
        {
            Name = "Maximus";
            Title = "Novice Gladiator";
            Level = 1;
            XP = 0;
            MaxXP = 100;
            Gold = 250;
            Rubies = 15;
            BaseStrength = 5;
            BaseDexterity = 5;
            BaseAgility = 5;
            BaseConstitution = 5;
            BaseCharisma = 5;
            BaseIntelligence = 5;

            Equipment = new Dictionary<string, Item>();
            Inventory = new List<Item>();
            InventoryCapacity = 24;

            Honor = 100;
            ArenaRank = 20;
            ArenaWins = 0;
            ArenaLosses = 0;

            HelmetStyle = 1;
            ArmorStyle = 1;
            HairStyle = 1;
            SkinColor = "#e0ac69";

            RecalculateStats();
            CurrentHP = MaxHP;
            CurrentEnergy = MaxEnergy;
        }

        public void RecalculateStats()
        {
            MaxHP = 100 + (GetTotalConstitution() * 15) + (Level * 20);
            MaxEnergy = 20 + (Level * 2);
            if (CurrentHP > MaxHP) CurrentHP = MaxHP;
            if (CurrentEnergy > MaxEnergy) CurrentEnergy = MaxEnergy;
        }

        public int GetTotalStrength() { return BaseStrength + GetBonus("Strength"); }
        public int GetTotalDexterity() { return BaseDexterity + GetBonus("Dexterity"); }
        public int GetTotalAgility() { return BaseAgility + GetBonus("Agility"); }
        public int GetTotalConstitution() { return BaseConstitution + GetBonus("Constitution"); }
        public int GetTotalCharisma() { return BaseCharisma + GetBonus("Charisma"); }
        public int GetTotalIntelligence() { return BaseIntelligence + GetBonus("Intelligence"); }

        public int GetBonus(string stat)
        {
            int bonus = 0;
            if (Equipment == null) return 0;
            foreach (var kvp in Equipment)
            {
                if (kvp.Value == null) continue;
                if (stat == "Strength") bonus += kvp.Value.Strength;
                else if (stat == "Dexterity") bonus += kvp.Value.Dexterity;
                else if (stat == "Agility") bonus += kvp.Value.Agility;
                else if (stat == "Constitution") bonus += kvp.Value.Constitution;
                else if (stat == "Charisma") bonus += kvp.Value.Charisma;
                else if (stat == "Intelligence") bonus += kvp.Value.Intelligence;
            }
            return bonus;
        }

        public int GetTotalArmor()
        {
            int armor = 0;
            if (Equipment != null)
            {
                foreach (var kvp in Equipment)
                {
                    if (kvp.Value != null) armor += kvp.Value.Armor;
                }
            }
            return armor;
        }

        public int GetMinDamage()
        {
            int baseDmg = 3 + (GetTotalStrength() / 2);
            if (Equipment != null && Equipment.ContainsKey("Weapon") && Equipment["Weapon"] != null)
            {
                baseDmg += Equipment["Weapon"].MinDamage;
            }
            return baseDmg;
        }

        public int GetMaxDamage()
        {
            int baseDmg = 6 + (GetTotalStrength() / 2) + (GetTotalDexterity() / 3);
            if (Equipment != null && Equipment.ContainsKey("Weapon") && Equipment["Weapon"] != null)
            {
                baseDmg += Equipment["Weapon"].MaxDamage;
            }
            return baseDmg;
        }

        public int GetTrainingCost(int currentBase)
        {
            return (int)(currentBase * currentBase * 2.5) + 15;
        }
    }

    public class Vendor
    {
        public string Type { get; set; } // Weaponsmith, Armorer, General, Alchemist
        public string Name { get; set; }
        public List<Item> Items { get; set; }

        public Vendor()
        {
            Items = new List<Item>();
        }
    }

    public class Monster
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public int Level { get; set; }
        public int MaxHP { get; set; }
        public int MinDamage { get; set; }
        public int MaxDamage { get; set; }
        public int Armor { get; set; }
        public int Dexterity { get; set; }
        public int Agility { get; set; }
        public int XPReward { get; set; }
        public int MinGold { get; set; }
        public int MaxGold { get; set; }
        public int LocationId { get; set; }
        public string IconSvg { get; set; }
    }

    public class ExpeditionLocation
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public int ReqLevel { get; set; }
        public int EnergyCost { get; set; }
        public List<Monster> Monsters { get; set; }
        public string ThemeColor { get; set; }

        public ExpeditionLocation()
        {
            Monsters = new List<Monster>();
        }
    }

    public class ArenaOpponent
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public int Level { get; set; }
        public int Rank { get; set; }
        public int Strength { get; set; }
        public int Dexterity { get; set; }
        public int Agility { get; set; }
        public int Constitution { get; set; }
        public int MaxHP { get; set; }
        public int MinDamage { get; set; }
        public int MaxDamage { get; set; }
        public int Armor { get; set; }
        public string IconSvg { get; set; }
    }

    public class Mercenary
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string ClassType { get; set; } // Murmillo, Retiarius, Thraex, Secutor
        public int Level { get; set; }
        public int MaxHP { get; set; }
        public int MinDamage { get; set; }
        public int MaxDamage { get; set; }
        public int Armor { get; set; }
        public int Price { get; set; }
        public bool IsRecruited { get; set; }
    }

    public class DungeonStage
    {
        public int StageNumber { get; set; }
        public string Name { get; set; }
        public Monster BossOrMonster { get; set; }
        public bool IsBoss { get; set; }
    }

    public class Dungeon
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public int ReqLevel { get; set; }
        public List<DungeonStage> Stages { get; set; }
        public int CurrentStage { get; set; }
        public bool IsCompleted { get; set; }

        public Dungeon()
        {
            Stages = new List<DungeonStage>();
        }
    }

    public class WorkTask
    {
        public bool IsWorking { get; set; }
        public int DurationHours { get; set; }
        public DateTime StartTime { get; set; }
        public int ExpectedGold { get; set; }
        public int ExpectedXP { get; set; }
    }

    public class Guild
    {
        public bool HasGuild { get; set; }
        public string Name { get; set; }
        public string Tag { get; set; }
        public int Level { get; set; }
        public int GoldVault { get; set; }
        public int TrainingGroundLevel { get; set; }
        public int LibraryLevel { get; set; }
        public int VillaLevel { get; set; }
        public List<string> Log { get; set; }

        public Guild()
        {
            Log = new List<string>();
        }
    }

    public class ForgeRecipe
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public ItemType ResultType { get; set; }
        public ItemRarity ResultRarity { get; set; }
        public int ReqIron { get; set; }
        public int ReqBronze { get; set; }
        public int ReqRuby { get; set; }
        public int ReqLeather { get; set; }
        public int ReqLevel { get; set; }
        public string IconSvg { get; set; }
    }

    public class UserSettings
    {
        public bool Fullscreen { get; set; }
        public int MasterVolume { get; set; }
        public int SFXVolume { get; set; }
        public int MusicVolume { get; set; }
        public string CombatSpeed { get; set; }
        public bool HighGlowEffects { get; set; }
        public string ThemeMode { get; set; }

        public UserSettings()
        {
            Fullscreen = false;
            MasterVolume = 80;
            SFXVolume = 80;
            MusicVolume = 50;
            CombatSpeed = "Normal";
            HighGlowEffects = true;
            ThemeMode = "DarkImperial";
        }
    }

    public class GameState
    {
        public Gladiator Player { get; set; }
        public Dictionary<string, Vendor> Vendors { get; set; }
        public List<ExpeditionLocation> Locations { get; set; }
        public List<ArenaOpponent> ArenaLadder { get; set; }
        public List<Mercenary> MercenarySquad { get; set; }
        public List<Dungeon> Dungeons { get; set; }
        public WorkTask ActiveWork { get; set; }
        public Guild PlayerGuild { get; set; }
        public int IronStash { get; set; }
        public int BronzeStash { get; set; }
        public int RubyStash { get; set; }
        public int LeatherStash { get; set; }
        public List<ForgeRecipe> Recipes { get; set; }
        public DateTime LastEnergyRegen { get; set; }
        public UserSettings Settings { get; set; }

        public GameState()
        {
            Vendors = new Dictionary<string, Vendor>();
            Locations = new List<ExpeditionLocation>();
            ArenaLadder = new List<ArenaOpponent>();
            MercenarySquad = new List<Mercenary>();
            Dungeons = new List<Dungeon>();
            ActiveWork = new WorkTask();
            PlayerGuild = new Guild();
            Recipes = new List<ForgeRecipe>();
            LastEnergyRegen = DateTime.Now;
            Settings = new UserSettings();
        }
    }
}
