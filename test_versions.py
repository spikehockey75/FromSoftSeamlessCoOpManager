#!/usr/bin/env python3
"""
Test Mode Helper - Dynamically set mod versions for testing without reinstalling
Usage: python test_versions.py <command> [game_id] [version]

Commands:
  set <game_id> <version>  - Set a fake installed version (e.g., set er 1.2.3)
  get                      - Show all current test versions
  clear                    - Clear all test versions
  test-elden-ring          - Test Elden Ring with different scenarios

Examples:
  python test_versions.py set er 1.2.3              # Set ER to 1.2.3
  python test_versions.py set er 1.5.0              # Update ER to 1.5.0
  python test_versions.py set ds3 2.0.0             # Set DS3 to 2.0.0
  python test_versions.py get                       # Show all test versions
  python test_versions.py clear                     # Clear all overrides
  python test_versions.py test-elden-ring           # Interactive ER test
"""

import urllib.request
import urllib.error
import json
import sys

# Base URL for the local API
BASE_URL = "http://127.0.0.1:5000"


def api_call(endpoint, method="GET"):
    """Make an API call to the local server."""
    url = f"{BASE_URL}{endpoint}"
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data, None
    except urllib.error.URLError as e:
        return None, f"Connection error: {e}\nMake sure the app is running: python server.py"
    except json.JSONDecodeError:
        return None, "Invalid JSON response from server"
    except Exception as e:
        return None, f"Error: {e}"


def set_version(game_id, version):
    """Set a test version for a game."""
    data, error = api_call(f"/api/test/set-version/{game_id}/{version}", method="POST")
    if error:
        print(f"✗ {error}")
        return False
    print(f"✓ {data['message']}")
    return True


def get_versions():
    """Show current test versions."""
    data, error = api_call("/api/test/get-versions")
    if error:
        print(f"✗ {error}")
        return False
    
    if data['test_versions']:
        print("\nCurrent test versions:")
        for game_id, version in data['test_versions'].items():
            print(f"  {game_id}: {version}")
    else:
        print("No test versions set.")
    return True


def clear_versions():
    """Clear all test versions."""
    data, error = api_call("/api/test/clear-versions", method="POST")
    if error:
        print(f"✗ {error}")
        return False
    print(f"✓ {data['message']}")
    return True


def test_elden_ring_scenarios():
    """Run through common test scenarios for Elden Ring."""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║          Elden Ring Update Check Test Scenarios           ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    scenarios = [
        {
            "name": "Scenario 1: Old Version (Update Available)",
            "version": "1.0.0",
            "description": "Simulates old mod. Should show 'Update available!'"
        },
        {
            "name": "Scenario 2: Current Version (Up to Date)",
            "version": "1.5.0",
            "description": "Simulates current mod. Should show 'Latest version'"
        },
        {
            "name": "Scenario 3: Very Old Version",
            "version": "0.9.5",
            "description": "Simulates very old mod. Should show large version jump"
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{scenario['name']}")
        print(f"  {scenario['description']}")
        print(f"  Setting version to: {scenario['version']}")

        if set_version("er", scenario['version']):
            print(f"\n  ✓ Now go to: http://127.0.0.1:5000")
            print(f"    Look at Elden Ring card on dashboard")
            print(f"    Or: Elden Ring → Manage → Mod Installer")
            print(f"    Refresh page to see the update notification\n")
            input("    Press ENTER when ready for next scenario...")
        else:
            print("  Failed to set version. Is the app running?")
            break

    print("\n✓ Test scenarios complete!")
    print("  Run: python test_versions.py clear")
    print("  to reset all test versions")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "set" and len(sys.argv) >= 4:
        game_id = sys.argv[2]
        version = sys.argv[3]
        set_version(game_id, version)

    elif command == "get":
        get_versions()

    elif command == "clear":
        response = input("Clear all test versions? (y/n): ").lower()
        if response == 'y':
            clear_versions()
        else:
            print("Cancelled")

    elif command == "test-elden-ring":
        test_elden_ring_scenarios()

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
