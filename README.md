# Czapo presents, a steaming bowl of "It should probably maybe work?". It's a single player "clone" of Gladiatus, the browser game. It's in a proof of concept stage and the code is indeed written with the help of an AI agent.
# Aeterna Roma - Hero of Rome

An offline, single-player ancient Roman RPG that runs entirely on your computer. The whole game is one self-contained web page (`game.html`): no server, no background process, no open network ports.

## Features

- **Dynamic Level Scaling**: Colosseum Arena ladder opponents and Expedition/Dungeon monsters scale their stats, HP, damage, and rewards to match the player's level.
- **10 Interactive Tabs**:
  - Overview / Character Sheet (with hidden combat stats)
  - Attribute Training
  - Expeditions
  - Colosseum Arena (21-place ranking ladder, 5-minute cooldown between bouts)
  - Dungeons
  - Roman Forum Merchants (Weaponsmith, Armorer, General Merchant, Apothecary)
  - The Forge (Smelting & Crafting)
  - Patrician Villa Work (timed shifts that pay out even while the game is closed)
  - Gladiator Guild
  - Game Settings & Theme Customization
- **5 Custom Visual Themes**: Dark Imperial, Roman Parchment, Colosseum Crimson, Legion Emerald, and Tyrian Purple.

## Playing

**Without building anything:** double-click `game.html` to open it in your browser (Edge, Chrome, or Firefox).

**As a Windows app:** run `build.bat` from Command Prompt or PowerShell to compile `AeternaRoma.exe`, then double-click it.

```cmd
build.bat
```

`AeternaRoma.exe` is only a small launcher. `game.html` is embedded inside it. The launcher unpacks the page to `%LOCALAPPDATA%\AeternaRoma\game.html`, opens it in a chromeless Edge (or Chrome) app window, and exits straight away. If neither browser is found, it opens the page in your default browser.

## Saving

- Progress is saved automatically in the browser's local storage after every action.
- Saves belong to the browser that ran the game. The launcher always opens the page from the same location, so your save carries over between launches.
- Use **Settings → Export Save File** to back up your gladiator or move it to another computer, and **Import Save File** to load it again. Save files from the old server version (`savegame.json`) can be imported too.
- If a save can't be read, it is kept as a backup copy in local storage, and a new game starts in its place.
