#!/usr/bin/env python3
"""
Fix Addon Import Script
This script fixes the ultroid_cmd import in addon files.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Track if any changes were made
        changes_made = False
        original_content = content
        
        # Fix various import patterns
        fixes = [
            # Fix: from pyUltroid import ultroid_cmd
            (r'from pyUltroid import ultroid_cmd', 'from pyUltroid._misc._decorators import ultroid_cmd'),
            
            # Fix: from pyUltroid.fns.decorators import ultroid_cmd  
            (r'from pyUltroid\.fns\.decorators import ultroid_cmd', 'from pyUltroid._misc._decorators import ultroid_cmd'),
            
            # Fix any other variations
            (r'from \.fns\.decorators import ultroid_cmd', 'from pyUltroid._misc._decorators import ultroid_cmd'),
        ]
        
        for old_pattern, new_import in fixes:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_import, content)
                changes_made = True
        
        # Write back if changes were made
        if changes_made and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed imports in: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix imports in all addon files."""
    print("🔧 Ultroid Addon Import Fixer")
    print("=" * 40)
    
    # Get the current directory
    current_dir = Path.cwd()
    addons_dir = current_dir / "addons"
    
    if not addons_dir.exists():
        print(f"❌ Addons directory not found: {addons_dir}")
        return
    
    print(f"📁 Scanning directory: {addons_dir}")
    
    # Find all Python files in addons directory
    python_files = list(addons_dir.glob("**/*.py"))
    
    if not python_files:
        print("❌ No Python files found in addons directory")
        return
    
    print(f"📄 Found {len(python_files)} Python files")
    print()
    
    fixed_count = 0
    
    # Process each file
    for py_file in python_files:
        if py_file.name == "__init__.py":
            continue  # Skip __init__.py files
            
        if fix_imports_in_file(py_file):
            fixed_count += 1
    
    print()
    print("=" * 40)
    print(f"✅ Import fix completed!")
    print(f"📊 Files processed: {len(python_files)}")
    print(f"🔧 Files fixed: {fixed_count}")
    
    if fixed_count > 0:
        print()
        print("🔄 Restart your bot to apply the changes:")
        print("   ./startup")

if __name__ == "__main__":
    main()
