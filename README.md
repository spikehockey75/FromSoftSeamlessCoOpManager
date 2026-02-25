# FromSoft Co-op Manager

A native Windows desktop app for managing Seamless Co-op mods across FromSoftware games. Install mods, configure settings, manage saves, and launch co-op sessions — all from a single app.

> **Note:** This is a **manager tool only**. The Seamless Co-op mods are created by [LukeYui](https://github.com/LukeYui). All credit for the mods goes to them.

![Windows](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> **Quick install:** Download the installer from the latest [Release](https://github.com/spikehockey75/FromSoftSeamlessCoOpManager/releases) and run it.

---

## Supported Games

| Game | Co-op Mod | Nexus Mods |
|------|-----------|------------|
| **Armored Core 6: Fires of Rubicon** | AC6 Seamless Co-op | [Link](https://www.nexusmods.com/armoredcore6firesofrubicon/mods/3) |
| **Dark Souls Remastered** | DSR Seamless Co-op | [Link](https://www.nexusmods.com/darksoulsremastered/mods/899) |
| **Dark Souls III** | DS3 Seamless Co-op | [Link](https://www.nexusmods.com/darksouls3/mods/1895) |
| **Elden Ring** | Elden Ring Seamless Co-op | [Link](https://www.nexusmods.com/eldenring/mods/510) |
| **Elden Ring Nightreign** | ER Nightreign Seamless Co-op | [Link](https://www.nexusmods.com/eldenringnightreign/mods/3) |

The app scans all Steam library folders across all drives and detects installed games using Steam's `appmanifest` files.

---

## Features

### Mod Management
- **One-click install** from Nexus Mods (with API key for premium fast downloads)
- **Automatic update checking** against Nexus Mods versions
- **Enable/disable** individual mods via toggle switches
- **Mod Engine 3 integration** — generates and manages ME3 TOML profiles for DLL injection and asset loading
- **Add third-party mods** from zip files with automatic game directory detection

### ME3 Profile Viewer
- Structured view of the ME3 profile for each game
- Shows native DLLs and asset packages with enabled/disabled status
- Collapsible raw TOML view for power users
- Games are launched via ME3 for proper mod loading

### Mod Settings
- Edit mod `.ini` settings through a clean dialog UI
- Smart type inference — dropdowns, number fields, and text inputs based on INI comments
- Change highlighting and save confirmation
- Reset to defaults

### Save Manager
- View base game saves (`.sl2`) and co-op saves (`.co2`)
- **Transfer** saves between base and co-op formats
- **Backup and restore** with timestamps
- Ban risk warnings for co-op-to-base transfers

### Game Launching
- Launch games via **Mod Engine 3** with all mods loaded
- Fallback to direct co-op launcher for non-ME3 games
- Error detection with ME3 log file checking
- Desktop shortcut creation

### Nexus Mods Integration
- API key authentication with user profile display
- Automatic mod update checks on scan
- Direct links to Nexus mod pages

---

## Installation

### Prerequisites
- **Windows 10/11**
- **Steam** with at least one supported game installed

### From Release (Recommended)
1. Download the installer `.exe` from the latest [GitHub Release](https://github.com/spikehockey75/FromSoftSeamlessCoOpManager/releases)
2. Run it — installs the app and creates a desktop shortcut
3. Done

### From Source (Development)
```bash
git clone https://github.com/spikehockey75/FromSoftSeamlessCoOpManager.git
cd FromSoftSeamlessCoOpManager
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

### Building the Installer
```bash
.venv\Scripts\python build\build.py
```
Then compile `build\installer.iss` with [Inno Setup](https://jrsoftware.org/isinfo.php) for the full installer.

---

## How to Use

### First Launch
1. Open the app
2. Click **Scan for Games** — scans all drives for Steam libraries and co-op mods
3. Games appear in the sidebar

### Managing Mods
- **Mods tab** — install, update, enable/disable mods
- **ME3 Profile tab** — view the ME3 mod loading configuration
- **Saves tab** — manage save files and backups

### Launching Games
Click the play button in the sidebar. Games with mods are launched via Mod Engine 3 for proper DLL injection.

---

## Project Structure

```
fromsoft_coop_manager/
├── main.py                  Entry point
├── app/
│   ├── config/
│   │   ├── config_manager.py    Config wrapper (config.json)
│   │   └── game_definitions.py  Game metadata and defaults
│   ├── core/
│   │   ├── game_scanner.py      Steam library scanner
│   │   ├── ini_parser.py        INI file parser with type inference
│   │   ├── me2_migrator.py      Mod Engine 2 migration
│   │   ├── me3_service.py       ME3 CLI integration
│   │   ├── mod_installer.py     Mod download and installation
│   │   ├── mod_updater.py       Version comparison and update checking
│   │   └── save_manager.py      Save file operations
│   ├── services/
│   │   ├── nexus_service.py     Nexus Mods API client
│   │   ├── nexus_sso.py         Nexus SSO auth flow
│   │   └── steam_service.py     Steam player count API
│   └── ui/
│       ├── main_window.py       Main window with sidebar/content split
│       ├── sidebar.py           Game list sidebar
│       ├── game_page.py         Per-game tab container
│       ├── terminal_widget.py   Log output panel
│       ├── tabs/                Mods, ME3 Profile, Saves tabs
│       ├── dialogs/             Settings, mod config, ME3 setup dialogs
│       └── widgets/             Toggle switch, etc.
├── resources/
│   ├── dark_theme.qss           Qt stylesheet (dark purple-navy theme)
│   └── covers/                  Steam cover art
├── build/
│   ├── build.py                 PyInstaller build script
│   └── installer.iss            Inno Setup installer config
├── requirements.txt             PySide6
└── VERSION                      App version
```

---

## FAQ

### Can I get banned for using this?

**No.** The co-op mods prevent you from connecting to FromSoftware's matchmaking servers and use separate save files. There is no risk of bans from normal use.

> Do **not** transfer co-op save files back to base game saves and then play online — this risks a ban.

### The app didn't find my game

- Make sure the game is installed via **Steam**
- The co-op mod must be installed in the game folder for settings/saves/launch features
- Click **Scan for Games** to re-detect

### Can I add support for another game?

Add a new entry to `GAME_DEFINITIONS` in `app/config/game_definitions.py`. See existing entries for the format.

---

## Technical Details

| Component | Details |
|-----------|---------|
| **UI Framework** | PySide6 (Qt 6) |
| **Mod Loader** | Mod Engine 3 CLI integration |
| **Packaging** | PyInstaller → Inno Setup installer |
| **Nexus API** | REST API with API key auth |
| **Config** | JSON config file (`config.json`) |
| **Theme** | Custom QSS dark theme (#0e0e18 bg, #e94560 accent) |
