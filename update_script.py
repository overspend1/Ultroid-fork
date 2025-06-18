#!/usr/bin/env python3
"""
Ultroid Update Script - Improved Version
This script handles updating the bot while it's not running using a robust approach.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, shell=True):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        print(f"Command: {cmd}")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
        if result.stderr.strip():
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return False

def backup_important_files():
    """Backup important configuration files."""
    important_files = [
        "config.py",
        ".env", 
        "resources/session/ultroid.session",
        "resources/session/ultroid.session-journal"
    ]
    
    backed_up = []
    for file in important_files:
        if os.path.exists(file):
            backup_name = f"{file}.backup"
            if run_command(f'copy "{file}" "{backup_name}"'):
                backed_up.append((file, backup_name))
                print(f"✅ Backed up {file}")
    
    return backed_up

def restore_important_files(backed_up):
    """Restore important configuration files."""
    for original, backup in backed_up:
        if os.path.exists(backup):
            if run_command(f'copy "{backup}" "{original}"'):
                print(f"✅ Restored {original}")
                run_command(f'del "{backup}"')

def clean_repository():
    """Clean the repository of cache files and reset to clean state."""
    print("🧹 Cleaning repository...")
    
    # Remove Python cache files
    run_command('for /r . %i in (*.pyc) do @del "%i" >nul 2>&1')
    run_command('for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d" >nul 2>&1')
    
    # Reset all tracked files to their HEAD state
    run_command("git reset --hard HEAD")
    
    # Clean untracked files (but preserve update script and important files)
    run_command("git clean -fd -e update_script*.py -e config.py -e .env -e resources/session/")

def main():
    """Main update function."""
    print("🔄 Starting Ultroid update process...")
    
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {script_dir}")
    
    # Check if we're in a git repository
    if not (script_dir / ".git").exists():
        print("❌ Not a git repository. Cannot update.")
        return False
    
    # Get the repository URL from command line args or default to user's fork
    repo_url = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/overspend1/Ultroid-fork.git"
    
    print(f"🔗 Using repository: {repo_url}")
    
    # Backup important files
    backed_up_files = backup_important_files()
    
    # Set up remote
    if not run_command("git remote get-url origin"):
        run_command(f"git remote add origin {repo_url}")
    else:
        run_command(f"git remote set-url origin {repo_url}")
    
    # Fetch latest changes
    print("📥 Fetching updates from repository...")
    if not run_command("git fetch origin"):
        print("❌ Failed to fetch updates")
        return False
    
    # Get current branch
    result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
    current_branch = result.stdout.strip() or "main"
    
    print(f"🌿 Current branch: {current_branch}")
    
    # Clean repository
    clean_repository()
    
    # Force pull updates (this will overwrite any local changes)
    print("⬇️ Force pulling updates...")
    if not run_command(f"git pull origin {current_branch}"):
        # If pull fails, try reset to remote
        print("🔄 Trying hard reset to remote...")
        if not run_command(f"git reset --hard origin/{current_branch}"):
            print("❌ Failed to update repository")
            return False
    
    # Restore important files
    restore_important_files(backed_up_files)
    
    # Update dependencies
    print("📦 Installing/updating dependencies...")
    if not run_command("pip3 install -r requirements.txt --upgrade"):
        print("⚠️ Warning: Failed to update some dependencies")
    
    # Try alternative pip command for systems that need it
    run_command("pip3 install -r requirements.txt --break-system-packages --upgrade")
    
    print("✅ Update completed successfully!")
    return True

def restart_bot():
    """Restart the bot after update."""
    print("🔄 Restarting Ultroid...")
    
    # Check if we have a virtual environment
    venv_python = None
    if os.path.exists("venv/bin/python"):
        venv_python = "venv/bin/python"
    elif os.path.exists("venv/Scripts/python.exe"):
        venv_python = "venv/Scripts/python.exe"
    
    # Determine how to start the bot
    if len(sys.argv) > 1 and sys.argv[-1] == "main.py":
        # Started with main.py
        if venv_python:
            os.execv(venv_python, [venv_python, "main.py"])
        else:
            os.execv(sys.executable, [sys.executable, "main.py"])
    else:
        # Started as module
        if venv_python:
            os.execv(venv_python, [venv_python, "-m", "pyUltroid"])
        else:
            os.execv(sys.executable, [sys.executable, "-m", "pyUltroid"])

if __name__ == "__main__":
    print("🚀 Ultroid Update Script - Improved Version")
    print("=" * 50)
    
    # Wait a moment for the bot to fully shutdown
    time.sleep(2)
    
    # Perform update
    if main():
        print("=" * 50)
        restart_bot()
    else:
        print("❌ Update failed. Please check the errors above.")
        sys.exit(1)
