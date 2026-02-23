"""
Mod Installer - Handles mod installation with backup/restore workflow
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


def backup_settings(game_install_path, game_def):
    """
    Backup the mod settings file with version and timestamp.
    
    Args:
        game_install_path: Path to game installation
        game_def: Game definition from GAME_DEFINITIONS
    
    Returns:
        dict: {'success': bool, 'backup_path': str, 'message': str}
    """
    try:
        config_rel_path = game_def.get("config_relative", "")
        config_path = os.path.join(game_install_path, config_rel_path)
        
        if not os.path.isfile(config_path):
            return {
                "success": False,
                "message": f"Settings file not found: {config_path}"
            }
        
        # Create backups directory inside the mod (co-op) folder
        mod_dir = os.path.join(game_install_path, game_def.get("mod_marker_relative", ""))
        backup_dir = os.path.join(mod_dir, "mod_backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{os.path.splitext(os.path.basename(config_path))[0]}_backup_{timestamp}.ini"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy settings file
        shutil.copy2(config_path, backup_path)
        
        return {
            "success": True,
            "backup_path": backup_path,
            "message": f"Settings backed up to {backup_filename}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to backup settings: {str(e)}"
        }


def remove_old_mod_files(game_install_path, game_def):
    """
    Remove old mod files from mod directory.
    
    Args:
        game_install_path: Path to game installation
        game_def: Game definition
    
    Returns:
        dict: {'success': bool, 'removed_count': int, 'message': str}
    """
    try:
        mod_dir = os.path.join(game_install_path, game_def.get("mod_marker_relative", ""))
        
        if not os.path.isdir(mod_dir):
            return {
                "success": False,
                "message": f"Mod directory not found: {mod_dir}"
            }
        
        removed_count = 0
        
        # Remove all files except settings and backups
        for item in os.listdir(mod_dir):
            item_path = os.path.join(mod_dir, item)
            
            # Skip settings files and backup directories
            if item.endswith('.ini') or item == 'mod_backups':
                continue
            
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    removed_count += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    removed_count += 1
            except Exception as e:
                print(f"Warning: Could not remove {item_path}: {e}")
        
        return {
            "success": True,
            "removed_count": removed_count,
            "message": f"Removed {removed_count} old mod files"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to remove old mod files: {str(e)}"
        }


def extract_mod_files(zip_path, game_install_path, game_def):
    """
    Extract mod files from zip to the correct mod directory.
    
    Args:
        zip_path: Path to mod zip file
        game_install_path: Path to game installation
        game_def: Game definition
    
    Returns:
        dict: {'success': bool, 'extracted_count': int, 'message': str}
    """
    try:
        if not os.path.isfile(zip_path):
            return {
                "success": False,
                "message": f"Zip file not found: {zip_path}"
            }
        
        mod_dir = os.path.join(game_install_path, game_def.get("mod_marker_relative", ""))
        os.makedirs(mod_dir, exist_ok=True)
        
        extracted_count = 0
        
        # Try to find the mod files and extract them
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check what's in the zip
            file_list = zip_ref.namelist()
            
            # Some zips might have a top-level folder, try to detect it
            root_folder = None
            if len(file_list) > 0:
                # Check if all files start with the same folder
                first_part = file_list[0].split('/')[0]
                if all(f.startswith(first_part + '/') or f == first_part for f in file_list):
                    root_folder = first_part
            
            # Extract files to mod directory
            for file_info in zip_ref.infolist():
                file_path = file_info.filename
                
                # Skip directories
                if file_path.endswith('/'):
                    continue
                
                # Remove root folder if present
                if root_folder and file_path.startswith(root_folder + '/'):
                    file_path = file_path[len(root_folder) + 1:]
                elif root_folder and file_path == root_folder:
                    continue
                
                # Extract to mod directory
                target_path = os.path.join(mod_dir, file_path)
                target_dir = os.path.dirname(target_path)
                os.makedirs(target_dir, exist_ok=True)
                
                with zip_ref.open(file_info) as source:
                    with open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                
                extracted_count += 1
        
        return {
            "success": True,
            "extracted_count": extracted_count,
            "message": f"Extracted {extracted_count} mod files"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to extract mod files: {str(e)}"
        }


def restore_settings(backup_path, game_install_path, game_def):
    """
    Restore settings from backup file.
    
    Args:
        backup_path: Path to backup settings file
        game_install_path: Path to game installation
        game_def: Game definition
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        if not os.path.isfile(backup_path):
            return {
                "success": False,
                "message": f"Backup file not found: {backup_path}"
            }
        
        config_rel_path = game_def.get("config_relative", "")
        config_path = os.path.join(game_install_path, config_rel_path)
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Copy backup back to original location
        shutil.copy2(backup_path, config_path)
        
        return {
            "success": True,
            "message": "Settings restored from backup"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to restore settings: {str(e)}"
        }


def install_mod_update(zip_path, game_install_path, game_def):
    """
    Complete mod installation workflow:
    1. Backup current settings
    2. Remove old mod files
    3. Extract new mod files
    4. Restore settings
    
    Args:
        zip_path: Path to new mod zip file
        game_install_path: Path to game installation
        game_def: Game definition
    
    Returns:
        dict: {'success': bool, 'steps': [...], 'message': str}
    """
    steps = []
    
    try:
        # Step 1: Backup settings
        backup_result = backup_settings(game_install_path, game_def)
        steps.append({"step": "backup_settings", **backup_result})
        if not backup_result["success"]:
            return {
                "success": False,
                "steps": steps,
                "message": "Failed to backup settings"
            }
        
        backup_path = backup_result["backup_path"]
        
        # Step 2: Remove old files
        remove_result = remove_old_mod_files(game_install_path, game_def)
        steps.append({"step": "remove_old_files", **remove_result})
        if not remove_result["success"]:
            return {
                "success": False,
                "steps": steps,
                "message": "Failed to remove old mod files"
            }
        
        # Step 3: Extract new files
        extract_result = extract_mod_files(zip_path, game_install_path, game_def)
        steps.append({"step": "extract_new_files", **extract_result})
        if not extract_result["success"]:
            return {
                "success": False,
                "steps": steps,
                "message": "Failed to extract new mod files"
            }
        
        # Step 4: Restore settings
        restore_result = restore_settings(backup_path, game_install_path, game_def)
        steps.append({"step": "restore_settings", **restore_result})
        if not restore_result["success"]:
            return {
                "success": False,
                "steps": steps,
                "message": "Failed to restore settings"
            }
        
        return {
            "success": True,
            "steps": steps,
            "message": "Mod successfully updated! Settings preserved.",
            "backup_path": backup_path
        }
    
    except Exception as e:
        steps.append({
            "step": "error",
            "success": False,
            "message": str(e)
        })
        return {
            "success": False,
            "steps": steps,
            "message": f"Installation failed: {str(e)}"
        }
