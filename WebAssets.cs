using System;

namespace GladiatusOffline
{
    public static class WebAssets
    {
        public static string IndexHtml = @"<!DOCTYPE html>
<html lang=""en"">
<head>
    <meta charset=""UTF-8"">
    <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">
    <title>Aeterna Roma - Hero of Rome</title>
    <link href=""https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Cinzel+Decorative:wght@700&family=Philosopher:ital,wght@0,400;0,700;1,400&display=swap"" rel=""stylesheet"">
    <style>
        :root {
            --bg-dark: #0f0a0a;
            --bg-card: #1c1414;
            --bg-card-hover: #2a1f1f;
            --border-gold: #c5a059;
            --text-gold: #ffd700;
            --text-primary: #e6dac3;
            --text-accent: #e5c158;
            --btn-red: #800000;
            --btn-red-hover: #a00000;
            --color-hp: #2e7d32;
            --color-energy: #1565c0;
            --color-xp: #7b1fa2;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        
        body {
            font-family: 'Philosopher', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-primary);
            background-image: radial-gradient(circle at 50% 20%, #2b1818 0%, #0f0a0a 80%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* HEADER & NAVBAR */
        header {
            background: linear-gradient(180deg, #1f1414 0%, #0f0a0a 100%);
            border-bottom: 2px solid var(--border-gold);
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.8);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .brand-title {
            font-family: 'Cinzel Decorative', serif;
            font-size: 26px;
            color: var(--text-gold);
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.4);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .resource-bar {
            display: flex;
            gap: 20px;
            background: rgba(0,0,0,0.5);
            padding: 8px 16px;
            border-radius: 20px;
            border: 1px solid rgba(197, 160, 89, 0.3);
        }

        .res-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: bold;
            font-size: 15px;
        }
        .res-gold { color: #ffd700; }
        .res-rubies { color: #ff5252; }
        .res-honor { color: #e040fb; }

        /* MAIN LAYOUT */
        .app-container {
            display: flex;
            flex: 1;
            padding: 20px;
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
        }

        /* LEFT SIDEBAR: GLADIATOR STATS */
        .sidebar {
            width: 320px;
            background: var(--bg-card);
            border: 2px solid var(--border-gold);
            border-radius: 8px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
        }

        .avatar-box {
            text-align: center;
            background: rgba(0,0,0,0.4);
            border: 1px solid var(--border-gold);
            border-radius: 6px;
            padding: 15px;
            position: relative;
        }

        .avatar-svg {
            width: 120px;
            height: 120px;
            filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.3));
        }

        .gladiator-name {
            font-family: 'Cinzel', serif;
            font-size: 20px;
            color: var(--text-gold);
            margin-top: 8px;
        }

        .gladiator-level {
            font-size: 13px;
            color: var(--text-accent);
        }

        /* PROGRESS BARS */
        .stat-bar-container {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .stat-bar-label {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            font-weight: bold;
        }

        .stat-bar {
            height: 14px;
            background: #222;
            border-radius: 7px;
            overflow: hidden;
            border: 1px solid #444;
            position: relative;
        }

        .stat-fill {
            height: 100%;
            transition: width 0.3s ease;
        }

        .fill-hp { background: linear-gradient(90deg, #1b5e20, #4caf50); }
        .fill-energy { background: linear-gradient(90deg, #0d47a1, #2196f3); }
        .fill-xp { background: linear-gradient(90deg, #4a148c, #ab47bc); }

        /* EQUIPMENT SLOTS GRID */
        .equipment-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 6px;
            border: 1px solid rgba(197, 160, 89, 0.2);
        }

        .equip-slot {
            width: 60px;
            height: 60px;
            background: rgba(0,0,0,0.6);
            border: 1px dashed var(--border-gold);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            position: relative;
            transition: transform 0.2s;
        }

        .equip-slot:hover {
            transform: scale(1.05);
            border-style: solid;
            box-shadow: 0 0 8px var(--border-gold);
        }

        .equip-slot.empty::after {
            content: attr(data-slot);
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
        }

        /* MAIN CONTENT VIEW */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        /* NAVIGATION TABS */
        .nav-tabs {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            background: rgba(0,0,0,0.4);
            padding: 8px;
            border-radius: 8px;
            border: 1px solid var(--border-gold);
        }

        .nav-tab {
            padding: 10px 18px;
            background: linear-gradient(180deg, #2b1d1d 0%, #150d0d 100%);
            border: 1px solid var(--border-gold);
            color: var(--text-primary);
            font-family: 'Cinzel', serif;
            font-weight: bold;
            font-size: 14px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .nav-tab:hover {
            background: linear-gradient(180deg, #4a2d2d 0%, #2b1d1d 100%);
            color: var(--text-gold);
        }

        .nav-tab.active {
            background: linear-gradient(180deg, var(--btn-red) 0%, #4a0000 100%);
            color: var(--text-gold);
            box-shadow: 0 0 10px var(--btn-red);
            border-color: var(--text-gold);
        }

        /* TAB PANELS */
        .tab-panel {
            background: var(--bg-card);
            border: 2px solid var(--border-gold);
            border-radius: 8px;
            padding: 20px;
            flex: 1;
            min-height: 500px;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* BUTTONS & UI COMPONENTS */
        .btn-roman {
            background: linear-gradient(180deg, var(--btn-red) 0%, #4a0000 100%);
            color: var(--text-gold);
            border: 1px solid var(--border-gold);
            padding: 8px 16px;
            font-family: 'Cinzel', serif;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-roman:hover {
            background: linear-gradient(180deg, #a00000 0%, #600000 100%);
            box-shadow: 0 0 8px rgba(255, 215, 0, 0.4);
        }

        .btn-gold {
            background: linear-gradient(180deg, #c5a059 0%, #7a602f 100%);
            color: #000;
        }
        .btn-gold:hover {
            background: linear-gradient(180deg, #ffd700 0%, #c5a059 100%);
        }

        /* INVENTORY GRID */
        .inventory-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 10px;
            margin-top: 15px;
        }

        .inv-slot {
            width: 70px;
            height: 70px;
            background: rgba(0,0,0,0.5);
            border: 1px solid #444;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            position: relative;
            transition: transform 0.2s;
        }

        .inv-slot:hover {
            transform: scale(1.05);
            border-color: var(--border-gold);
        }

        .rarity-Common { border-color: #888; }
        .rarity-Uncommon { border-color: #2e7d32; box-shadow: inset 0 0 5px #2e7d32; }
        .rarity-Rare { border-color: #1565c0; box-shadow: inset 0 0 8px #1565c0; }
        .rarity-Epic { border-color: #7b1fa2; box-shadow: inset 0 0 10px #7b1fa2; }
        .rarity-Legendary { border-color: #ffd700; box-shadow: inset 0 0 12px #ffd700; }

        /* EXPEDITIONS & ARENA CARDS */
        .exp-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }

        .exp-card {
            background: rgba(0,0,0,0.4);
            border: 1px solid var(--border-gold);
            border-radius: 6px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .monster-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 10px;
        }

        .monster-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.03);
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid rgba(255,255,255,0.05);
        }

        /* COMBAT LOG MODAL OVERLAY */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.85);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .combat-modal {
            background: var(--bg-card);
            border: 2px solid var(--border-gold);
            border-radius: 8px;
            width: 100%;
            max-width: 650px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 0 30px rgba(0,0,0,0.9);
        }

        .modal-header {
            padding: 15px;
            border-bottom: 1px solid var(--border-gold);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.4);
        }

        .modal-body {
            padding: 15px;
            overflow-y: auto;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .turn-line {
            padding: 6px 10px;
            border-radius: 4px;
            font-size: 13px;
            background: rgba(255,255,255,0.03);
        }

        .turn-player { border-left: 3px solid #2196f3; }
        .turn-enemy { border-left: 3px solid #f44336; }
        .turn-crit { background: rgba(255, 215, 0, 0.1); border-left-color: #ffd700; }

        .combat-result-banner {
            text-align: center;
            padding: 12px;
            font-family: 'Cinzel Decorative', serif;
            font-size: 22px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .victory-bg { background: rgba(46, 125, 50, 0.4); color: #4caf50; border: 1px solid #4caf50; }
        .defeat-bg { background: rgba(198, 40, 40, 0.4); color: #f44336; border: 1px solid #f44336; }

        .overview-subtabs {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            border-bottom: 1px solid var(--border-gold);
            padding-bottom: 8px;
        }
        .subtab-btn {
            background: rgba(0,0,0,0.4);
            border: 1px solid var(--border-gold);
            color: var(--text-primary);
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Cinzel', serif;
            font-size: 12px;
        }
        .subtab-btn.active {
            background: var(--btn-red);
            color: var(--text-gold);
        }
    </style>
</head>
<body>

    <header>
        <div class=""brand-title"">
            🦅 <span>Aeterna Roma</span>
        </div>
        <div class=""resource-bar"">
            <div class=""res-item res-gold"">💰 <span id=""resGold"">0</span></div>
            <div class=""res-item res-rubies"">💎 <span id=""resRubies"">0</span></div>
            <div class=""res-item res-honor"">🏆 <span id=""resHonor"">0</span></div>
        </div>
        <div>
            <button class=""btn-roman"" onclick=""playAudio('click'); saveGame();"">💾 Save</button>
            <button class=""btn-roman btn-gold"" id=""btnMute"" onclick=""toggleAudio();"">🔊 Audio</button>
        </div>
    </header>

    <div class=""app-container"">
        <!-- SIDEBAR -->
        <div class=""sidebar"">
            <div class=""avatar-box"">
                <div id=""avatarContainer""></div>
                <div class=""gladiator-name"" id=""gladName"">Gladiator</div>
                <div class=""gladiator-level"" id=""gladLevel"">LVL 1</div>
            </div>

            <!-- STAT BARS -->
            <div class=""stat-bar-container"">
                <div class=""stat-bar-label""><span>HP</span><span id=""textHp"">100/100</span></div>
                <div class=""stat-bar""><div class=""stat-fill fill-hp"" id=""fillHp"" style=""width:100%""></div></div>
            </div>

            <div class=""stat-bar-container"">
                <div class=""stat-bar-label""><span>Energy</span><span id=""textEnergy"">24/24</span></div>
                <div class=""stat-bar""><div class=""stat-fill fill-energy"" id=""fillEnergy"" style=""width:100%""></div></div>
            </div>

            <div class=""stat-bar-container"">
                <div class=""stat-bar-label""><span>Damage</span><span id=""statDmg"">3 - 6</span></div>
            </div>

            <div class=""stat-bar-container"">
                <div class=""stat-bar-label""><span>Armor</span><span id=""statArmor"">0</span></div>
            </div>

            <div class=""stat-bar-container"">
                <div class=""stat-bar-label""><span>Arena Rank</span><span id=""statRank"">#10</span></div>
            </div>

            <!-- EQUIPMENT SLOTS -->
            <div style=""font-family:'Cinzel',serif; font-size:12px; color:var(--text-gold); text-align:center; margin-top:5px;"">EQUIPPED GEAR</div>
            <div class=""equipment-grid"">
                <div class=""equip-slot empty"" data-slot=""Head"" id=""slot-Head"" onclick=""clickEquipSlot('Head')""></div>
                <div class=""equip-slot empty"" data-slot=""Chest"" id=""slot-Chest"" onclick=""clickEquipSlot('Chest')""></div>
                <div class=""equip-slot empty"" data-slot=""Gloves"" id=""slot-Gloves"" onclick=""clickEquipSlot('Gloves')""></div>
                <div class=""equip-slot empty"" data-slot=""Shoes"" id=""slot-Shoes"" onclick=""clickEquipSlot('Shoes')""></div>
                <div class=""equip-slot empty"" data-slot=""Weapon"" id=""slot-Weapon"" onclick=""clickEquipSlot('Weapon')""></div>
                <div class=""equip-slot empty"" data-slot=""Shield"" id=""slot-Shield"" onclick=""clickEquipSlot('Shield')""></div>
                <div class=""equip-slot empty"" data-slot=""Ring"" id=""slot-Ring"" onclick=""clickEquipSlot('Ring')""></div>
                <div class=""equip-slot empty"" data-slot=""Amulet"" id=""slot-Amulet"" onclick=""clickEquipSlot('Amulet')""></div>
            </div>
        </div>

        <!-- MAIN PANEL -->
        <div class=""main-content"">
            <div class=""nav-tabs"">
                <button class=""nav-tab active"" onclick=""switchTab('overview', this)"">🏛️ Gladiator</button>
                <button class=""nav-tab"" onclick=""switchTab('training', this)"">💪 Training</button>
                <button class=""nav-tab"" onclick=""switchTab('expeditions', this)"">🗺️ Expeditions</button>
                <button class=""nav-tab"" onclick=""switchTab('arena', this)"">⚔️ Colosseum</button>
                <button class=""nav-tab"" onclick=""switchTab('dungeons', this)"">🗝️ Dungeons</button>
                <button class=""nav-tab"" onclick=""switchTab('merchants', this)"">⚖️ Merchants</button>
                <button class=""nav-tab"" onclick=""switchTab('forge', this)"">🔥 The Forge</button>
                <button class=""nav-tab"" onclick=""switchTab('work', this)"">🌾 Villa Work</button>
                <button class=""nav-tab"" onclick=""switchTab('guild', this)"">🦅 Guild</button>
                <button class=""nav-tab"" onclick=""switchTab('settings', this)"">⚙️ Settings</button>
            </div>

            <div class=""tab-panel"">
                <!-- OVERVIEW TAB -->
                <div id=""tab-overview"" class=""tab-content active"">
                    <div class=""overview-subtabs"">
                        <button class=""subtab-btn active"" id=""ovSubtabBtnBase"" onclick=""switchOverviewSubtab('base')"">Base Attributes</button>
                        <button class=""subtab-btn"" id=""ovSubtabBtnHidden"" onclick=""switchOverviewSubtab('hidden')"">Hidden & Combat Stats</button>
                    </div>

                    <div id=""ovSubtab-base"">
                        <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Gladiator Overview</h2>
                        <div style=""display:grid; grid-template-columns: 1fr 1fr; gap:20px;"">
                            <div>
                                <h4 style=""color:var(--text-accent); margin-bottom:10px;"">Core Attributes</h4>
                                <div class=""monster-list"">
                                    <div class=""monster-row""><span>Strength (Dmg & Block)</span><strong id=""attrStr"">5</strong></div>
                                    <div class=""monster-row""><span>Dexterity (Hit & Crit)</span><strong id=""attrDex"">5</strong></div>
                                    <div class=""monster-row""><span>Agility (Dodge & Block)</span><strong id=""attrAgi"">5</strong></div>
                                    <div class=""monster-row""><span>Constitution (Max HP & Regen)</span><strong id=""attrCon"">5</strong></div>
                                    <div class=""monster-row""><span>Charisma (Double Strike)</span><strong id=""attrCha"">5</strong></div>
                                    <div class=""monster-row""><span>Intelligence (Crit Dmg & Potions)</span><strong id=""attrInt"">5</strong></div>
                                </div>
                            </div>
                            <div>
                                <h4 style=""color:var(--text-accent); margin-bottom:10px;"">Progress & Level</h4>
                                <div class=""monster-list"">
                                    <div class=""monster-row""><span>Level</span><strong id=""ovLvl"">1</strong></div>
                                    <div class=""monster-row""><span>Experience</span><strong id=""ovXpText"">0 / 100 XP</strong></div>
                                </div>
                                <div class=""stat-bar"" style=""margin-top:10px;""><div class=""stat-fill fill-xp"" id=""ovXpFill"" style=""width:0%""></div></div>
                            </div>
                        </div>

                        <h3 style=""font-family:'Cinzel',serif; color:var(--text-gold); margin-top:25px; margin-bottom:10px;"">Inventory Items</h3>
                        <div class=""inventory-grid"" id=""inventoryContainer""></div>
                        <div id=""selectedItemPanel"" style=""margin-top:15px; padding:12px; background:rgba(0,0,0,0.4); border:1px solid var(--border-gold); border-radius:6px; display:none;""></div>
                    </div>

                    <div id=""ovSubtab-hidden"" style=""display:none;"">
                        <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Hidden & Combat Formulae</h2>
                        <div class=""monster-list"" id=""hiddenStatsGrid""></div>
                    </div>
                </div>

                <!-- TRAINING TAB -->
                <div id=""tab-training"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Campus Martialis - Training</h2>
                    <p style=""font-size:13px; margin-bottom:15px;"">Train your gladiator's physical attributes to increase combat potency in Arena and Expeditions.</p>
                    <div class=""monster-list"" id=""trainingContainer""></div>
                </div>

                <!-- EXPEDITIONS TAB -->
                <div id=""tab-expeditions"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Expeditions across the Empire</h2>
                    <div class=""exp-grid"" id=""expeditionContainer""></div>
                </div>

                <!-- ARENA TAB -->
                <div id=""tab-arena"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">The Colosseum Arena</h2>
                    <div class=""monster-list"" id=""arenaContainer""></div>
                </div>

                <!-- DUNGEONS TAB -->
                <div id=""tab-dungeons"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Catacombs & Dungeons</h2>
                    <div class=""exp-grid"" id=""dungeonContainer""></div>
                </div>

                <!-- MERCHANTS TAB -->
                <div id=""tab-merchants"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Forum Boarium - Merchants</h2>
                    <div style=""display:flex; gap:10px; margin-bottom:15px;"">
                        <button class=""btn-roman"" onclick=""switchVendor('armorer')"">🛡️ Armorer</button>
                        <button class=""btn-roman"" onclick=""switchVendor('weaponsmith')"">⚔️ Weaponsmith</button>
                        <button class=""btn-roman"" onclick=""switchVendor('alchemist')"">🧪 Alchemist</button>
                    </div>
                    <div class=""inventory-grid"" id=""merchantContainer""></div>
                </div>

                <!-- FORGE TAB -->
                <div id=""tab-forge"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Vulcan's Forge</h2>
                    <div id=""forgeStashInfo"" style=""margin-bottom:15px; background:rgba(0,0,0,0.4); padding:10px; border-radius:6px; border:1px solid var(--border-gold);""></div>
                    <div class=""exp-grid"" id=""forgeRecipeContainer""></div>
                </div>

                <!-- WORK TAB -->
                <div id=""tab-work"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Roman Villa Work</h2>
                    <p style=""margin-bottom:15px;"">Perform manual labor for patrician lords to earn honest Gold and Experience.</p>
                    <button class=""btn-roman btn-gold"" onclick=""startWork()"">Start Work</button>
                </div>

                <!-- GUILD TAB -->
                <div id=""tab-guild"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Gladiator Guild House</h2>
                    <div id=""guildContent""></div>
                </div>

                <!-- SETTINGS TAB -->
                <div id=""tab-settings"" class=""tab-content"">
                    <h2 style=""font-family:'Cinzel Decorative',serif; color:var(--text-gold); margin-bottom:10px;"">Settings & Controls</h2>
                    <div style=""display:flex; flex-direction:column; gap:10px; max-width:300px;"">
                        <button class=""btn-roman btn-gold"" id=""btnToggleFS"" onclick=""toggleFullscreen()"">📺 Fullscreen</button>
                        <button class=""btn-roman btn-gold"" onclick=""saveGame()"">💾 Quick Save</button>
                        <button class=""btn-roman"" onclick=""exportSaveJSON()"">📥 Export Save</button>
                        <button class=""btn-roman"" onclick=""promptImportSave()"">📤 Import Save</button>
                    </div>
                    <div style=""margin-top:30px; border-top:1px solid #444; padding-top:15px;"">
                        <button class=""btn-roman"" style=""background:#800000; border-color:#ff4d4d; color:#fff; width:100%; justify-content:center; margin-top:5px;"" onclick=""resetGameConfirm()"">🔄 Reset Gladiator Progress</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- COMBAT REPORT MODAL -->
    <div class=""modal-overlay"" id=""combatModal"">
        <div class=""combat-modal"">
            <div class=""modal-header"">
                <span id=""modalCombatTitle"">COMBAT REPORT</span>
                <button style=""background:none; border:none; color:#ffd700; font-size:24px; cursor:pointer;"" onclick=""closeCombatModal()"">✕</button>
            </div>
            <div class=""modal-body"">
                <div class=""combat-result-banner"" id=""modalCombatResultBanner"">VICTORY!</div>
                <div style=""display:flex; justify-content:space-between; margin-bottom:10px; font-weight:bold; font-size:14px;"">
                    <span id=""modalFighter1Name"" style=""color:#2196f3;"">Player</span>
                    <span style=""color:#888;"">VS</span>
                    <span id=""modalFighter2Name"" style=""color:#f44336;"">Enemy</span>
                </div>
                <div id=""modalCombatLog""></div>
            </div>
        </div>
    </div>

    <script>
        let gameState = null;
        let selectedInventoryIndex = -1;
        let audioMuted = false;
        let audioCtx = null;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
        }

        function playAudio(type) {
            if (audioMuted) return;
            try {
                initAudio();
                const now = audioCtx.currentTime;
                if (type === 'click') {
                    let osc = audioCtx.createOscillator();
                    let gain = audioCtx.createGain();
                    osc.frequency.setValueAtTime(400, now);
                    osc.frequency.exponentialRampToValueAtTime(200, now + 0.05);
                    gain.gain.setValueAtTime(0.15, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.05);
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start(now);
                    osc.stop(now + 0.05);
                } else if (type === 'hit') {
                    let osc = audioCtx.createOscillator();
                    let gain = audioCtx.createGain();
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(150, now);
                    osc.frequency.exponentialRampToValueAtTime(40, now + 0.15);
                    gain.gain.setValueAtTime(0.3, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.15);
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start(now);
                    osc.stop(now + 0.15);
                } else if (type === 'victory') {
                    let notes = [261.63, 329.63, 392.00, 523.25];
                    notes.forEach((freq, i) => {
                        let osc = audioCtx.createOscillator();
                        let gain = audioCtx.createGain();
                        osc.frequency.setValueAtTime(freq, now + i * 0.1);
                        gain.gain.setValueAtTime(0.2, now + i * 0.1);
                        gain.gain.linearRampToValueAtTime(0.01, now + i * 0.1 + 0.2);
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        osc.start(now + i * 0.1);
                        osc.stop(now + i * 0.1 + 0.2);
                    });
                }
            } catch(e) {}
        }

        function toggleAudio() {
            audioMuted = !audioMuted;
            document.getElementById('btnMute').innerText = audioMuted ? '🔇 Muted' : '🔊 Audio';
        }

        function getSVGIcon(iconType) {
            if (!iconType) return '🗡️';
            if (iconType.startsWith('weapon')) return `<svg viewBox=""0 0 64 64"" width=""36"" height=""36""><path d=""M20 50 L44 14 L50 20 L26 56 Z"" fill=""#cccccc"" stroke=""#ffd700"" stroke-width=""2""/></svg>`;
            if (iconType.startsWith('helmet')) return `<svg viewBox=""0 0 64 64"" width=""36"" height=""36""><path d=""M16 36 C16 18 48 18 48 36 Z"" fill=""#888888"" stroke=""#ffd700"" stroke-width=""2""/></svg>`;
            if (iconType.startsWith('armor')) return `<svg viewBox=""0 0 64 64"" width=""36"" height=""36""><rect x=""14"" y=""16"" width=""36"" height=""40"" rx=""6"" fill=""#666666"" stroke=""#ffd700"" stroke-width=""2""/></svg>`;
            if (iconType.startsWith('shield')) return `<svg viewBox=""0 0 64 64"" width=""36"" height=""36""><path d=""M16 12 L48 12 L48 38 C48 50 32 58 32 58 C32 58 16 50 16 38 Z"" fill=""#aa2222"" stroke=""#ffd700"" stroke-width=""2""/></svg>`;
            return '🛡️';
        }

        function renderGladiatorAvatar(glad) {
            return `<svg class=""avatar-svg"" viewBox=""0 0 100 120"">
                <!-- Body Base -->
                <circle cx=""50"" cy=""30"" r=""18"" fill=""#dca376""/>
                <rect x=""35"" y=""48"" width=""30"" height=""45"" rx=""5"" fill=""#800000""/>
                <rect x=""25"" y=""50"" width=""10"" height=""35"" fill=""#dca376""/>
                <rect x=""65"" y=""50"" width=""10"" height=""35"" fill=""#dca376""/>
                <rect x=""38"" y=""93"" width=""10"" height=""20"" fill=""#dca376""/>
                <rect x=""52"" y=""93"" width=""10"" height=""20"" fill=""#dca376""/>
                <!-- Armor Overlay -->
                <path d=""M35 50 L65 50 L60 80 L40 80 Z"" fill=""#707070"" stroke=""#ffd700"" stroke-width=""1.5""/>
                <!-- Sandals -->
                <rect x=""38"" y=""103"" width=""10"" height=""40"" fill=""#573e27""/>
                <rect x=""52"" y=""103"" width=""10"" height=""40"" fill=""#573e27""/>
                <!-- Helmet -->
                <path d=""M34 32 C34 15 66 15 66 32 Z"" fill=""#707070"" stroke=""#ffd700"" stroke-width=""2""/>
                <path d=""M50 10 L50 25"" stroke=""#cc0000"" stroke-width=""5""/>
            </svg>`;
        }

        async function loadState() {
            try {
                let res = await fetch('/api/state');
                gameState = await res.json();
                renderUI();
            } catch (e) {
                console.error('Error loading state:', e);
            }
        }

        function renderUI() {
            if (!gameState) return;
            const glad = gameState.Player;

            // Top Header Resources
            document.getElementById('resGold').innerText = glad.Gold.toLocaleString();
            document.getElementById('resRubies').innerText = glad.Rubies;
            document.getElementById('resHonor').innerText = glad.Honor;

            document.getElementById('textHp').innerText = `${glad.CurrentHP}/${glad.MaxHP}`;
            document.getElementById('fillHp').style.width = `${Math.max(0, Math.min(100, (glad.CurrentHP / glad.MaxHP) * 100))}%`;

            document.getElementById('textEnergy').innerText = `${glad.CurrentEnergy}/${glad.MaxEnergy}`;
            document.getElementById('fillEnergy').style.width = `${Math.max(0, Math.min(100, (glad.CurrentEnergy / glad.MaxEnergy) * 100))}%`;

            // Gladiator Panel
            document.getElementById('gladName').innerText = glad.Name;
            document.getElementById('gladLevel').innerText = `LVL ${glad.Level}`;

            // Calculate derived stats
            let minDmg = 3 + Math.floor((glad.BaseStrength + getBonus('Strength')) / 2);
            let maxDmg = 6 + Math.floor((glad.BaseStrength + getBonus('Strength')) / 2);
            if (glad.Equipment.Weapon) {
                minDmg += glad.Equipment.Weapon.MinDamage;
                maxDmg += glad.Equipment.Weapon.MaxDamage;
            }
            document.getElementById('statDmg').innerText = `${minDmg} - ${maxDmg}`;

            let armor = 0;
            for (let k in glad.Equipment) {
                if (glad.Equipment[k]) armor += glad.Equipment[k].Armor;
            }
            document.getElementById('statArmor').innerText = armor;
            document.getElementById('statRank').innerText = `#${glad.ArenaRank}`;

            // Render Avatar SVG
            document.getElementById('avatarContainer').innerHTML = renderGladiatorAvatar(glad);

            // Render Equipment Slots
            const slots = ['Head', 'Chest', 'Gloves', 'Shoes', 'Weapon', 'Shield', 'Ring', 'Amulet'];
            slots.forEach(slot => {
                let el = document.getElementById(`slot-${slot}`);
                if (glad.Equipment[slot]) {
                    let item = glad.Equipment[slot];
                    el.className = `equip-slot rarity-${item.Rarity}`;
                    el.innerHTML = getSVGIcon(item.IconSvg);
                } else {
                    el.className = `equip-slot empty`;
                    el.innerHTML = '';
                }
            });

            // Overview Attributes
            document.getElementById('attrStr').innerText = glad.BaseStrength + getBonus('Strength');
            document.getElementById('attrDex').innerText = glad.BaseDexterity + getBonus('Dexterity');
            document.getElementById('attrAgi').innerText = glad.BaseAgility + getBonus('Agility');
            document.getElementById('attrCon').innerText = glad.BaseConstitution + getBonus('Constitution');
            document.getElementById('attrCha').innerText = glad.BaseCharisma + getBonus('Charisma');
            document.getElementById('attrInt').innerText = glad.BaseIntelligence + getBonus('Intelligence');

            document.getElementById('ovLvl').innerText = glad.Level;
            document.getElementById('ovXpText').innerText = `${glad.XP} / ${glad.MaxXP} XP`;
            document.getElementById('ovXpFill').style.width = `${Math.min(100, (glad.XP / glad.MaxXP) * 100)}%`;

            // Render Tabs
            renderInventory();
            renderMerchants();
            renderTraining();
            renderExpeditions();
            renderArena();
            renderDungeons();
            renderForge();
            renderGuild();
            renderSettings();

            if (document.getElementById('ovSubtab-hidden') && document.getElementById('ovSubtab-hidden').style.display !== 'none') {
                renderHiddenStats();
            }
        }

        function switchOverviewSubtab(subId) {
            playAudio('click');
            const btnBase = document.getElementById('ovSubtabBtnBase');
            const btnHidden = document.getElementById('ovSubtabBtnHidden');
            const tabBase = document.getElementById('ovSubtab-base');
            const tabHidden = document.getElementById('ovSubtab-hidden');

            if (!btnBase || !btnHidden || !tabBase || !tabHidden) return;

            btnBase.classList.remove('active');
            btnHidden.classList.remove('active');
            tabBase.style.display = 'none';
            tabHidden.style.display = 'none';

            if (subId === 'base') {
                btnBase.classList.add('active');
                tabBase.style.display = 'block';
            } else {
                btnHidden.classList.add('active');
                tabHidden.style.display = 'block';
                renderHiddenStats();
            }
        }

        function renderHiddenStats() {
            if (!gameState || !gameState.Player) return;
            const glad = gameState.Player;
            const str = glad.BaseStrength + getBonus('Strength');
            const dex = glad.BaseDexterity + getBonus('Dexterity');
            const agi = glad.BaseAgility + getBonus('Agility');
            const con = glad.BaseConstitution + getBonus('Constitution');
            const cha = glad.BaseCharisma + getBonus('Charisma');
            const intel = glad.BaseIntelligence + getBonus('Intelligence');

            let armor = 0;
            if (glad.Equipment) {
                for (let k in glad.Equipment) {
                    if (glad.Equipment[k] && glad.Equipment[k].Armor) armor += glad.Equipment[k].Armor;
                }
            }

            const hasShield = glad.Equipment && glad.Equipment.Shield != null;

            const hpMin = Math.round((2.0 + con * 0.5) * 60);
            const hpMinRate = (2.0 + con * 0.5).toFixed(1);
            const blockChance = Math.min(30, Math.round((agi * 0.5) + (str * 0.3) + (hasShield ? 8 : 0)));
            const hitChance = Math.min(95, Math.max(15, Math.round((dex / (dex + agi)) * 115)));
            const critChance = Math.min(40, Math.round(5 + ((dex / (dex + agi)) * 12) + (intel * 0.3)));
            const critDmg = (150 + (intel * 1.5)).toFixed(1);
            const doubleHit = Math.min(30, Math.max(2, Math.round((cha / (cha * 2)) * 22)));
            const healBonus = Math.round(intel * 2);
            const armorRed = (100 - (10000 / (100 + armor * 0.45))).toFixed(1);
            const armorPen = Math.round(str * 0.5);

            const stats = [
                { icon: '🛡️', title: 'Block Value / Parry Chance', val: `${blockChance}%`, desc: `Derived from Agility, Strength & ${hasShield ? 'Shield (+8%)' : 'No Shield'}` },
                { icon: '🎯', title: 'Base Hit Chance', val: `${hitChance}%`, desc: 'Derived from Dexterity vs Enemy Agility ratio' },
                { icon: '⚡', title: 'Critical Strike Chance', val: `${critChance}%`, desc: 'Derived from Dexterity & Intelligence' },
                { icon: '💥', title: 'Critical Damage Multiplier', val: `${critDmg}%`, desc: `+${(intel * 1.5).toFixed(1)}% bonus damage from Intelligence` },
                { icon: '⚔️', title: 'Double Strike Chance', val: `${doubleHit}%`, desc: 'Gladiatus Charisma second attack chance' },
                { icon: '❤️', title: 'HP Regeneration Rate', val: `+${hpMin} HP/h`, desc: `+${hpMinRate} HP/min (driven by ${con} Constitution)` },
                { icon: '🧪', title: 'Healing Potion Bonus', val: `+${healBonus}%`, desc: `+2% item healing per Intelligence point` },
                { icon: '🛡️', title: 'Armor Damage Reduction', val: `${armorRed}%`, desc: `Damage mitigation from ${armor} total Armor points` },
                { icon: '🗡️', title: 'Armor Penetration', val: `-${armorPen} Armor`, desc: `Enemy armor bypassed by ${str} Strength` }
            ];

            let html = '';
            stats.forEach(s => {
                html += `<div class=""monster-row"">
                    <div>
                        <span style=""font-family:'Cinzel',serif; color:var(--text-accent); font-weight:bold;"">${s.icon} ${s.title}</span>
                        <div style=""font-size:11px; color:var(--text-primary); opacity:0.8;"">${s.desc}</div>
                    </div>
                    <strong style=""color:var(--text-primary); font-size:13px;"">${s.val}</strong>
                </div>`;
            });

            const container = document.getElementById('hiddenStatsGrid');
            if (container) container.innerHTML = html;
        }

        function getBonus(stat) {
            let bonus = 0;
            const glad = gameState.Player;
            for (let k in glad.Equipment) {
                let item = glad.Equipment[k];
                if (item && item[stat]) bonus += item[stat];
            }
            return bonus;
        }

        function renderInventory() {
            let container = document.getElementById('inventoryContainer');
            let html = '';
            const inv = gameState.Player.Inventory;

            for (let i = 0; i < gameState.Player.InventoryCapacity; i++) {
                if (i < inv.length) {
                    let item = inv[i];
                    html += `<div class=""inv-slot rarity-${item.Rarity} ${selectedInventoryIndex === i ? 'selected' : ''}"" onclick=""selectInventoryItem(${i})"">
                        ${getSVGIcon(item.IconSvg)}
                    </div>`;
                } else {
                    html += `<div class=""inv-slot"" style=""opacity:0.2;""></div>`;
                }
            }
            container.innerHTML = html;
        }

        function selectInventoryItem(idx) {
            playAudio('click');
            selectedInventoryIndex = idx;
            renderInventory();
            let item = gameState.Player.Inventory[idx];
            let panel = document.getElementById('selectedItemPanel');
            if (!item) {
                panel.style.display = 'none';
                return;
            }

            let name = item.Name;
            if (item.Prefix) name = item.Prefix + ' ' + name;
            if (item.Suffix) name = name + ' ' + item.Suffix;

            let html = `<div style=""font-weight:bold; color:var(--text-gold); margin-bottom:5px;"">${name} (${item.Rarity})</div>`;
            if (item.MinDamage) html += `<div>Damage: ${item.MinDamage} - ${item.MaxDamage}</div>`;
            if (item.Armor) html += `<div>Armor: +${item.Armor}</div>`;
            if (item.Strength) html += `<div>Strength: +${item.Strength}</div>`;
            if (item.Dexterity) html += `<div>Dexterity: +${item.Dexterity}</div>`;
            if (item.Agility) html += `<div>Agility: +${item.Agility}</div>`;
            if (item.Constitution) html += `<div>Constitution: +${item.Constitution}</div>`;
            if (item.Charisma) html += `<div>Charisma: +${item.Charisma}</div>`;
            if (item.Intelligence) html += `<div>Intelligence: +${item.Intelligence}</div>`;
            if (item.HealAmount) html += `<div>Restores: +${item.HealAmount} HP</div>`;

            html += `<div style=""margin-top:10px; display:flex; gap:10px;"">`;
            if (item.Type === 8) { // Potion
                html += `<button class=""btn-roman btn-gold"" onclick=""usePotion(${idx})"">Drink Potion</button>`;
            } else {
                html += `<button class=""btn-roman btn-gold"" onclick=""equipItem(${idx})"">Equip</button>`;
            }
            html += `<button class=""btn-roman"" onclick=""sellItem(${idx})"">Sell (${item.Price} Gold)</button>`;
            html += `<button class=""btn-roman"" onclick=""smeltItem(${idx})"">Smelt</button>`;
            html += `</div>`;

            panel.innerHTML = html;
            panel.style.display = 'block';
        }

        async function equipItem(idx) {
            playAudio('click');
            let res = await fetch('/api/equip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ inventoryIndex: idx })
            });
            gameState = await res.json();
            selectedInventoryIndex = -1;
            document.getElementById('selectedItemPanel').style.display = 'none';
            renderUI();
        }

        async function usePotion(idx) {
            playAudio('click');
            let res = await fetch('/api/equip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ inventoryIndex: idx })
            });
            gameState = await res.json();
            selectedInventoryIndex = -1;
            document.getElementById('selectedItemPanel').style.display = 'none';
            renderUI();
        }

        async function clickEquipSlot(slot) {
            playAudio('click');
            if (gameState.Player.Equipment[slot]) {
                let res = await fetch('/api/unequip', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ slot: slot })
                });
                gameState = await res.json();
                renderUI();
            }
        }

        async function sellItem(idx) {
            playAudio('click');
            let res = await fetch('/api/sell', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ inventoryIndex: idx })
            });
            gameState = await res.json();
            selectedInventoryIndex = -1;
            document.getElementById('selectedItemPanel').style.display = 'none';
            renderUI();
        }

        async function smeltItem(idx) {
            playAudio('click');
            let res = await fetch('/api/smelt', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ inventoryIndex: idx })
            });
            gameState = await res.json();
            selectedInventoryIndex = -1;
            document.getElementById('selectedItemPanel').style.display = 'none';
            renderUI();
        }

        function renderTraining() {
            const glad = gameState.Player;
            const attrs = ['Strength', 'Dexterity', 'Agility', 'Constitution', 'Charisma', 'Intelligence'];
            let html = '';

            attrs.forEach(attr => {
                let baseVal = glad[`Base${attr}`];
                let cost = Math.floor(baseVal * baseVal * 2.5) + 15;
                html += `<div class=""monster-row"">
                    <div>
                        <strong style=""color:var(--text-gold);"">${attr}</strong> - Current Base: ${baseVal}
                    </div>
                    <button class=""btn-roman btn-gold"" onclick=""trainAttr('${attr}')"">Train (${cost} Gold)</button>
                </div>`;
            });
            document.getElementById('trainingContainer').innerHTML = html;
        }

        async function trainAttr(attr) {
            playAudio('click');
            let res = await fetch('/api/train', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ attribute: attr })
            });
            gameState = await res.json();
            renderUI();
        }

        function renderExpeditions() {
            let html = '';
            const glad = gameState.Player;
            gameState.Locations.forEach(loc => {
                let levelDelta = Math.max(0, glad.Level - loc.ReqLevel);
                html += `<div class=""exp-card"">
                    <h3 style=""color:var(--text-accent); font-family:'Cinzel',serif;"">${loc.Name}</h3>
                    <p style=""font-size:12px; color:var(--text-primary);"">${loc.Description}</p>
                    <div style=""font-size:12px; color:var(--text-accent);"">Req. Level: ${loc.ReqLevel} | Energy Cost: ${loc.EnergyCost}</div>
                    <div class=""monster-list"">`;
                
                loc.Monsters.forEach(m => {
                    let scaledLvl = m.Level + levelDelta;
                    html += `<div class=""monster-row"">
                        <div>
                            <strong style=""color:var(--text-primary);"">${m.Name}</strong> <span style=""font-size:11px; color:var(--text-accent);"">LVL ${scaledLvl}</span>
                        </div>
                        <button class=""btn-roman"" onclick=""startExpedition(${loc.Id}, '${m.Id}')"">Attack ⚔️</button>
                    </div>`;
                });

                html += `</div></div>`;
            });
            document.getElementById('expeditionContainer').innerHTML = html;
        }

        async function startExpedition(locId, monsterId) {
            playAudio('click');
            let res = await fetch('/api/expedition', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ locationId: locId, monsterId: monsterId })
            });
            let data = await res.json();
            gameState = data.state;
            renderUI();
            showCombatModal(data.result);
        }

        function renderArena() {
            let html = '';
            gameState.ArenaLadder.slice(0, 10).forEach(opp => {
                html += `<div class=""monster-row"">
                    <div>
                        <span style=""font-family:'Cinzel',serif; color:var(--text-accent); font-weight:bold;"">#${opp.Rank}</span> - 
                        <strong style=""color:var(--text-primary);"">${opp.Name}</strong> <span style=""font-size:11px; color:var(--text-primary);"">(LVL ${opp.Level})</span>
                    </div>
                    <button class=""btn-roman btn-gold"" onclick=""challengeArena('${opp.Id}')"">Challenge Arena ⚔️</button>
                </div>`;
            });
            document.getElementById('arenaContainer').innerHTML = html;
        }

        async function challengeArena(oppId) {
            playAudio('click');
            let res = await fetch('/api/arena', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ opponentId: oppId })
            });
            let data = await res.json();
            gameState = data.state;
            renderUI();
            showCombatModal(data.result);
        }

        function renderDungeons() {
            let html = '';
            gameState.Dungeons.forEach(dung => {
                html += `<div class=""exp-card"">
                    <h3 style=""color:var(--text-accent); font-family:'Cinzel',serif;"">${dung.Name}</h3>
                    <p style=""font-size:12px; color:var(--text-primary);"">${dung.Description}</p>
                    <div style=""font-size:12px; color:var(--text-accent);"">Current Stage: ${dung.CurrentStage} / ${dung.Stages.length}</div>
                    <button class=""btn-roman btn-gold"" onclick=""enterDungeon(${dung.Id})"">Enter Dungeon Floor ⚔️</button>
                </div>`;
            });
            document.getElementById('dungeonContainer').innerHTML = html;
        }

        async function enterDungeon(dungId) {
            playAudio('click');
            let res = await fetch('/api/dungeon', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ dungeonId: dungId })
            });
            let data = await res.json();
            gameState = data.state;
            renderUI();
            showCombatModal(data.result);
        }

        let currentVendor = 'armorer';
        function renderMerchants() {
            let container = document.getElementById('merchantContainer');
            let html = '';
            let v = gameState.Vendors[currentVendor];
            if (v && v.Items) {
                v.Items.forEach((item, idx) => {
                    html += `<div class=""exp-card"">
                        <div style=""font-weight:bold; color:var(--text-gold);"">${item.Name}</div>
                        <div style=""font-size:12px;"">Price: ${item.Price} Gold</div>
                        <button class=""btn-roman btn-gold"" onclick=""buyItem('${currentVendor}', ${idx})"">Buy (${item.Price} Gold)</button>
                    </div>`;
                });
            }
            container.innerHTML = html;
        }

        function switchVendor(vendorType) {
            playAudio('click');
            currentVendor = vendorType;
            renderMerchants();
        }

        async function buyItem(vendorType, idx) {
            playAudio('click');
            let res = await fetch('/api/buy', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ vendorType: vendorType, itemIndex: idx })
            });
            gameState = await res.json();
            renderUI();
        }

        function renderForge() {
            let stash = document.getElementById('forgeStashInfo');
            stash.innerHTML = `Iron: <strong>${gameState.IronStash}</strong> | Bronze: <strong>${gameState.BronzeStash}</strong> | Ruby: <strong>${gameState.RubyStash}</strong> | Leather: <strong>${gameState.LeatherStash}</strong>`;

            let html = '';
            gameState.Recipes.forEach(rec => {
                html += `<div class=""exp-card"">
                    <h4 style=""color:var(--text-gold);"">${rec.Name}</h4>
                    <div style=""font-size:12px;"">Cost: ${rec.ReqIron} Iron, ${rec.ReqBronze} Bronze, ${rec.ReqRuby} Ruby, ${rec.ReqLeather} Leather</div>
                    <button class=""btn-roman btn-gold"" onclick=""craftRecipe('${rec.Id}')"">Craft Gear 🔨</button>
                </div>`;
            });
            document.getElementById('forgeRecipeContainer').innerHTML = html;
        }

        async function craftRecipe(recId) {
            playAudio('click');
            let res = await fetch('/api/craft', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ recipeId: recId })
            });
            gameState = await res.json();
            renderUI();
        }

        function renderGuild() {
            let container = document.getElementById('guildContent');
            let g = gameState.PlayerGuild;
            if (!g.HasGuild) {
                container.innerHTML = `<div>
                    <h3>Found a Gladiator Guild</h3>
                    <p style=""margin-bottom:10px;"">Found your own ludus to recruit mercenaries and upgrade guild buildings.</p>
                    <button class=""btn-roman btn-gold"" onclick=""createGuild()"">Found Guild (500 Gold)</button>
                </div>`;
            } else {
                let html = `<h3>${g.Name} [${g.Tag}] - Level ${g.Level}</h3>
                <div style=""margin-top:10px;"">Guild Gold Vault: <strong>${g.GoldVault}</strong></div>
                <div class=""monster-list"" style=""margin-top:15px;"">`;
                g.Log.forEach(l => {
                    html += `<div class=""turn-line"">${l}</div>`;
                });
                html += `</div>`;
                container.innerHTML = html;
            }
        }

        async function createGuild() {
            playAudio('click');
            let res = await fetch('/api/guild/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: 'Legio Victrix', tag: 'ROM' })
            });
            gameState = await res.json();
            renderUI();
        }

        function startWork() {
            playAudio('click');
            fetch('/api/work', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ hours: 1 })
            }).then(r => r.json()).then(st => {
                gameState = st;
                renderUI();
                alert('Completed 1 Hour of Villa Work! Earned +110 Gold, +25 XP');
            });
        }

        function renderSettings() {
            // Placeholder for settings binding
        }

        function toggleFullscreen() {
            playAudio('click');
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(() => {});
            } else {
                if (document.exitFullscreen) document.exitFullscreen();
            }
        }

        async function saveGame() {
            playAudio('click');
            await fetch('/api/save', { method: 'POST' });
            alert('Game Saved Successfully!');
        }

        function exportSaveJSON() {
            let dataStr = ""data:text/json;charset=utf-8,"" + encodeURIComponent(JSON.stringify(gameState));
            let downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute(""href"", dataStr);
            downloadAnchor.setAttribute(""download"", ""aeterna_roma_save.json"");
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }

        function promptImportSave() {
            let input = prompt('Paste your exported Save JSON string:');
            if (input) {
                try {
                    let parsed = JSON.parse(input);
                    if (parsed.Player) {
                        gameState = parsed;
                        saveGame();
                        renderUI();
                        alert('Save Game Loaded!');
                    }
                } catch(e) {
                    alert('Invalid Save File Format');
                }
            }
        }

        async function resetGameConfirm() {
            if (confirm('Are you sure you want to reset all gladiator progress? This cannot be undone.')) {
                playAudio('click');
                let res = await fetch('/api/reset', { method: 'POST' });
                gameState = await res.json();
                renderUI();
                alert('Gladiator progress reset!');
            }
        }

        // Initialize on load
        window.addEventListener('load', () => {
            loadState();
        });
    </script>
</body>
</html>";
    }
}
