"""
Mod Update Utility for FromSoft Seamless Co-op Manager
Handles version detection and checking for mod updates via Nexus Mods API
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
import struct
import re

# Nexus Mods API mapping: game_id -> (nexus_game_domain, mod_id)
NEXUS_MOD_MAP = {
    "ac6": ("armoredcore6firesofrubicon", 3),
    "dsr": ("darksoulsremastered", 899),
    "ds3": ("darksouls3", 1895),
    "er": ("eldenring", 510),
    "ern": ("eldenringnightreign", 3),
}

# Nexus Mods API base URL
NEXUS_API_BASE = "https://api.nexusmods.com/v1"

# TEST MODE: Override installed versions for testing without reinstalling
TEST_VERSION_OVERRIDES = {}  # game_id -> version string


def set_test_version(game_id, version):
    """Set a fake installed version for testing purposes."""
    if version is None:
        TEST_VERSION_OVERRIDES.pop(game_id, None)
    else:
        TEST_VERSION_OVERRIDES[game_id] = str(version)


def get_test_version(game_id):
    """Get the test version override if set."""
    return TEST_VERSION_OVERRIDES.get(game_id)


def clear_test_versions():
    """Clear all test version overrides."""
    TEST_VERSION_OVERRIDES.clear()


def extract_dll_version(dll_path):
    """
    Extract version info from a .dll file's version resource.
    Returns: tuple (major, minor, patch, build) or None if can't extract
    """
    if not os.path.isfile(dll_path):
        return None
    
    try:
        with open(dll_path, 'rb') as f:
            # Read PE header to find version resource
            data = f.read(4096)  # Read first 4KB
            
            # Simple approach: look for version number patterns in the file
            # Pattern for version strings like "1.2.3" or "1.2.3.4"
            version_pattern = rb'(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?'
            matches = re.findall(version_pattern, data)
            
            if matches:
                # Return the first match found
                major, minor, patch, build = matches[0]
                return (
                    int(major),
                    int(minor),
                    int(patch),
                    int(build) if build else 0
                )
    except Exception as e:
        print(f"Error extracting DLL version from {dll_path}: {e}")
    
    return None


def read_version_file(mod_dir):
    """
    Check for common version file locations in a mod directory.
    Returns: version string or None
    """
    version_files = [
        os.path.join(mod_dir, "VERSION"),
        os.path.join(mod_dir, "version.txt"),
        os.path.join(mod_dir, ".version"),
    ]
    
    for vf in version_files:
        if os.path.isfile(vf):
            try:
                with open(vf, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                    if content:
                        # Extract first line that looks like a version
                        for line in content.splitlines():
                            line = line.strip()
                            if line and re.match(r'^\d+\.\d+', line):
                                return line
            except Exception as e:
                print(f"Error reading version file {vf}: {e}")
    
    return None


def guess_installed_version(game_install_path, game_id, game_def):
    """
    Attempt to detect the installed mod version.
    Looks for DLL files or version files in the mod directory.
    Checks test overrides first (for testing without reinstalls).
    
    Args:
        game_install_path: Path to the game installation
        game_id: Game ID (e.g., "er", "ds3")
        game_def: Game definition from GAME_DEFINITIONS
    
    Returns:
        version string (e.g., "1.2.3") or "unknown"
    """
    # CHECK TEST OVERRIDE FIRST (for testing without reinstalling)
    test_version = get_test_version(game_id)
    if test_version:
        return test_version
    
    mod_dir = os.path.join(game_install_path, game_def.get("mod_marker_relative", ""))
    
    if not os.path.isdir(mod_dir):
        return None
    
    # First, try to read a version file
    version = read_version_file(mod_dir)
    if version:
        return version
    
    # Second, try to extract version from DLL files
    try:
        for file in os.listdir(mod_dir):
            if file.endswith('.dll'):
                dll_path = os.path.join(mod_dir, file)
                dll_version = extract_dll_version(dll_path)
                if dll_version:
                    major, minor, patch, build = dll_version
                    if build > 0:
                        return f"{major}.{minor}.{patch}.{build}"
                    else:
                        return f"{major}.{minor}.{patch}"
    except Exception as e:
        print(f"Error scanning DLL files in {mod_dir}: {e}")
    
    return None


def get_nexus_mod_info(game_id, api_key=None):
    """
    Fetch mod information from Nexus Mods API.
    
    The Nexus Mods API requires authentication for most endpoints.
    Without an API key, we'll use a fallback approach or return available info.
    
    Args:
        game_id: Game ID (e.g., "er", "ds3")
        api_key: Optional Nexus Mods API key for higher rate limits
    
    Returns:
        dict with 'latest_version' and 'release_date' or error dict
    """
    if game_id not in NEXUS_MOD_MAP:
        return {"error": f"Unknown game: {game_id}"}
    
    nexus_domain, mod_id = NEXUS_MOD_MAP[game_id]
    
    # Endpoint: GET /games/{domain}/mods/{mod_id}
    url = f"{NEXUS_API_BASE}/games/{nexus_domain}/mods/{mod_id}.json"
    
    headers = {"User-Agent": "FromSoft-Coop-Manager/1.0"}
    if api_key:
        headers["apikey"] = api_key
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Extract latest file information
            if 'uploaded_files' in data and len(data['uploaded_files']) > 0:
                latest_file = data['uploaded_files'][0]  # Most recent upload
                return {
                    "latest_version": latest_file.get('version', 'unknown'),
                    "release_date": latest_file.get('uploaded_time', ''),
                    "size_mb": latest_file.get('size', 0) / (1024 * 1024),
                    "name": latest_file.get('name', ''),
                }
            
            # Fallback to mod version
            return {
                "latest_version": data.get('version', 'unknown'),
                "release_date": data.get('updated_time', ''),
            }
    
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return {
                "error": "Nexus API requires authentication. Download updates manually from Nexus Mods.",
                "requires_auth": True
            }
        elif e.code == 429:
            return {"error": "Rate limited by Nexus API. Please try again later."}
        elif e.code == 404:
            return {"error": f"Mod not found on Nexus Mods for {game_id}"}
        else:
            return {"error": f"API error: {e.code}"}
    except Exception as e:
        return {"error": f"Failed to fetch mod info: {str(e)}"}


def check_mod_update(game_install_path, game_id, game_def, api_key=None, installed_override=None):
    """
    Check if a mod has an available update.
    
    Args:
        game_install_path: Path to the game installation
        game_id: Game ID
        game_def: Game definition
        api_key: Optional Nexus Mods API key
    
    Returns:
        dict with:
        - "installed_version": str or None
        - "latest_version": str
        - "has_update": bool
        - "update_available": bool
        - "nexus_url": str
        - "error": str (if applicable)
    """
    result = {
        "game_id": game_id,
        "game_name": game_def.get("name", "Unknown"),
        "nexus_url": game_def.get("nexus_url", ""),
    }
    
    # Get installed version
    test_version = get_test_version(game_id)
    if test_version:
        installed = test_version
    elif installed_override:
        installed = installed_override
    else:
        installed = None
    result["installed_version"] = installed
    
    # Get latest version from Nexus
    nexus_info = get_nexus_mod_info(game_id, api_key)
    
    if "error" in nexus_info:
        result["error"] = nexus_info["error"]
        result["has_update"] = False
        return result
    
    latest = nexus_info.get("latest_version", "unknown")
    result["latest_version"] = latest
    result.update({k: v for k, v in nexus_info.items() if k != "error" and k != "latest_version"})
    
    # Compare versions
    if installed and latest and latest != "unknown":
        result["has_update"] = version_compare(installed, latest) < 0
    elif latest and latest != "unknown":
        # Unknown installed version: always treat as update available
        result["has_update"] = True
    else:
        result["has_update"] = False
    
    result["update_available"] = result.get("has_update", False)
    
    return result


def version_compare(v1, v2):
    """
    Compare semantic versions.
    Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    def normalize(v):
        """Convert version string to list of integers"""
        parts = []
        for part in v.split('.'):
            try:
                parts.append(int(part))
            except ValueError:
                # Handle pre-release versions (e.g., "1.2.3-beta")
                break
        return parts
    
    parts1 = normalize(v1)
    parts2 = normalize(v2)
    
    # Pad with zeros
    max_len = max(len(parts1), len(parts2))
    parts1 += [0] * (max_len - len(parts1))
    parts2 += [0] * (max_len - len(parts2))
    
    for p1, p2 in zip(parts1, parts2):
        if p1 < p2:
            return -1
        elif p1 > p2:
            return 1
    
    return 0


def check_all_mods_for_updates(config, api_key=None):
    """
    Check all installed mods for updates.
    
    Args:
        config: Configuration dict with games
        api_key: Optional Nexus Mods API key
    
    Returns:
        list of dicts with update status for each game
    """
    from server import GAME_DEFINITIONS
    
    updates = []
    for game_id, game_config in config.get("games", {}).items():
        if not game_config.get("mod_installed"):
            continue
        
        game_def = GAME_DEFINITIONS.get(game_id, {})
        if not game_def:
            continue
        
        install_path = game_config.get("install_path")
        if not install_path:
            continue
        
        installed_override = game_config.get("installed_mod_version")
        update_info = check_mod_update(
            install_path,
            game_id,
            game_def,
            api_key,
            installed_override=installed_override,
        )
        updates.append(update_info)
    
    return updates


if __name__ == "__main__":
    # Test the utility
    test_config = {
        "games": {
            "er": {
                "name": "Elden Ring",
                "install_path": "E:\\SteamLibrary\\steamapps\\common\\ELDEN RING",
                "mod_installed": True,
            }
        }
    }
    
    results = check_all_mods_for_updates(test_config)
    for r in results:
        print(json.dumps(r, indent=2))
