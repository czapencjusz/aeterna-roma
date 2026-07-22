using System;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using System.Collections.Generic;

namespace GladiatusOffline
{
    public class Server
    {
        private HttpListener listener;
        private GameState state;
        private JavaScriptSerializer serializer;
        private bool isRunning;

        public int BoundPort { get; private set; }
        public string BoundUrl { get; private set; }
        public ManualResetEvent ServerStartedEvent { get; private set; }

        public Server(int initialPort = 8080)
        {
            BoundPort = initialPort;
            ServerStartedEvent = new ManualResetEvent(false);
            state = SaveManager.LoadOrCreate();
            serializer = new JavaScriptSerializer();
        }

        public void Start()
        {
            int startPort = 8080;
            bool bound = false;

            for (int p = startPort; p < startPort + 50; p++)
            {
                try
                {
                    listener = new HttpListener();
                    listener.Prefixes.Add(string.Format("http://127.0.0.1:{0}/", p));
                    listener.Prefixes.Add(string.Format("http://localhost:{0}/", p));
                    listener.Start();
                    BoundPort = p;
                    BoundUrl = string.Format("http://127.0.0.1:{0}/", p);
                    bound = true;
                    break;
                }
                catch
                {
                    try { if (listener != null) listener.Close(); } catch { }
                }
            }

            if (bound)
            {
                isRunning = true;
                ServerStartedEvent.Set();
                // Server is running silently (no console in winexe mode)
                Listen();
            }
            else
            {
                // Could not bind to any port - server failed to start
            }
        }

        private void Listen()
        {
            while (isRunning)
            {
                try
                {
                    HttpListenerContext context = listener.GetContext();
                    ProcessRequest(context);
                }
                catch (Exception ex)
                {
                    if (!isRunning) break;
                    // Listener exception occurred - continue silently
                }
            }
        }

        private void ProcessRequest(HttpListenerContext context)
        {
            HttpListenerRequest req = context.Request;
            HttpListenerResponse res = context.Response;

            res.Headers.Add("Access-Control-Allow-Origin", "*");
            res.Headers.Add("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
            res.Headers.Add("Access-Control-Allow-Headers", "Content-Type");

            if (req.HttpMethod == "OPTIONS")
            {
                res.StatusCode = 200;
                res.Close();
                return;
            }

            string rawUrl = req.Url.AbsolutePath;

            if (rawUrl == "/" || rawUrl == "/index.html")
            {
                byte[] buffer = Encoding.UTF8.GetBytes(WebAssets.IndexHtml);
                res.ContentType = "text/html; charset=utf-8";
                res.ContentLength64 = buffer.Length;
                res.OutputStream.Write(buffer, 0, buffer.Length);
                res.Close();
                return;
            }

            if (rawUrl.StartsWith("/api/"))
            {
                string jsonBody = "";
                if (req.HasEntityBody)
                {
                    using (StreamReader reader = new StreamReader(req.InputStream, req.ContentEncoding))
                    {
                        jsonBody = reader.ReadToEnd();
                    }
                }

                object responseObj = HandleApiCall(rawUrl, jsonBody);
                string jsonResp = serializer.Serialize(responseObj);
                byte[] buffer = Encoding.UTF8.GetBytes(jsonResp);
                res.ContentType = "application/json; charset=utf-8";
                res.ContentLength64 = buffer.Length;
                res.OutputStream.Write(buffer, 0, buffer.Length);
                res.Close();
                return;
            }

            res.StatusCode = 404;
            res.Close();
        }

        private object HandleApiCall(string path, string jsonBody)
        {
            Dictionary<string, object> args = new Dictionary<string, object>();
            if (!string.IsNullOrEmpty(jsonBody))
            {
                try
                {
                    args = serializer.Deserialize<Dictionary<string, object>>(jsonBody);
                }
                catch { }
            }

            switch (path)
            {
                case "/api/state":
                    state.ArenaLadder = CombatEngine.GetScaledArenaLadder(state.Player, state.ArenaLadder);
                    return state;

                case "/api/train":
                    if (args.ContainsKey("attribute"))
                    {
                        string attr = args["attribute"].ToString();
                        TrainAttribute(attr);
                    }
                    state.ArenaLadder = CombatEngine.GetScaledArenaLadder(state.Player, state.ArenaLadder);
                    SaveManager.Save(state);
                    return state;

                case "/api/expedition":
                    int locId = Convert.ToInt32(args["locationId"]);
                    string monsterId = args["monsterId"].ToString();
                    CombatResult expResult = RunExpedition(locId, monsterId);
                    state.ArenaLadder = CombatEngine.GetScaledArenaLadder(state.Player, state.ArenaLadder);
                    SaveManager.Save(state);
                    return new { state = state, result = expResult };

                case "/api/arena":
                    string oppId = args["opponentId"].ToString();
                    CombatResult arenaResult = RunArena(oppId);
                    state.ArenaLadder = CombatEngine.GetScaledArenaLadder(state.Player, state.ArenaLadder);
                    SaveManager.Save(state);
                    return new { state = state, result = arenaResult };

                case "/api/dungeon":
                    int dungId = Convert.ToInt32(args["dungeonId"]);
                    CombatResult dungResult = RunDungeon(dungId);
                    SaveManager.Save(state);
                    return new { state = state, result = dungResult };

                case "/api/buy":
                    string vendorType = args["vendorType"].ToString();
                    int buyIdx = Convert.ToInt32(args["itemIndex"]);
                    BuyVendorItem(vendorType, buyIdx);
                    SaveManager.Save(state);
                    return state;

                case "/api/sell":
                    int sellIdx = Convert.ToInt32(args["inventoryIndex"]);
                    SellInventoryItem(sellIdx);
                    SaveManager.Save(state);
                    return state;

                case "/api/equip":
                    int eqIdx = Convert.ToInt32(args["inventoryIndex"]);
                    EquipItem(eqIdx);
                    SaveManager.Save(state);
                    return state;

                case "/api/unequip":
                    string slot = args["slot"].ToString();
                    UnequipSlot(slot);
                    SaveManager.Save(state);
                    return state;

                case "/api/forge/smelt":
                    int smeltIdx = Convert.ToInt32(args["inventoryIndex"]);
                    SmeltItem(smeltIdx);
                    SaveManager.Save(state);
                    return state;

                case "/api/forge/craft":
                    string recipeId = args["recipeId"].ToString();
                    CraftRecipe(recipeId);
                    SaveManager.Save(state);
                    return state;

                case "/api/work/start":
                    int hours = Convert.ToInt32(args["hours"]);
                    DoWork(hours);
                    SaveManager.Save(state);
                    return state;

                case "/api/guild/create":
                    string name = args["name"].ToString();
                    string tag = args["tag"].ToString();
                    CreateGuild(name, tag);
                    SaveManager.Save(state);
                    return state;

                case "/api/save":
                    SaveManager.Save(state);
                    return new { success = true };

                case "/api/settings/fullscreen":
                    if (state.Settings == null) state.Settings = new UserSettings();
                    state.Settings.Fullscreen = !state.Settings.Fullscreen;
                    if (Program.ToggleFullscreenAction != null)
                    {
                        Program.ToggleFullscreenAction();
                    }
                    SaveManager.Save(state);
                    return state;

                case "/api/settings/update":
                    if (state.Settings == null) state.Settings = new UserSettings();
                    if (args.ContainsKey("masterVolume")) state.Settings.MasterVolume = Convert.ToInt32(args["masterVolume"]);
                    if (args.ContainsKey("sfxVolume")) state.Settings.SFXVolume = Convert.ToInt32(args["sfxVolume"]);
                    if (args.ContainsKey("musicVolume")) state.Settings.MusicVolume = Convert.ToInt32(args["musicVolume"]);
                    if (args.ContainsKey("combatSpeed")) state.Settings.CombatSpeed = args["combatSpeed"].ToString();
                    if (args.ContainsKey("highGlowEffects")) state.Settings.HighGlowEffects = Convert.ToBoolean(args["highGlowEffects"]);
                    if (args.ContainsKey("themeMode")) state.Settings.ThemeMode = args["themeMode"].ToString();
                    SaveManager.Save(state);
                    return state;

                case "/api/settings/import":
                    if (args.ContainsKey("json"))
                    {
                        string importJson = args["json"].ToString();
                        GameState imported = serializer.Deserialize<GameState>(importJson);
                        if (imported != null && imported.Player != null)
                        {
                            SaveManager.EnsureDefaultData(imported);
                            state = imported;
                            SaveManager.Save(state);
                        }
                    }
                    return state;

                case "/api/reset":
                    SaveManager.ResetSave();
                    state = SaveManager.CreateInitialGameState();
                    return state;

                default:
                    return state;
            }
        }

        private void TrainAttribute(string attr)
        {
            Gladiator p = state.Player;
            int currentBase = 5;
            if (attr == "Strength") currentBase = p.BaseStrength;
            else if (attr == "Dexterity") currentBase = p.BaseDexterity;
            else if (attr == "Agility") currentBase = p.BaseAgility;
            else if (attr == "Constitution") currentBase = p.BaseConstitution;
            else if (attr == "Charisma") currentBase = p.BaseCharisma;
            else if (attr == "Intelligence") currentBase = p.BaseIntelligence;

            int cost = p.GetTrainingCost(currentBase);
            if (p.Gold >= cost)
            {
                p.Gold -= cost;
                if (attr == "Strength") p.BaseStrength++;
                else if (attr == "Dexterity") p.BaseDexterity++;
                else if (attr == "Agility") p.BaseAgility++;
                else if (attr == "Constitution") p.BaseConstitution++;
                else if (attr == "Charisma") p.BaseCharisma++;
                else if (attr == "Intelligence") p.BaseIntelligence++;
                p.RecalculateStats();
            }
        }

        private CombatResult RunExpedition(int locId, string monsterId)
        {
            Gladiator p = state.Player;
            ExpeditionLocation loc = state.Locations.Find(l => l.Id == locId);
            if (loc == null || p.CurrentEnergy < loc.EnergyCost)
            {
                return new CombatResult { IsVictory = false, WinnerName = "No Energy" };
            }

            Monster baseM = loc.Monsters.Find(mon => mon.Id == monsterId);
            if (baseM == null) return new CombatResult { IsVictory = false, WinnerName = "Monster Not Found" };

            Monster scaledM = CombatEngine.GetScaledMonster(baseM, p, loc);

            p.CurrentEnergy -= loc.EnergyCost;
            return CombatEngine.FightMonster(p, scaledM);
        }

        private CombatResult RunArena(string oppId)
        {
            Gladiator p = state.Player;
            ArenaOpponent baseOpp = state.ArenaLadder.Find(a => a.Id == oppId);
            if (baseOpp == null) return new CombatResult { IsVictory = false, WinnerName = "Opponent Not Found" };

            ArenaOpponent scaledOpp = CombatEngine.GetScaledArenaOpponent(p, baseOpp);

            return CombatEngine.FightArena(p, scaledOpp);
        }

        private CombatResult RunDungeon(int dungId)
        {
            Gladiator p = state.Player;
            Dungeon d = state.Dungeons.Find(dung => dung.Id == dungId);
            if (d == null || d.IsCompleted) return new CombatResult { IsVictory = false, WinnerName = "Dungeon Finished" };

            DungeonStage stage = d.Stages.Find(s => s.StageNumber == d.CurrentStage);
            if (stage == null) return new CombatResult { IsVictory = false, WinnerName = "No Stage" };

            CombatResult res = CombatEngine.FightMonster(p, stage.BossOrMonster);
            if (res.IsVictory)
            {
                if (d.CurrentStage < d.Stages.Count)
                {
                    d.CurrentStage++;
                }
                else
                {
                    d.IsCompleted = true;
                }
            }
            return res;
        }

        private void EquipItem(int invIdx)
        {
            Gladiator p = state.Player;
            if (invIdx < 0 || invIdx >= p.Inventory.Count) return;

            Item item = p.Inventory[invIdx];
            string slot = item.Type.ToString();
            if (slot == "Helmet") slot = "Head";
            if (slot == "Armor") slot = "Chest";

            p.Inventory.RemoveAt(invIdx);

            if (p.Equipment.ContainsKey(slot) && p.Equipment[slot] != null)
            {
                p.Inventory.Add(p.Equipment[slot]);
            }

            p.Equipment[slot] = item;
            p.RecalculateStats();
        }

        private void UnequipSlot(string slot)
        {
            Gladiator p = state.Player;
            if (p.Equipment.ContainsKey(slot) && p.Equipment[slot] != null)
            {
                if (p.Inventory.Count < p.InventoryCapacity)
                {
                    p.Inventory.Add(p.Equipment[slot]);
                    p.Equipment[slot] = null;
                    p.RecalculateStats();
                }
            }
        }

        private void SmeltItem(int invIdx)
        {
            Gladiator p = state.Player;
            if (invIdx < 0 || invIdx >= p.Inventory.Count) return;

            Item item = p.Inventory[invIdx];
            state.IronStash += item.SmeltIron;
            state.BronzeStash += item.SmeltBronze;
            state.RubyStash += item.SmeltRuby;
            state.LeatherStash += item.SmeltLeather;

            p.Inventory.RemoveAt(invIdx);
        }

        private void CraftRecipe(string recipeId)
        {
            ForgeRecipe r = state.Recipes.Find(rec => rec.Id == recipeId);
            if (r == null) return;

            if (state.IronStash >= r.ReqIron && state.BronzeStash >= r.ReqBronze && state.RubyStash >= r.ReqRuby && state.LeatherStash >= r.ReqLeather)
            {
                state.IronStash -= r.ReqIron;
                state.BronzeStash -= r.ReqBronze;
                state.RubyStash -= r.ReqRuby;
                state.LeatherStash -= r.ReqLeather;

                Item newItem = CombatEngine.GenerateRandomItem(state.Player.Level);
                newItem.Name = r.Name;
                newItem.Type = r.ResultType;
                newItem.Rarity = r.ResultRarity;
                newItem.IconSvg = r.IconSvg;

                if (state.Player.Inventory.Count < state.Player.InventoryCapacity)
                {
                    state.Player.Inventory.Add(newItem);
                }
            }
        }

        private void DoWork(int hours)
        {
            Gladiator p = state.Player;
            int goldGain = hours * 110;
            int xpGain = hours * 25;
            p.Gold += goldGain;
            p.XP += xpGain;
        }

        private void CreateGuild(string name, string tag)
        {
            Gladiator p = state.Player;
            if (p.Gold >= 500 && !state.PlayerGuild.HasGuild)
            {
                p.Gold -= 500;
                state.PlayerGuild.HasGuild = true;
                state.PlayerGuild.Name = name;
                state.PlayerGuild.Tag = tag;
                state.PlayerGuild.Level = 1;
                state.PlayerGuild.TrainingGroundLevel = 1;
                state.PlayerGuild.Log.Add(string.Format("Guild founded by {0}.", p.Name));
            }
        }

        private void BuyVendorItem(string vendorType, int itemIndex)
        {
            if (state.Vendors.ContainsKey(vendorType))
            {
                Vendor vendor = state.Vendors[vendorType];
                if (itemIndex >= 0 && itemIndex < vendor.Items.Count)
                {
                    Item item = vendor.Items[itemIndex];
                    if (state.Player.Gold >= item.Price && state.Player.Inventory.Count < state.Player.InventoryCapacity)
                    {
                        state.Player.Gold -= item.Price;
                        vendor.Items.RemoveAt(itemIndex);
                        state.Player.Inventory.Add(item);
                        // Replenish vendor with a new random item matching player level
                        vendor.Items.Add(CombatEngine.GenerateRandomItem(state.Player.Level));
                    }
                }
            }
        }

        private void SellInventoryItem(int inventoryIndex)
        {
            if (inventoryIndex >= 0 && inventoryIndex < state.Player.Inventory.Count)
            {
                Item item = state.Player.Inventory[inventoryIndex];
                state.Player.Gold += item.Price;
                state.Player.Inventory.RemoveAt(inventoryIndex);
            }
        }
    }
}
