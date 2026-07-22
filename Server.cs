using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;

namespace GladiatusOffline
{
    public class Server
    {
        private HttpListener listener;
        private int port;
        private GameState state;
        private JavaScriptSerializer jsonSerializer;
        public EventWaitHandle ServerStartedEvent = new ManualResetEvent(false);
        public string BoundUrl { get; private set; }

        public Server(int port = 8080)
        {
            this.port = port;
            this.jsonSerializer = new JavaScriptSerializer();
            this.state = SaveManager.LoadOrCreate();
            // Initialize dynamic scaling if missing
            state.ArenaLadder = CombatEngine.GetScaledArenaLadder(state.Player, state.ArenaLadder);
        }

        public void Start()
        {
            try
            {
                listener = new HttpListener();
                string prefix = string.Format("http://127.0.0.1:{0}/", port);
                listener.Prefixes.Add(prefix);
                listener.Start();
                BoundUrl = prefix;
                ServerStartedEvent.Set();
                Console.WriteLine("Server listening at {0}", prefix);

                while (listener.IsListening)
                {
                    try
                    {
                        HttpListenerContext ctx = listener.GetContext();
                        ThreadPool.QueueUserWorkItem((_) => ProcessRequest(ctx));
                    }
                    catch (HttpListenerException) { break; }
                    catch (Exception ex) { Console.WriteLine("Listener context exception: {0}", ex.Message); }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to bind port {0}: {1}", port, ex.Message);
                // Fallback port
                try
                {
                    port = 8085;
                    listener = new HttpListener();
                    string prefix = string.Format("http://127.0.0.1:{0}/", port);
                    listener.Prefixes.Add(prefix);
                    listener.Start();
                    BoundUrl = prefix;
                    ServerStartedEvent.Set();

                    while (listener.IsListening)
                    {
                        try
                        {
                            HttpListenerContext ctx = listener.GetContext();
                            ThreadPool.QueueUserWorkItem((_) => ProcessRequest(ctx));
                        }
                        catch (HttpListenerException) { break; }
                        catch (Exception ex) { Console.WriteLine("Listener context exception: {0}", ex.Message); }
                    }
                }
                catch (Exception e2)
                {
                    Console.WriteLine("Fallback port failed: {0}", e2.Message);
                    ServerStartedEvent.Set();
                }
            }
        }

        public void Stop()
        {
            if (listener != null && listener.IsListening)
            {
                listener.Stop();
                listener.Close();
            }
        }

        private void ProcessRequest(HttpListenerContext ctx)
        {
            HttpListenerRequest req = ctx.Request;
            HttpListenerResponse resp = ctx.Response;

            resp.Headers.Add("Access-Control-Allow-Origin", "*");
            resp.Headers.Add("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
            resp.Headers.Add("Access-Control-Allow-Headers", "Content-Type");

            if (req.HttpMethod == "OPTIONS")
            {
                resp.StatusCode = 200;
                resp.Close();
                return;
            }

            try
            {
                RegenerateStats();

                string path = req.Url.AbsolutePath;

                if (path == "/" || path == "/index.html")
                {
                    byte[] htmlBytes = Encoding.UTF8.GetBytes(WebAssets.IndexHtml);
                    resp.ContentType = "text/html; charset=utf-8";
                    resp.ContentLength64 = htmlBytes.Length;
                    resp.OutputStream.Write(htmlBytes, 0, htmlBytes.Length);
                    resp.Close();
                    return;
                }

                if (path.StartsWith("/api/"))
                {
                    object responseData = HandleApi(path, req);
                    string json = jsonSerializer.Serialize(responseData);
                    byte[] jsonBytes = Encoding.UTF8.GetBytes(json);

                    resp.ContentType = "application/json; charset=utf-8";
                    resp.ContentLength64 = jsonBytes.Length;
                    resp.OutputStream.Write(jsonBytes, 0, jsonBytes.Length);
                    resp.Close();
                    return;
                }

                resp.StatusCode = 404;
                resp.Close();
            }
            catch (Exception ex)
            {
                Console.WriteLine("API Error [{0}]: {1}\n{2}", req.Url.AbsolutePath, ex.Message, ex.StackTrace);
                try
                {
                    resp.StatusCode = 500;
                    byte[] errBytes = Encoding.UTF8.GetBytes(jsonSerializer.Serialize(new { error = ex.Message }));
                    resp.ContentType = "application/json";
                    resp.ContentLength64 = errBytes.Length;
                    resp.OutputStream.Write(errBytes, 0, errBytes.Length);
                    resp.Close();
                }
                catch { }
            }
        }

        private object HandleApi(string path, HttpListenerRequest req)
        {
            Dictionary<string, object> args = new Dictionary<string, object>();
            if (req.HttpMethod == "POST" && req.HasEntityBody)
            {
                using (var reader = new StreamReader(req.InputStream, req.ContentEncoding))
                {
                    string body = reader.ReadToEnd();
                    if (!string.IsNullOrEmpty(body))
                    {
                        args = jsonSerializer.Deserialize<Dictionary<string, object>>(body) ?? new Dictionary<string, object>();
                    }
                }
            }

            lock (state)
            {
                switch (path)
                {
                    case "/api/state":
                        state.ArenaLadder = CombatEngine.GetScaledArenaLadder(state.Player, state.ArenaLadder);
                        return state;

                    case "/api/save":
                        SaveManager.Save(state);
                        return new { status = "ok" };

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
                        int equipIdx = Convert.ToInt32(args["inventoryIndex"]);
                        EquipItem(equipIdx);
                        SaveManager.Save(state);
                        return state;

                    case "/api/unequip":
                        string slot = args["slot"].ToString();
                        UnequipSlot(slot);
                        SaveManager.Save(state);
                        return state;

                    case "/api/smelt":
                        int smeltIdx = Convert.ToInt32(args["inventoryIndex"]);
                        SmeltItem(smeltIdx);
                        SaveManager.Save(state);
                        return state;

                    case "/api/craft":
                        string recipeId = args["recipeId"].ToString();
                        CraftRecipe(recipeId);
                        SaveManager.Save(state);
                        return state;

                    case "/api/work":
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

                    case "/api/reset":
                        state = SaveManager.CreateDefaultState();
                        SaveManager.Save(state);
                        return state;

                    default:
                        return new { error = "Unknown Endpoint" };
                }
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

        private void RegenerateStats()
        {
            if (state == null || state.Player == null) return;
            DateTime now = DateTime.Now;

            // HP Regeneration driven by Constitution (2 + Constitution * 0.5 per min)
            if (state.LastHPRegen == default(DateTime))
            {
                state.LastHPRegen = now;
            }
            else
            {
                double hpElapsedMin = (now - state.LastHPRegen).TotalMinutes;
                if (hpElapsedMin >= 0.05)
                {
                    double hpRate = state.Player.GetHPRegenPerMinute();
                    int hpGained = (int)(hpElapsedMin * hpRate);
                    if (hpGained > 0)
                    {
                        state.Player.CurrentHP = Math.Min(state.Player.MaxHP, state.Player.CurrentHP + hpGained);
                        state.LastHPRegen = now;
                    }
                }
            }

            // Energy Regeneration
            if (state.LastEnergyRegen == default(DateTime))
            {
                state.LastEnergyRegen = now;
            }
            else
            {
                double energyElapsedMin = (now - state.LastEnergyRegen).TotalMinutes;
                if (energyElapsedMin >= 0.5)
                {
                    int energyGained = (int)(energyElapsedMin * 2);
                    if (energyGained > 0)
                    {
                        state.Player.CurrentEnergy = Math.Min(state.Player.MaxEnergy, state.Player.CurrentEnergy + energyGained);
                        state.LastEnergyRegen = now;
                    }
                }
            }
        }

        private void EquipItem(int invIdx)
        {
            Gladiator p = state.Player;
            if (invIdx < 0 || invIdx >= p.Inventory.Count) return;

            Item item = p.Inventory[invIdx];

            // Potion / Consumable handling with Intelligence healing multiplier
            if (item.Type == ItemType.Potion)
            {
                p.Inventory.RemoveAt(invIdx);
                if (item.HealAmount > 0)
                {
                    double intMult = p.GetIntHealMultiplier();
                    int effectiveHeal = (int)(item.HealAmount * intMult);
                    p.CurrentHP = Math.Min(p.MaxHP, p.CurrentHP + effectiveHeal);
                }
                if (item.EnergyAmount > 0)
                {
                    p.CurrentEnergy = Math.Min(p.MaxEnergy, p.CurrentEnergy + item.EnergyAmount);
                }
                return;
            }

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
