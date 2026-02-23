"""
Test script for the mod update utility
Tests version detection and Nexus Mods API integration
"""

import json
import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

from mod_updater import (
    version_compare,
    get_nexus_mod_info,
    check_mod_update,
    NEXUS_MOD_MAP
)

def test_version_compare():
    """Test semantic version comparison"""
    print("=" * 60)
    print("Testing semantic version comparison...")
    print("=" * 60)
    
    test_cases = [
        ("1.0.0", "2.0.0", -1),
        ("2.0.0", "1.0.0", 1),
        ("1.0.0", "1.0.0", 0),
        ("1.2.3", "1.2.4", -1),
        ("1.10.0", "1.9.0", 1),
    ]
    
    for v1, v2, expected in test_cases:
        result = version_compare(v1, v2)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status}: compare('{v1}', '{v2}') = {result} (expected {expected})")
    
    print()


def test_nexus_mod_info():
    """Test fetching mod info from Nexus Mods API"""
    print("=" * 60)
    print("Testing Nexus Mods API integration...")
    print("=" * 60)
    print()
    
    # Test all supported games
    for game_id in NEXUS_MOD_MAP.keys():
        print(f"Fetching info for {game_id}...")
        info = get_nexus_mod_info(game_id)
        
        if "error" in info:
            print(f"  Error: {info['error']}")
        else:
            print(f"  Latest version: {info.get('latest_version', 'unknown')}")
            if 'release_date' in info:
                print(f"  Release date: {info['release_date']}")
            if 'size_mb' in info:
                print(f"  Size: {info['size_mb']:.1f} MB")
        print()


def test_elden_ring():
    """Specific test for Elden Ring mod update checking"""
    print("=" * 60)
    print("Testing Elden Ring mod update check...")
    print("=" * 60)
    print()
    
    # Simulate checking update if Elden Ring is installed
    info = get_nexus_mod_info("er")
    
    if "error" in info:
        print(f"Could not fetch Elden Ring mod info: {info['error']}")
        print("(This is expected if the API is rate-limited or unavailable)")
    else:
        print(f"Elden Ring Seamless Co-op latest version: {info.get('latest_version')}")
        print(f"Release date: {info.get('release_date')}")
        print()
        print("If you have Elden Ring installed, you can check your mod version:")
        print("- Look in: <ELDEN_RING_ROOT>/Game/SeamlessCoop/")
        print("- The mod DLL or version.txt file would contain the installed version")


def main():
    print("\n")
    print("  FromSoft Co-op Manager - Mod Updater Test Suite")
    print()
    
    test_version_compare()
    test_nexus_mod_info()
    test_elden_ring()
    
    print("=" * 60)
    print("Test suite completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
