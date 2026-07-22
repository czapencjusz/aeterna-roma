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
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }

        :root {
            --bg-main: #0c0908;
            --bg-gradient: radial-gradient(circle at 50% 30%, #291c14 0%, #0d0907 80%);
            --bg-card: rgba(26, 17, 10, 0.85);
            --sub-bg: rgba(30, 20, 13, 0.7);
            --bg-header: #1c130d;
            --text-primary: #e5d3b3;
            --text-accent: #ffd700;
            --border-color: #8c6738;
            --panel-header-bg: linear-gradient(90deg, #4a1515 0%, #1a0808 100%);
            --btn-bg: linear-gradient(180deg, #6e1c1c 0%, #3d0c0c 100%);
            --btn-gold-bg: linear-gradient(180deg, #a67c1e 0%, #573e0e 100%);
        }

        body.theme-DarkImperial {
            --bg-main: #0c0908;
            --bg-gradient: radial-gradient(circle at 50% 30%, #291c14 0%, #0d0907 80%);
            --bg-card: rgba(26, 17, 10, 0.85);
            --sub-bg: rgba(30, 20, 13, 0.7);
            --bg-header: #1c130d;
            --text-primary: #e5d3b3;
            --text-accent: #ffd700;
            --border-color: #8c6738;
            --panel-header-bg: linear-gradient(90deg, #4a1515 0%, #1a0808 100%);
            --btn-bg: linear-gradient(180deg, #6e1c1c 0%, #3d0c0c 100%);
            --btn-gold-bg: linear-gradient(180deg, #a67c1e 0%, #573e0e 100%);
        }

        body.theme-RomanParchment {
            --bg-main: #f4ecd8;
            --bg-gradient: radial-gradient(circle at 50% 30%, #ede0c4 0%, #dfd0b0 80%);
            --bg-card: #ede0c4;
            --sub-bg: #e2d2b0;
            --bg-header: #dfd0b0;
            --text-primary: #2c1a0c;
            --text-accent: #8b0000;
            --border-color: #a88556;
            --panel-header-bg: linear-gradient(90deg, #a88556 0%, #6e5230 100%);
            --btn-bg: linear-gradient(180deg, #8b0000 0%, #4a0000 100%);
            --btn-gold-bg: linear-gradient(180deg, #c59b27 0%, #7a5e12 100%);
        }

        body.theme-ColosseumCrimson {
            --bg-main: #140505;
            --bg-gradient: radial-gradient(circle at 50% 30%, #3b0a0a 0%, #140505 80%);
            --bg-card: rgba(35, 10, 10, 0.85);
            --sub-bg: rgba(45, 15, 15, 0.7);
            --bg-header: #280808;
            --text-primary: #f5d6d6;
            --text-accent: #ff4d4d;
            --border-color: #a83232;
            --panel-header-bg: linear-gradient(90deg, #7a1515 0%, #3b0808 100%);
            --btn-bg: linear-gradient(180deg, #a81c1c 0%, #520c0c 100%);
            --btn-gold-bg: linear-gradient(180deg, #d49b27 0%, #7a5712 100%);
        }

        body.theme-LegionEmerald {
            --bg-main: #06140b;
            --bg-gradient: radial-gradient(circle at 50% 30%, #0d381c 0%, #06140b 80%);
            --bg-card: rgba(10, 30, 18, 0.85);
            --sub-bg: rgba(15, 40, 24, 0.7);
            --bg-header: #0a2414;
            --text-primary: #d4f5e0;
            --text-accent: #4dff91;
            --border-color: #2e8b57;
            --panel-header-bg: linear-gradient(90deg, #15522e 0%, #082915 100%);
            --btn-bg: linear-gradient(180deg, #1ca857 0%, #0c522a 100%);
            --btn-gold-bg: linear-gradient(180deg, #b8a027 0%, #695a12 100%);
        }

        body.theme-TyrianPurple {
            --bg-main: #120614;
            --bg-gradient: radial-gradient(circle at 50% 30%, #310c38 0%, #120614 80%);
            --bg-card: rgba(28, 10, 33, 0.85);
            --sub-bg: rgba(38, 15, 45, 0.7);
            --bg-header: #200a26;
            --text-primary: #f1d6f5;
            --text-accent: #e066ff;
            --border-color: #8a2be2;
            --panel-header-bg: linear-gradient(90deg, #5c157a 0%, #2b083b 100%);
            --btn-bg: linear-gradient(180deg, #7b1ca8 0%, #3e0c52 100%);
            --btn-gold-bg: linear-gradient(180deg, #d49b27 0%, #7a5712 100%);
        }

        body {
            background: var(--bg-main);
            background-image: var(--bg-gradient);
            color: var(--text-primary);
            font-family: 'Philosopher', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            transition: background 0.3s ease, color 0.3s ease;
        }

        header {
            background: var(--bg-header);
            border-bottom: 2px solid var(--border-color);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.8);
        }

        .logo {
            font-family: 'Cinzel Decorative', serif;
            font-size: 24px;
            font-weight: 700;
            color: var(--text-accent);
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 2px 10px rgba(255, 215, 0, 0.3);
        }

        .nav-tabs {
            display: flex;
            gap: 6px;
            background: rgba(0,0,0,0.3);
            padding: 4px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }

        .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-primary);
            font-family: 'Cinzel', serif;
            font-size: 13px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .tab-btn:hover {
            background: var(--sub-bg);
            color: var(--text-accent);
        }

        .tab-btn.active {
            background: var(--btn-gold-bg);
            color: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.5);
        }

        .container {
            max-width: 1200px;
            width: 100%;
            margin: 20px auto;
            padding: 0 16px;
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            flex-grow: 1;
        }

        .hero-panel {
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.6);
        }

        .panel-header {
            background: var(--panel-header-bg);
            color: var(--text-accent);
            font-family: 'Cinzel', serif;
            font-weight: bold;
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
            text-align: center;
            font-size: 15px;
            letter-spacing: 1px;
        }

        .stat-bar {
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            height: 18px;
            position: relative;
            overflow: hidden;
            margin-top: 4px;
        }

        .stat-fill {
            height: 100%;
            transition: width 0.3s ease;
        }

        .fill-hp { background: linear-gradient(90deg, #8b0000 0%, #ff3333 100%); }
        .fill-exp { background: linear-gradient(90deg, #1c6e1c 0%, #33ff33 100%); }
        .fill-energy { background: linear-gradient(90deg, #1c4a6e 0%, #3399ff 100%); }

        .stat-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 10px;
            font-weight: bold;
            color: #fff;
            text-shadow: 1px 1px 2px #000;
        }

        .main-content {
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.6);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .btn-roman {
            background: var(--btn-bg);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            font-family: 'Cinzel', serif;
            font-size: 13px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-roman:hover {
            filter: brightness(1.2);
            box-shadow: 0 0 10px rgba(255,215,0,0.3);
        }

        .btn-gold {
            background: var(--btn-gold-bg);
            color: #fff;
        }

        .inv-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 8px;
            background: var(--sub-bg);
            padding: 12px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }

        .inv-slot {
            aspect-ratio: 1;
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            cursor: pointer;
        }

        .inv-slot:hover {
            border-color: var(--text-accent);
        }

        .equip-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .train-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid var(--sub-bg);
        }

        .train-card {
            background: var(--sub-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 8px;
        }

        .exp-card {
            background: var(--sub-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 14px;
            margin-bottom: 12px;
        }

        .monster-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            background: var(--sub-bg);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            margin-top: 6px;
        }

        .shop-item-card {
            background: var(--sub-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .tooltip-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px;
            margin-top: 10px;
        }

        .forge-mats {
            background: var(--sub-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 12px;
        }

        /* Modal styling */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.8);
            display: flex; align-items: center; justify-content: center;
            z-index: 1000;
        }

        .modal-body {
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 24px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
    </style>
</head>
<body class=""theme-DarkImperial"">
    <header>
        <div class=""logo"">⚔️ Aeterna Roma 🏛️</div>
        <div class=""nav-tabs"">
            <button class=""tab-btn active"" onclick=""switchTab('overview')"">Overview</button>
            <button class=""tab-btn"" onclick=""switchTab('training')"">Training</button>
            <button class=""tab-btn"" onclick=""switchTab('expeditions')"">Expeditions</button>
            <button class=""tab-btn"" onclick=""switchTab('arena')"">Colosseum</button>
            <button class=""tab-btn"" onclick=""switchTab('dungeons')"">Dungeons</button>
            <button class=""tab-btn"" onclick=""switchTab('merchants')"">Merchants</button>
            <button class=""tab-btn"" onclick=""switchTab('forge')"">Forge</button>
            <button class=""tab-btn"" onclick=""switchTab('work')"">Villa Work</button>
            <button class=""tab-btn"" onclick=""switchTab('guild')"">Guild</button>
            <button class=""tab-btn"" onclick=""switchTab('settings')"">Settings</button>
        </div>
    </header>

    <div class=""container"">
        <!-- Hero Sidebar -->
        <div class=""hero-panel"">
            <div class=""panel-header"" id=""heroNameTitle"">Maximus - Novice</div>
            <div>
                <div style=""display:flex; justify-content:space-between; font-size:12px;""><span>Health:</span><span id=""hpVal"">100/100</span></div>
                <div class=""stat-bar""><div id=""hpBar"" class=""stat-fill fill-hp"" style=""width:100%;""></div><div class=""stat-text"" id=""hpText"">100%</div></div>
            </div>
            <div>
                <div style=""display:flex; justify-content:space-between; font-size:12px;""><span>Exp:</span><span id=""xpVal"">0/100</span></div>
                <div class=""stat-bar""><div id=""xpBar"" class=""stat-fill fill-exp"" style=""width:0%;""></div><div class=""stat-text"" id=""xpText"">0%</div></div>
            </div>
            <div>
                <div style=""display:flex; justify-content:space-between; font-size:12px;""><span>Energy:</span><span id=""energyVal"">20/20</span></div>
                <div class=""stat-bar""><div id=""energyBar"" class=""stat-fill fill-energy"" style=""width:100%;""></div><div class=""stat-text"" id=""energyText"">100%</div></div>
            </div>
            <div style=""display:flex; justify-content:space-around; font-weight:bold; font-size:14px; color:var(--text-accent);"">
                <div>Gold: 💰 <span id=""goldVal"">0</span></div>
                <div>Rubies: 💎 <span id=""rubyVal"">0</span></div>
            </div>
            <div class=""panel-header"">Equipment</div>
            <div class=""equip-grid"" id=""equipGrid"">
                <!-- Equipment Slots -->
            </div>
        </div>

        <!-- Main Content Panel -->
        <div class=""main-content"">
            <!-- Overview Tab -->
            <div id=""tab-overview"" class=""tab-content active"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Gladiator Overview</h2>
                <div style=""display:grid; grid-template-columns:1fr 1fr; gap:20px;"">
                    <div>
                        <h3 style=""color:var(--text-primary); border-bottom:1px solid var(--border-color); padding-bottom:4px; margin-bottom:10px;"">Base Attributes</h3>
                        <div id=""attributesList""></div>
                    </div>
                    <div>
                        <h3 style=""color:var(--text-primary); border-bottom:1px solid var(--border-color); padding-bottom:4px; margin-bottom:10px;"">Backpack Inventory</h3>
                        <div class=""inv-grid"" id=""inventoryGrid""></div>
                        <div class=""tooltip-card"" id=""itemInspector"" style=""display:none;"">
                            <strong id=""inspectName"" style=""color:var(--text-accent);"">Item Name</strong>
                            <p id=""inspectStats"" style=""font-size:12px; margin:6px 0;""></p>
                            <button id=""inspectActionBtn"" class=""btn-roman btn-gold"" onclick=""actionInspectItem()"">Equip</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Training Tab -->
            <div id=""tab-training"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Ludus Training Ground</h2>
                <p style=""font-size:13px; margin-bottom:16px;"">Train your Gladiator's core attributes to enhance damage, armor, and combat accuracy.</p>
                <div id=""trainingContainer""></div>
            </div>

            <!-- Expeditions Tab -->
            <div id=""tab-expeditions"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Wilderness Expeditions</h2>
                <div id=""expeditionContainer""></div>
            </div>

            <!-- Colosseum Arena Tab -->
            <div id=""tab-arena"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Roman Colosseum Arena</h2>
                <p style=""font-size:13px; margin-bottom:16px;"">Challenge top gladiators to gain Honor, Gold, and improve your Arena Rank.</p>
                <div id=""arenaContainer""></div>
            </div>

            <!-- Dungeons Tab -->
            <div id=""tab-dungeons"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Ancient Catacombs & Dungeons</h2>
                <div id=""dungeonsContainer""></div>
            </div>

            <!-- Merchants Tab -->
            <div id=""tab-merchants"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Roman Forum Merchants</h2>
                <div style=""display:flex; gap:10px; margin-bottom:16px;"">
                    <select id=""vendorSelect"" onchange=""renderMerchants()"" class=""btn-roman"" style=""background:var(--sub-bg); border-color:var(--border-color); color:var(--text-primary);"">
                        <option value=""Weaponsmith"">Weaponsmith Marcus</option>
                        <option value=""Armorer"">Armorer Flavius</option>
                        <option value=""General"">General Merchant Gaius</option>
                        <option value=""Alchemist"">Apothecary Cornelia</option>
                    </select>
                </div>
                <div id=""shopContainer"" style=""display:grid; grid-template-columns:repeat(3,1fr); gap:12px;""></div>
            </div>

            <!-- Forge Tab -->
            <div id=""tab-forge"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Vulcan's Forge & Smelter</h2>
                <div class=""forge-mats"" id=""forgeMatsDisplay""></div>
                <h3 style=""color:var(--text-primary); margin-bottom:8px;"">Known Crafting Recipes</h3>
                <div id=""recipesContainer"" style=""display:grid; grid-template-columns:repeat(2,1fr); gap:12px;""></div>
            </div>

            <!-- Work Tab -->
            <div id=""tab-work"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Patrician Villa Work</h2>
                <p style=""font-size:13px; margin-bottom:16px;"">Serve Roman Patricians to earn Gold and Experience.</p>
                <div style=""display:flex; gap:10px; align-items:center;"">
                    <label>Duration (Hours): </label>
                    <input type=""number"" id=""workHours"" min=""1"" max=""8"" value=""1"" class=""btn-roman"" style=""width:60px; background:var(--sub-bg); color:var(--text-primary);"">
                    <button class=""btn-roman btn-gold"" onclick=""startWork()"">Work 🔨</button>
                </div>
            </div>

            <!-- Guild Tab -->
            <div id=""tab-guild"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Gladiator Guild</h2>
                <div id=""guildContainer""></div>
            </div>

            <!-- Settings Tab -->
            <div id=""tab-settings"" class=""tab-content"">
                <h2 style=""color:var(--text-accent); font-family:'Cinzel',serif; margin-bottom:12px;"">Game Settings</h2>
                <div style=""display:flex; flex-direction:column; gap:16px; max-width:400px;"">
                    <div>
                        <label>Visual Theme Mode:</label>
                        <select id=""themeSelect"" onchange=""changeTheme(this.value)"" class=""btn-roman"" style=""width:100%; margin-top:4px; background:var(--sub-bg); color:var(--text-primary);"">
                            <option value=""DarkImperial"">Dark Imperial (Default)</option>
                            <option value=""RomanParchment"">Roman Parchment</option>
                            <option value=""ColosseumCrimson"">Colosseum Crimson</option>
                            <option value=""LegionEmerald"">Legion Emerald</option>
                            <option value=""TyrianPurple"">Tyrian Purple</option>
                        </select>
                    </div>
                    <div>
                        <button class=""btn-roman btn-gold"" onclick=""resetSaveData()"">Reset Game Save ⚠️</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Combat Modal -->
    <div id=""combatModal"" class=""modal-overlay"" style=""display:none;"">
        <div class=""modal-body"">
            <h3 id=""modalCombatTitle"" style=""color:var(--text-accent); font-family:'Cinzel',serif; border-bottom:1px solid var(--border-color); padding-bottom:8px; margin-bottom:12px;"">Combat Report</h3>
            <div id=""modalCombatLog"" style=""font-size:12px; font-family:monospace; height:240px; overflow-y:auto; background:rgba(0,0,0,0.5); padding:10px; border-radius:4px; border:1px solid var(--border-color);""></div>
            <div style=""margin-top:16px; text-align:right;"">
                <button class=""btn-roman btn-gold"" onclick=""closeCombatModal()"">Close Report</button>
            </div>
        </div>
    </div>

    <script>
        let gameState = null;
        let selectedInspectIdx = -1;
        let selectedInspectType = 'inventory';

        async function fetchState() {
            let res = await fetch('/api/state');
            gameState = await res.json();
            if (gameState.Settings && gameState.Settings.ThemeMode) {
                document.body.className = 'theme-' + gameState.Settings.ThemeMode;
                document.getElementById('themeSelect').value = gameState.Settings.ThemeMode;
            }
            renderUI();
        }

        function playAudio(type) {
            // Web Audio sound synthesizer for retro RPG clicks & hits
            try {
                let ctx = new (window.AudioContext || window.webkitAudioContext)();
                let osc = ctx.createOscillator();
                let gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                if (type === 'click') {
                    osc.frequency.setValueAtTime(440, ctx.currentTime);
                    gain.gain.setValueAtTime(0.1, ctx.currentTime);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.05);
                }
            } catch(e){}
        }

        function switchTab(tabId) {
            playAudio('click');
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById('tab-' + tabId).classList.add('active');

            if (tabId === 'merchants') renderMerchants();
            if (tabId === 'forge') renderForge();
            if (tabId === 'guild') renderGuild();
            if (tabId === 'arena') renderArena();
            if (tabId === 'expeditions') renderExpeditions();
            if (tabId === 'training') renderTraining();
            if (tabId === 'dungeons') renderDungeons();
        }

        function renderUI() {
            if (!gameState) return;
            let glad = gameState.Player;

            document.getElementById('heroNameTitle').innerText = glad.Name + ' - ' + glad.Title;
            document.getElementById('hpVal').innerText = glad.CurrentHP + '/' + glad.MaxHP;
            document.getElementById('hpBar').style.width = Math.min(100, Math.max(0, (glad.CurrentHP / glad.MaxHP) * 100)) + '%';
            document.getElementById('hpText').innerText = Math.round((glad.CurrentHP / glad.MaxHP) * 100) + '%';

            document.getElementById('xpVal').innerText = glad.XP + '/' + glad.MaxXP;
            document.getElementById('xpBar').style.width = Math.min(100, Math.max(0, (glad.XP / glad.MaxXP) * 100)) + '%';
            document.getElementById('xpText').innerText = Math.round((glad.XP / glad.MaxXP) * 100) + '%';

            document.getElementById('energyVal').innerText = glad.CurrentEnergy + '/' + glad.MaxEnergy;
            document.getElementById('energyBar').style.width = Math.min(100, Math.max(0, (glad.CurrentEnergy / glad.MaxEnergy) * 100)) + '%';
            document.getElementById('energyText').innerText = Math.round((glad.CurrentEnergy / glad.MaxEnergy) * 100) + '%';

            document.getElementById('goldVal').innerText = glad.Gold;
            document.getElementById('rubyVal').innerText = glad.Rubies;

            renderEquipment();
            renderAttributes();
            renderInventory();
        }

        function renderEquipment() {
            let slots = ['Head', 'Chest', 'Weapon', 'Shield', 'Ring', 'Amulet', 'Gloves', 'Shoes'];
            let html = '';
            slots.forEach(slot => {
                let item = gameState.Player.Equipment[slot];
                html += `<div class=""inv-slot"" onclick=""inspectEquipItem('${slot}')"">
                    <span style=""font-size:10px; position:absolute; top:2px; left:2px; opacity:0.6;"">${slot}</span>
                    ${item ? `<strong style=""font-size:11px; color:var(--text-accent);"">${item.Name}</strong>` : ''}
                </div>`;
            });
            document.getElementById('equipGrid').innerHTML = html;
        }

        function renderAttributes() {
            let glad = gameState.Player;
            let attrs = [
                { name: 'Strength', val: glad.BaseStrength, bonus: glad.Equipment ? getBonus('Strength') : 0 },
                { name: 'Dexterity', val: glad.BaseDexterity, bonus: glad.Equipment ? getBonus('Dexterity') : 0 },
                { name: 'Agility', val: glad.BaseAgility, bonus: glad.Equipment ? getBonus('Agility') : 0 },
                { name: 'Constitution', val: glad.BaseConstitution, bonus: glad.Equipment ? getBonus('Constitution') : 0 },
                { name: 'Charisma', val: glad.BaseCharisma, bonus: glad.Equipment ? getBonus('Charisma') : 0 },
                { name: 'Intelligence', val: glad.BaseIntelligence, bonus: glad.Equipment ? getBonus('Intelligence') : 0 }
            ];
            let html = '';
            attrs.forEach(a => {
                html += `<div class=""train-row"">
                    <span>${a.name}</span>
                    <strong style=""color:var(--text-accent);"">${a.val} ${a.bonus > 0 ? '(+' + a.bonus + ')' : ''}</strong>
                </div>`;
            });
            document.getElementById('attributesList').innerHTML = html;
        }

        function getBonus(stat) {
            let bonus = 0;
            let eq = gameState.Player.Equipment;
            for (let k in eq) {
                if (eq[k] && eq[k][stat]) bonus += eq[k][stat];
            }
            return bonus;
        }

        function renderInventory() {
            let html = '';
            let inv = gameState.Player.Inventory;
            for (let i = 0; i < gameState.Player.InventoryCapacity; i++) {
                let item = inv[i];
                html += `<div class=""inv-slot"" onclick=""inspectInvItem(${i})"">
                    ${item ? `<span style=""font-size:11px; text-align:center; color:var(--text-primary);"">${item.Name}</span>` : ''}
                </div>`;
            }
            document.getElementById('inventoryGrid').innerHTML = html;
        }

        function inspectInvItem(idx) {
            let item = gameState.Player.Inventory[idx];
            if (!item) return;
            selectedInspectIdx = idx;
            selectedInspectType = 'inventory';

            document.getElementById('inspectName').innerText = item.Name;
            document.getElementById('inspectStats').innerText = `Type: ${item.Type} | Price: ${item.Price}g`;
            document.getElementById('inspectActionBtn').innerText = 'Equip / Use';
            document.getElementById('inspectActionBtn').onclick = () => equipItem(idx);
            document.getElementById('itemInspector').style.display = 'block';
        }

        function inspectEquipItem(slot) {
            let item = gameState.Player.Equipment[slot];
            if (!item) return;

            document.getElementById('inspectName').innerText = item.Name;
            document.getElementById('inspectStats').innerText = `Slot: ${slot} | Armor/Dmg: ${item.Armor || item.MinDamage || 0}`;
            document.getElementById('inspectActionBtn').innerText = 'Unequip';
            document.getElementById('inspectActionBtn').onclick = () => unequipItem(slot);
            document.getElementById('itemInspector').style.display = 'block';
        }

        async function equipItem(idx) {
            playAudio('click');
            let res = await fetch('/api/equip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ inventoryIndex: idx })
            });
            gameState = await res.json();
            document.getElementById('itemInspector').style.display = 'none';
            renderUI();
        }

        async function unequipItem(slot) {
            playAudio('click');
            let res = await fetch('/api/unequip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ slot: slot })
            });
            gameState = await res.json();
            document.getElementById('itemInspector').style.display = 'none';
            renderUI();
        }

        function renderTraining() {
            let glad = gameState.Player;
            let attrs = ['Strength', 'Dexterity', 'Agility', 'Constitution', 'Charisma', 'Intelligence'];
            let html = '';
            attrs.forEach(attr => {
                let baseVal = glad['Base' + attr];
                let cost = Math.floor(baseVal * baseVal * 2.5) + 15;
                html += `<div class=""train-card"">
                    <div style=""display:flex; justify-content:space-between; align-items:center;"">
                        <div>
                            <strong style=""color:var(--text-accent);"">${attr}</strong> - Current Base: ${baseVal}
                        </div>
                        <button class=""btn-roman btn-gold"" onclick=""trainAttribute('${attr}')"">Train (${cost}g)</button>
                    </div>
                </div>`;
            });
            document.getElementById('trainingContainer').innerHTML = html;
        }

        async function trainAttribute(attrName) {
            playAudio('click');
            let res = await fetch('/api/train', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ attribute: attrName })
            });
            gameState = await res.json();
            renderUI();
            renderTraining();
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

        function renderMerchants() {
            let vendorType = document.getElementById('vendorSelect').value;
            let vendor = gameState.Vendors[vendorType];
            let html = '';
            if (vendor && vendor.Items) {
                vendor.Items.forEach((item, idx) => {
                    html += `<div class=""shop-item-card"">
                        <strong style=""color:var(--text-accent);"">${item.Name}</strong>
                        <p style=""font-size:11px; margin:4px 0;"">Price: ${item.Price}g</p>
                        <button class=""btn-roman btn-gold"" onclick=""buyItem('${vendorType}', ${idx})"">Buy Item 💰</button>
                    </div>`;
                });
            }
            document.getElementById('shopContainer').innerHTML = html;
        }

        async function buyItem(vType, idx) {
            playAudio('click');
            let res = await fetch('/api/buy', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ vendorType: vType, itemIndex: idx })
            });
            gameState = await res.json();
            renderUI();
            renderMerchants();
        }

        function renderForge() {
            let mats = `Iron: ${gameState.IronStash} | Bronze: ${gameState.BronzeStash} | Rubies: ${gameState.RubyStash} | Leather: ${gameState.LeatherStash}`;
            document.getElementById('forgeMatsDisplay').innerText = mats;

            let html = '';
            gameState.Recipes.forEach(r => {
                html += `<div class=""shop-item-card"">
                    <strong style=""color:var(--text-accent);"">${r.Name}</strong>
                    <p style=""font-size:11px; margin:4px 0;"">Requires: ${r.ReqIron} Iron, ${r.ReqBronze} Bronze</p>
                    <button class=""btn-roman btn-gold"" onclick=""craftRecipe('${r.Id}')"">Craft Weapon 🛠️</button>
                </div>`;
            });
            document.getElementById('recipesContainer').innerHTML = html;
        }

        async function craftRecipe(rId) {
            playAudio('click');
            let res = await fetch('/api/forge/craft', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ recipeId: rId })
            });
            gameState = await res.json();
            renderUI();
            renderForge();
        }

        function renderDungeons() {
            let html = '';
            gameState.Dungeons.forEach(d => {
                html += `<div class=""exp-card"">
                    <h3 style=""color:var(--text-accent);"">${d.Name}</h3>
                    <p style=""font-size:12px;"">${d.Description}</p>
                    <p style=""font-size:12px; color:var(--text-accent);"">Stage: ${d.CurrentStage}/${d.Stages.length} | Status: ${d.IsCompleted ? 'Completed' : 'Active'}</p>
                    ${!d.IsCompleted ? `<button class=""btn-roman btn-gold"" onclick=""enterDungeon(${d.Id})"" style=""margin-top:8px;"">Enter Stage ${d.CurrentStage} ⚔️</button>` : ''}
                </div>`;
            });
            document.getElementById('dungeonsContainer').innerHTML = html;
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

        async function startWork() {
            let h = document.getElementById('workHours').value;
            let res = await fetch('/api/work/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ hours: h })
            });
            gameState = await res.json();
            renderUI();
            alert('Work completed! Earned Gold and Experience.');
        }

        function renderGuild() {
            let g = gameState.PlayerGuild;
            let html = '';
            if (g && g.HasGuild) {
                html = `<div>
                    <h3>Guild: ${g.Name} [${g.Tag}]</h3>
                    <p>Level: ${g.Level} | Vault: ${g.GoldVault}g</p>
                </div>`;
            } else {
                html = `<div>
                    <p>You are not currently in a Guild.</p>
                    <div style=""display:flex; gap:8px; margin-top:10px;"">
                        <input type=""text"" id=""guildName"" placeholder=""Guild Name"" class=""btn-roman"" style=""background:var(--sub-bg); color:var(--text-primary);"">
                        <input type=""text"" id=""guildTag"" placeholder=""TAG"" style=""width:60px; background:var(--sub-bg); color:var(--text-primary);"" class=""btn-roman"">
                        <button class=""btn-roman btn-gold"" onclick=""createGuild()"">Create Guild (500g)</button>
                    </div>
                </div>`;
            }
            document.getElementById('guildContainer').innerHTML = html;
        }

        async function createGuild() {
            let name = document.getElementById('guildName').value;
            let tag = document.getElementById('guildTag').value;
            let res = await fetch('/api/guild/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: name, tag: tag })
            });
            gameState = await res.json();
            renderUI();
            renderGuild();
        }

        async function changeTheme(themeName) {
            document.body.className = 'theme-' + themeName;
            await fetch('/api/settings/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ themeMode: themeName })
            });
        }

        async function resetSaveData() {
            if (confirm('Are you sure you want to reset all character progress?')) {
                let res = await fetch('/api/reset');
                gameState = await res.json();
                renderUI();
                alert('Save data reset successfully.');
            }
        }

        function showCombatModal(result) {
            document.getElementById('modalCombatTitle').innerText = (result.IsVictory ? '🏆 VICTORY - ' : '💀 DEFEAT - ') + result.WinnerName;
            let logHtml = result.Turns.map(t => `<div style=""color:${t.AttackerIsPlayer ? '#4dff91' : '#ff4d4d'};"">Turn ${t.TurnNumber}: ${t.Message}</div>`).join('');
            document.getElementById('modalCombatLog').innerHTML = logHtml;
            document.getElementById('combatModal').style.display = 'flex';
        }

        function closeCombatModal() {
            document.getElementById('combatModal').style.display = 'none';
        }

        window.onload = fetchState;
    </script>
</body>
</html>";
    }
}
