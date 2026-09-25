// End-to-end test of the game window's interface.
//
// Loads aeterna/ui/index.html in Chromium and replaces pywebview's bridge with one that
// forwards every window.pywebview.api call to the real Python game (tests/e2e/bridge.py).
//
// Requirements: Node.js and Playwright (npm install playwright), plus Python 3.
// Run from the repository root:   node tests/e2e/ui_test.js [screenshot-dir]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const readline = require('readline');
const path = require('path');
const fs = require('fs');
const os = require('os');

const ROOT = path.resolve(__dirname, '..', '..');
const PAGE = 'file://' + path.join(ROOT, 'aeterna', 'ui', 'index.html');
const SHOTS = process.argv[2] || null;
let failures = 0;
function check(cond, msg) { console.log((cond ? 'PASS ' : 'FAIL ') + msg); if (!cond) failures++; }

// --- Python bridge -------------------------------------------------------------------------
const py = spawn(process.env.PYTHON || 'python3', [path.join(__dirname, 'bridge.py')], { stdio: ['pipe', 'pipe', 'inherit'] });
const pending = new Map();
let nextId = 1;
readline.createInterface({ input: py.stdout }).on('line', line => {
    const msg = JSON.parse(line);
    const p = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) p.reject(new Error(msg.error)); else p.resolve(msg.result);
});
function pyCall(method, args) {
    return new Promise((resolve, reject) => {
        const id = nextId++;
        pending.set(id, { resolve, reject });
        py.stdin.write(JSON.stringify({ id, method, args }) + '\n');
    });
}

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
    const errors = [];
    page.on('pageerror', e => errors.push('pageerror: ' + e.message));
    page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_/.test(m.text())) errors.push('console: ' + m.text()); });
    const dialogAnswers = [];
    page.on('dialog', d => { const a = dialogAnswers.shift(); if (a === false) d.dismiss(); else d.accept(a === true || a === undefined ? undefined : a); });

    // Stand-in for pywebview: window.pywebview.api.<method>(...) -> Python.
    await page.exposeFunction('__py', (method, args) => pyCall(method, args));
    await page.addInitScript(() => {
        window.pywebview = { api: new Proxy({}, { get: (_, method) => (...args) => window.__py(method, args) }) };
        window.addEventListener('DOMContentLoaded', () => setTimeout(() => window.dispatchEvent(new Event('pywebviewready')), 50));
    });

    const set = (p, v) => pyCall('test_set', [p, v]);
    const get = p => pyCall('test_get', [p]);
    const refresh = () => page.evaluate(() => call('get_view'));
    const text = sel => page.textContent(sel);
    // Drags with the mouse from the centre of `fromSel` to the point (x, y) or the centre of `toSel`.
    const dragTo = async (fromSel, to) => {
        const a = await page.locator(fromSel).boundingBox();
        await page.mouse.move(a.x + a.width / 2, a.y + a.height / 2);
        await page.mouse.down();
        await page.mouse.move(a.x + a.width / 2 + 8, a.y + a.height / 2 + 8, { steps: 3 });
        let x = to.x, y = to.y;
        if (to.sel) { const b = await page.locator(to.sel).boundingBox(); x = b.x + b.width / 2; y = b.y + b.height / 2; }
        await page.mouse.move(x, y, { steps: 8 });
        await page.mouse.up();
    };
    // The screen point at the centre of bag cell (cx, cy) for an item of w x h cells grabbed in its middle.
    const bagPoint = async (sel, cx, cy, w, h) => {
        const b = await page.locator(sel).boundingBox();
        return { x: b.x + 1 + (cx + w / 2) * 46, y: b.y + 1 + (cy + h / 2) * 46 };
    };
    const shot = async name => { if (SHOTS) await page.screenshot({ path: path.join(SHOTS, name) }); };

    await page.goto(PAGE);
    await page.waitForFunction(() => view !== null);
    await set(['Settings', 'CombatSpeed'], 'Instant');
    await refresh();

    check(await text('#gladName') === 'Flavius', 'new game renders the gladiator');
    check(await text('#statDmg') === '8 - 16', 'sidebar damage comes from Python');
    check((await page.$$('#brandLogo svg')).length === 1, 'logo art renders');

    for (const tab of ['training', 'expeditions', 'arena', 'dungeons', 'labors', 'quests', 'merchants', 'forge', 'work', 'guild', 'settings', 'overview']) {
        await page.click(`.nav-tab[data-tab="${tab}"]`);
        check(await page.isVisible(`#tab-${tab}`), `tab ${tab} opens`);
    }
    await page.click('#ovSubtabBtnHidden');
    check((await page.$$('#hiddenStatsGrid .monster-row')).length === 11, 'hidden stats render');
    await page.click('#ovSubtabBtnChronicle');
    check((await page.$$('#chronicleGrid .monster-row')).length === 16, 'chronicle renders');
    await page.click('#ovSubtabBtnSets');
    check((await page.$$('#setsGrid .exp-card')).length === 6, 'gear sets render');
    await page.click('#ovSubtabBtnBestiary');
    check((await page.$$('#bestiaryGrid .beast-card.unknown')).length === 64, 'bestiary starts with every foe unknown');
    await page.click('#ovSubtabBtnLaurels');
    check((await page.$$('#laurelsGrid .ach-card')).length === 28 && (await page.$$('#laurelsGrid .ach-card.done')).length === 0, 'laurels render');
    await page.click('#ovSubtabBtnBase');

    // Merchants
    await page.click('.nav-tab[data-tab="merchants"]');
    const vendorCounts = [];
    for (const label of ['Weaponsmith', 'Armorer', 'General', 'Apothecary']) {
        await page.click(`#vendorButtons button:has-text("${label}")`);
        vendorCounts.push((await page.$$('#merchantContainer .exp-card')).length);
    }
    check(vendorCounts.join() === '6,6,6,7', 'all four merchants show stock ' + vendorCounts);
    await page.click('#merchantContainer .exp-card:nth-child(1) button');
    await page.waitForFunction(() => view.state.Player.Inventory.length === 2);
    check(await text('#resGold') === '235', 'buying a potion goes through Python');
    await page.click('#vendorButtons button:has-text("Apothecary")');
    await dragTo('#merchantContainer .exp-card:nth-child(1)', await bagPoint('#shopBag', 7, 8, 1, 1));
    await page.waitForFunction(() => view.state.Player.Inventory.some(i => i.Pos && i.Pos[0] === 7 && i.Pos[1] === 8));
    check(await text('#resGold') === '220', 'dragging wares into the bag buys them at that spot');
    const potionAt = (await get(['Player', 'Inventory'])).findIndex(i => i.Pos && i.Pos[0] === 7 && i.Pos[1] === 8);
    await dragTo(`#shopBag .inv-slot:nth-child(${potionAt + 1})`, { sel: '#merchantContainer' });
    await page.waitForFunction(() => view.state.Player.Inventory.length === 2);
    check(await text('#resGold') === '227', "dragging an item onto the merchant's stall sells it");

    // Expedition -> combat report
    await page.click('.nav-tab[data-tab="expeditions"]');
    await page.click('#expeditionContainer .exp-card:nth-child(1) .monster-row:nth-child(2) button');
    await page.waitForSelector('#combatModal.open');
    check((await page.$$('#modalCombatLog .turn-line')).length > 0, 'combat report shows the fight log');
    check((await page.$$('#modalPortrait2 svg')).length === 1, 'enemy portrait shown');
    await shot('combat.png');
    await page.keyboard.press('Escape');
    check(!(await page.isVisible('#combatModal.open')), 'Escape closes the report');
    check((await text('#textEnergy')) === '23/24', 'expedition energy cost shown');
    check(await page.isDisabled('#expeditionContainer .exp-card:nth-child(3) button'), 'locked region buttons disabled');
    check((await page.$$('#expeditionContainer .exp-card')).length === 12, 'all twelve regions listed');
    check((await page.$$('#expeditionContainer .exp-card:nth-child(1) .threat')).length === 3, 'open regions show a threat rating per foe');
    check((await page.$$('#expeditionContainer .exp-card:nth-child(3) .threat')).length === 0, 'locked regions show no threat rating');
    await page.click('.nav-tab[data-tab="overview"]');
    await page.click('#ovSubtabBtnBestiary');
    check((await page.$$('#bestiaryGrid .beast-card:not(.unknown)')).length === (await get(['Stats', 'FightsWon'])), 'a won fight adds a bestiary entry');
    await page.click('#ovSubtabBtnLaurels');
    check((await get(['Stats', 'FightsWon'])) === 0 || (await page.$$('#laurelsGrid .ach-card.done')).length === 1, 'first victory earns a laurel');
    await page.click('#ovSubtabBtnBase');
    await page.click('.nav-tab[data-tab="dungeons"]');
    check(/Energy per floor: 2/.test(await text('#dungeonContainer .exp-card:nth-child(1)')), 'dungeon energy cost comes from Python');
    check(/Crown of Cassius/.test(await text('#dungeonContainer')), 'dungeon boss treasures are shown');

    // Arena
    await set(['Player', 'CurrentHP'], 999);
    await page.click('.nav-tab[data-tab="arena"]');
    await refresh();
    check((await page.$$('#arenaContainer .monster-row')).length === 21, 'arena ladder: 20 rivals + player');
    await page.click('#arenaContainer .monster-row:last-child button');
    await page.waitForSelector('#combatModal.open');
    await page.click('#combatModal .modal-header button:has-text("✕")');
    check(await page.isDisabled('#arenaContainer .monster-row:last-child button'), 'arena cooldown disables challenges');
    await set(['Player', 'Rubies'], 5);
    await refresh();
    await page.waitForTimeout(1100); // let the 1-second timer run at least once
    await page.click('#btnSkipArena');
    await page.waitForFunction(() => view.arena.cooldownUntil === 0);
    check(await get(['Player', 'Rubies']) === 4, 'ruby skip button works while timers tick');

    // Battle series, with a level-up on the way
    await set(['Player', 'CurrentHP'], 999);
    await set(['Player', 'CurrentEnergy'], 24);
    await set(['Player', 'XP'], (await get(['Player', 'MaxXP'])) - 1);
    await refresh();
    await page.click('.nav-tab[data-tab="expeditions"]');
    await page.selectOption('#seriesSize', '3');
    await page.click('#expeditionContainer .exp-card:nth-child(1) .monster-row:nth-child(2) .btn-series');
    await page.waitForSelector('#combatModal.open');
    const seriesLines = (await page.$$('#modalCombatLog .series-line')).length;
    check(seriesLines >= 1 && seriesLines <= 3 && /VICTORIES/.test(await text('#modalCombatResultBanner')), 'battle series shows one line per fight');
    check(await page.isVisible('.levelup-burst'), 'a level-up is celebrated in the report');
    await shot('series.png');
    await page.keyboard.press(' ');
    check(!(await page.isVisible('#combatModal.open')), 'Space closes a finished report');
    check(await get(['Player', 'Level']) === 2, 'series XP levels the gladiator up');

    // Keyboard shortcuts
    await page.keyboard.press('2');
    check(await page.isVisible('#tab-training'), 'number keys switch tabs');
    await page.keyboard.press('1');

    // Imperial Decree
    await page.click('.nav-tab[data-tab="quests"]');
    check(/Daily gift ready/.test(await text('#sidebarDaily')), 'sidebar announces the daily gift');
    const goldBeforeDaily = await get(['Player', 'Gold']);
    await page.click('#dailyContainer button:has-text("Claim Day 1")');
    await page.waitForFunction(() => view.state.Daily.Streak === 1);
    check((await get(['Player', 'Gold'])) > goldBeforeDaily && (await text('#sidebarDaily')) === '', 'claiming the decree pays out once');
    check((await page.$$('#dailyContainer .daily-day.claimed')).length === 1, 'claimed day is marked');

    // Labors of Hercules
    await set(['Player', 'Level'], 6);
    await set(['Player', 'BaseStrength'], 300);
    await set(['Player', 'BaseConstitution'], 300);
    await set(['Player', 'CurrentHP'], 99999);
    await set(['Player', 'CurrentEnergy'], 24);
    await refresh();
    await page.click('.nav-tab[data-tab="labors"]');
    check((await page.$$('#laborsContainer .labor-card')).length === 12, 'twelve labors listed');
    check((await page.$$('#laborsContainer .labor-card button')).length === 1, 'only the next labor can be attempted');
    await page.click('#laborsContainer .labor-card:nth-child(1) button');
    await page.waitForSelector('#combatModal.open');
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => view.state.Player.Labors.length === 1);
    check((await page.$$('#laborsProgress .labor-pip.done')).length === 1 && /Permanent|Completed/.test(await text('#laborsContainer .labor-card:nth-child(1)')), 'a completed labor is marked');
    await shot('labors.png');
    await set(['Player', 'BaseStrength'], 5);
    await set(['Player', 'BaseConstitution'], 5);
    await set(['Player', 'CurrentHP'], 999);
    await refresh();

    // Honor exchange
    await set(['Player', 'Honor'], 1000);
    await refresh();
    await page.click('.nav-tab[data-tab="arena"]');
    await page.waitForFunction(() => view.state.Player.Honor === 1000);
    check((await page.$$('#honorShopContainer .exp-card')).length === 4, 'honor exchange renders');
    const capBefore = await get(['Player', 'InventoryCapacity']);
    await page.click('#honorShopContainer .exp-card:nth-child(1) button');
    await page.waitForFunction(cap => view.state.Player.InventoryCapacity === cap + 4 && document.getElementById('resHonor').textContent === '850', capBefore);
    check(true, 'honor purchase goes through Python');

    // Temple blessing
    await set(['Player', 'Gold'], 1000);
    await refresh();
    await page.waitForFunction(() => view.state.Player.Gold === 1000);
    await page.click('.nav-tab[data-tab="quests"]');
    check((await page.$$('#templeContainer .exp-card')).length === 5, 'temple blessings render');
    await page.click('#templeContainer .exp-card:nth-child(1) button');
    await page.waitForFunction(() => view.state.Blessing && view.state.Blessing.Key === 'mars');
    check(/Blessing of Mars · 5 fights/.test(await text('#sidebarBlessing')), 'active blessing shown in the sidebar');

    // Mythic treasure details
    await pyCall('test_add_unique', ['Lich Lord Cassius', 1]);
    await refresh();
    await page.click('.nav-tab[data-tab="overview"]');
    const mythicIndex = (await get(['Player', 'Inventory'])).length - 1;
    await page.click(`#inventoryContainer .inv-slot:nth-child(${mythicIndex + 1})`);
    check(/Heal 5% of the damage you deal/.test(await text('#selectedItemPanel')), 'mythic effects listed in item details');
    check((await page.$$('#inventoryContainer .rarity-Mythic')).length === 1, 'mythic rarity styled');
    await shot('mythic.png');
    dialogAnswers.push(true);
    await page.click('#selectedItemPanel button:has-text("Sell")');
    await page.waitForFunction(n => view.state.Player.Inventory.length === n, mythicIndex);

    // Inventory: select, compare, equip, sell
    await pyCall('test_add_item', [1, 'Helmet', 'Rare']);
    await refresh();
    await page.click('.nav-tab[data-tab="overview"]');
    const helmIndex = (await get(['Player', 'Inventory'])).length - 1;
    await page.click(`#inventoryContainer .inv-slot:nth-child(${helmIndex + 1})`);
    check(/Head slot is empty/.test(await text('#selectedItemPanel')), 'item panel compares with equipped gear');
    await dragTo(`#inventoryContainer .inv-slot:nth-child(${helmIndex + 1})`, { sel: '#slot-Head' });
    await page.waitForFunction(() => view.state.Player.Equipment.Head !== null);
    check(!(await page.$('#slot-Head.empty')), 'dragging a helmet onto the doll equips it');
    await dragTo('#slot-Head', await bagPoint('#inventoryContainer', 6, 7, 2, 2));
    await page.waitForFunction(() => view.state.Player.Equipment.Head === null);
    const helm = (await get(['Player', 'Inventory'])).find(i => i.Type === 'Helmet');
    check(JSON.stringify(helm.Pos) === '[6,7]', 'dragging from the doll drops the helmet where it was let go ' + JSON.stringify(helm.Pos));
    const helmAt = (await get(['Player', 'Inventory'])).findIndex(i => i.Type === 'Helmet');
    await dragTo(`#inventoryContainer .inv-slot:nth-child(${helmAt + 1})`, await bagPoint('#inventoryContainer', 3, 4, 2, 2));
    await page.waitForFunction(i => JSON.stringify(view.state.Player.Inventory[i].Pos) === '[3,4]', helmAt);
    check(true, 'items can be rearranged in the bag');
    await page.dblclick(`#inventoryContainer .inv-slot:nth-child(${helmAt + 1})`);
    await page.waitForFunction(() => view.state.Player.Equipment.Head !== null);
    await page.dblclick('#slot-Head');
    await page.waitForFunction(() => view.state.Player.Equipment.Head === null);
    check(true, 'double-click equips and unequips');
    const invBefore = (await get(['Player', 'Inventory'])).length;
    await page.click(`#inventoryContainer .inv-slot:nth-child(${invBefore})`);
    await page.click('#selectedItemPanel button:has-text("Sell")');
    await page.waitForFunction(n => view.state.Player.Inventory.length === n - 1, invBefore);
    check(true, 'unequip and sell work');

    // Lock, tooltip, sort
    await pyCall('test_add_item', [1, 'Ring', 'Common']);
    await refresh();
    const ringIndex = (await get(['Player', 'Inventory'])).length - 1;
    await page.hover(`#inventoryContainer .inv-slot:nth-child(${ringIndex + 1})`);
    await page.waitForSelector('#itemTooltip', { state: 'visible' });
    check(/Ring/.test(await text('#itemTooltip')), 'hovering an item shows a tooltip');
    await page.click(`#inventoryContainer .inv-slot:nth-child(${ringIndex + 1})`);
    await page.click('#selectedItemPanel button:has-text("Lock")');
    await page.waitForFunction(i => view.state.Player.Inventory[i].Locked, ringIndex);
    check(!(await page.$('#selectedItemPanel button:has-text("Sell")')) && (await page.$$('#inventoryContainer .slot-badge.lock')).length === 1, 'locked items show a lock and cannot be sold');
    await page.click('button:has-text("Sort")');
    await page.waitForFunction(() => view.state.Player.Inventory[0].Type !== 'Potion');
    check(true, 'sorting puts gear before potions');
    const lockedAt = (await get(['Player', 'Inventory'])).findIndex(i => i.Locked);
    await page.click(`#inventoryContainer .inv-slot:nth-child(${lockedAt + 1})`);
    await page.click('#selectedItemPanel button:has-text("Unlock")');
    await page.waitForFunction(i => !view.state.Player.Inventory[i].Locked, lockedAt);

    // Reforge at the forge
    await pyCall('test_add_item', [5, 'Amulet', 'Rare']);
    await set(['Player', 'Gold'], 5000);
    await refresh();
    await page.click('.nav-tab[data-tab="forge"]');
    const reforgeBtn = '#enhanceContainer .monster-row:last-child button:has-text("Reforge")';
    await page.click(reforgeBtn);
    await page.waitForFunction(() => view.state.Stats.ItemsReforged === 1);
    check(true, 'reforging goes through Python');
    await page.click('.nav-tab[data-tab="overview"]');

    // Sell junk
    await pyCall('test_add_item', [1, 'Ring', 'Common']);
    await pyCall('test_add_item', [1, 'Ring', 'Common']);
    await refresh();
    dialogAnswers.push(true);
    await page.click('button:has-text("Sell Common")');
    await page.waitForFunction(() => !view.state.Player.Inventory.some(i => i.Type === 'Ring' && i.Rarity === 'Common'));
    check(true, 'sell common gear asks, then sells');

    // Training + a notice when it's too expensive
    await set(['Player', 'Gold'], 30);
    await refresh();
    await page.click('.nav-tab[data-tab="training"]');
    check(await page.isDisabled('#trainingContainer .monster-row:nth-child(1) button'), 'unaffordable training is disabled');
    await set(['Player', 'Gold'], 5000);
    await refresh();
    await page.click('#trainingContainer .monster-row:nth-child(1) button');
    await page.waitForFunction(() => view.state.Player.BaseStrength === 6);
    check(true, 'training works');

    // Work
    await page.click('.nav-tab[data-tab="work"]');
    await page.click('#workContainer button:has-text("Work 1h")');
    await page.waitForFunction(() => view.work.active);
    check(/Working at the villa/.test(await text('#sidebarStatus')), 'working status shown with countdown');
    dialogAnswers.push(true);
    await page.click('#workContainer button:has-text("Stop Working")');
    await page.waitForFunction(() => !view.work.active);
    check(true, 'stop working asks, then cancels');

    // Guild with an HTML-injection name, then a donation
    await page.click('.nav-tab[data-tab="guild"]');
    dialogAnswers.push('<img src=x onerror=a=1>', 'ab');
    await page.click('#guildContent button');
    await page.waitForFunction(() => view.state.PlayerGuild.HasGuild);
    check(await page.evaluate(() => document.querySelector('#guildContent img') === null && window.a === undefined), 'guild name is shown as text, not HTML');
    check(/\[AB\]/.test(await text('#guildContent h3')), 'guild tag upper-cased by Python');
    await page.click('#guildContent button:has-text("Donate 100")');
    await page.waitForFunction(() => view.state.PlayerGuild.GoldVault === 100);
    check((await page.$$('#guildContent .exp-card')).length === 3, 'guild buildings render');

    // Quests (the battle series may already have finished the first task)
    await set(['QuestSlots', 0, 'Quest', 'Progress'], 0);
    await refresh();
    await page.click('.nav-tab[data-tab="quests"]');
    dialogAnswers.push(true);
    await page.click('#questContainer .exp-card:nth-child(1) button:has-text("Abandon")');
    await page.waitForFunction(() => view.quests[0].empty);
    check(/new task will be offered/.test(await text('#questContainer .exp-card:nth-child(1)')), 'abandoned quest shows a countdown');
    await pyCall('test_advance_clock', [5 * 60 * 1000 + 1000]);
    await page.waitForFunction(() => !view.quests[0].empty, null, { timeout: 5000 });
    check(true, 'the timer tick brings a new quest');

    // Animated report: the sidebar must not reveal the result early
    await set(['Settings', 'CombatSpeed'], 'Normal');
    await set(['ActiveWork', 'IsWorking'], false);
    await set(['Player', 'CurrentHP'], 999);
    await set(['Player', 'CurrentEnergy'], 20);
    await refresh();
    const hpBefore = await text('#textHp');
    await page.click('.nav-tab[data-tab="expeditions"]');
    await page.click('#expeditionContainer .exp-card:nth-child(1) .monster-row:nth-child(1) button');
    await page.waitForSelector('#combatModal.open');
    check(/FIGHT/.test(await text('#modalCombatResultBanner')), 'report starts animating');
    check(await text('#textHp') === hpBefore && /^20\//.test(await text('#textEnergy')), 'sidebar waits for the report to finish');
    await page.click('#btnSkipCombat');
    check(/VICTORY|DEFEAT/.test(await text('#modalCombatResultBanner')), 'skip reveals the result');
    check(/^19\//.test(await text('#textEnergy')), 'sidebar updates after the report');
    await page.keyboard.press('Escape');

    // Settings: theme, rename, export/import, reset
    await page.click('.nav-tab[data-tab="settings"]');
    await page.selectOption('#themeSelect', 'LegionEmerald');
    await page.waitForFunction(() => view.state.Settings.ThemeMode === 'LegionEmerald');
    check(await page.evaluate(() => document.documentElement.dataset.theme) === 'LegionEmerald', 'theme applies and is stored in Python');
    dialogAnswers.push('  Maximus   Decimus ');
    await page.click('button:has-text("Rename Gladiator")');
    await page.waitForFunction(() => view.state.Player.Name === 'Maximus Decimus');
    check(await text('#gladName') === 'Maximus Decimus', 'rename goes through Python');
    dialogAnswers.push('X');
    await page.click('button:has-text("Rename Gladiator")');
    await page.waitForSelector('.toast:has-text("3-20 characters")');
    check(true, 'invalid name shows Python\'s message');
    check(/saved automatically to/.test(await text('#savePathInfo')), 'save location shown in settings');

    const exportPath = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'aeterna-')), 'save.json');
    await set(['Player', 'Gold'], 4242);
    const imported = await pyCall('test_export_import', [exportPath]);
    check(imported.view.state.Player.Gold === 4242 && JSON.parse(fs.readFileSync(exportPath, 'utf8')).Player.Gold === 4242, 'export/import code paths round-trip');

    dialogAnswers.push(true, 'Nero Claudius');
    await page.click('button:has-text("Reset Gladiator Progress")');
    await page.waitForFunction(() => view.state.Player.Name === 'Nero Claudius' && view.state.Player.Gold === 250);
    check(await page.evaluate(() => document.documentElement.dataset.theme) === 'LegionEmerald', 'reset keeps settings');

    if (SHOTS) {
        await set(['Settings', 'ThemeMode'], 'DarkImperial');
        await refresh();
        for (const tab of ['overview', 'expeditions', 'arena', 'dungeons', 'labors', 'quests', 'forge']) {
            await page.click(`.nav-tab[data-tab="${tab}"]`);
            await shot(`tab-${tab}.png`);
        }
    }

    check(errors.length === 0, 'no page errors ' + JSON.stringify(errors));
    await browser.close();
    py.stdin.end();
    console.log(failures ? `\n${failures} FAILURE(S)` : '\nALL PASSED');
    process.exit(failures ? 1 : 0);
})().catch(err => { console.error(err); py.kill(); process.exit(1); });
