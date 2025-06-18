#!/usr/bin/env python3
"""
Ultroid Plugin Diagnostic Tool
Comprehensive testing tool to identify issues with plugins and addons.
"""

import os
import sys
import traceback
import importlib.util
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

@dataclass
class PluginTestResult:
    """Result of a plugin test"""
    name: str
    status: str  # 'passed', 'failed', 'warning'
    issues: List[str]
    import_success: bool
    functions_found: List[str]
    dependencies_missing: List[str]

class UltroidPluginDiagnostic:
    """Diagnostic tool for Ultroid plugins and addons"""
    
    def __init__(self):
        self.results: Dict[str, PluginTestResult] = {}
        self.project_root = project_root
        self.common_issues = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log diagnostic messages"""
        print(f"[{level}] {message}")
    
    def test_imports(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Test if a plugin can be imported and find missing dependencies"""
        missing_deps = []
        import_errors = []
        
        try:
            # Read the file to check imports
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Common problematic imports to check
            problematic_imports = [
                'from pyUltroid import',
                'from pyUltroid.fns',
                'from pyUltroid.dB',
                'from pyUltroid._misc',
                'from . import',
                'import google',
                'import requests',
                'import aiohttp',
                'import telethon',
            ]
            
            for imp in problematic_imports:
                if imp in content:
                    # Try to import the specific module
                    try:
                        if 'google' in imp:
                            import google
                    except ImportError as e:
                        missing_deps.append(f"Google API: {str(e)}")
                    
                    if 'requests' in imp:
                        try:
                            import requests
                        except ImportError as e:
                            missing_deps.append(f"requests: {str(e)}")
                    
                    if 'aiohttp' in imp:
                        try:
                            import aiohttp
                        except ImportError as e:
                            missing_deps.append(f"aiohttp: {str(e)}")
            
            # Try to import the module
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return True, import_errors, missing_deps
            else:
                import_errors.append("Could not create module spec")
                return False, import_errors, missing_deps
                
        except ImportError as e:
            import_errors.append(f"Import error: {str(e)}")
            return False, import_errors, missing_deps
        except SyntaxError as e:
            import_errors.append(f"Syntax error: {str(e)}")
            return False, import_errors, missing_deps
        except Exception as e:
            import_errors.append(f"General error: {str(e)}")
            return False, import_errors, missing_deps
    
    def find_functions(self, file_path: Path) -> List[str]:
        """Find command functions in a plugin file"""
        functions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for async functions and ultroid_cmd decorators
            import re
            
            # Find @ultroid_cmd decorated functions
            cmd_pattern = r'@ultroid_cmd\s*\(.*?\)\s*async\s+def\s+(\w+)'
            functions.extend(re.findall(cmd_pattern, content, re.DOTALL))
            
            # Find other async functions that might be commands
            func_pattern = r'async\s+def\s+(\w+)\s*\('
            all_functions = re.findall(func_pattern, content)
            
            # Filter out common utility functions
            command_functions = [f for f in all_functions if not f.startswith('_') and f not in ['main', 'setup', 'init']]
            functions.extend(command_functions)
            
            return list(set(functions))  # Remove duplicates
            
        except Exception as e:
            self.log(f"Error finding functions in {file_path}: {e}", "WARNING")
            return []
    
    def test_plugin_file(self, file_path: Path) -> PluginTestResult:
        """Test a single plugin file"""
        self.log(f"Testing {file_path.name}...")
        
        issues = []
        
        # Test file exists and is readable
        if not file_path.exists():
            return PluginTestResult(
                name=file_path.name,
                status='failed',
                issues=['File does not exist'],
                import_success=False,
                functions_found=[],
                dependencies_missing=[]
            )
        
        # Test imports
        import_success, import_errors, missing_deps = self.test_imports(file_path)
        issues.extend(import_errors)
        
        # Find functions
        functions = self.find_functions(file_path)
        
        # Determine status
        if not import_success:
            status = 'failed'
        elif missing_deps or import_errors:
            status = 'warning'
        else:
            status = 'passed'
        
        return PluginTestResult(
            name=file_path.name,
            status=status,
            issues=issues,
            import_success=import_success,
            functions_found=functions,
            dependencies_missing=missing_deps
        )
    
    def test_gdrive_specific(self) -> Dict[str, Any]:
        """Specific tests for Google Drive functionality"""
        gdrive_issues = {}
        
        # Check if Google API libraries are installed
        try:
            import google.auth
            import google.oauth2
            import googleapiclient
            gdrive_issues['google_libs'] = 'installed'
        except ImportError as e:
            gdrive_issues['google_libs'] = f'missing: {e}'
        
        # Check if credentials are configured
        try:
            from pyUltroid import udB
            
            client_id = udB.get_key("GDRIVE_CLIENT_ID")
            client_secret = udB.get_key("GDRIVE_CLIENT_SECRET")
            auth_token = udB.get_key("GDRIVE_AUTH_TOKEN")
            
            gdrive_issues['client_id'] = 'configured' if client_id else 'not set'
            gdrive_issues['client_secret'] = 'configured' if client_secret else 'not set'
            gdrive_issues['auth_token'] = 'configured' if auth_token else 'not set'
            
        except Exception as e:
            gdrive_issues['config_check'] = f'error: {e}'
        
        # Check credentials file
        creds_file = project_root / "resources" / "auth" / "gdrive_creds.json"
        gdrive_issues['creds_file'] = 'exists' if creds_file.exists() else 'missing'
        
        return gdrive_issues
    
    def run_diagnostics(self):
        """Run comprehensive diagnostics on all plugins and addons"""
        self.log("🔍 Starting Ultroid Plugin Diagnostics...")
        self.log("=" * 50)
        
        # Test plugins directory
        plugins_dir = self.project_root / "plugins"
        addons_dir = self.project_root / "addons"
        
        # Test plugins
        if plugins_dir.exists():
            self.log(f"📁 Testing plugins in {plugins_dir}")
            for plugin_file in plugins_dir.glob("*.py"):
                if plugin_file.name.startswith('__'):
                    continue
                result = self.test_plugin_file(plugin_file)
                self.results[f"plugins/{result.name}"] = result
        
        # Test addons
        if addons_dir.exists():
            self.log(f"📁 Testing addons in {addons_dir}")
            for addon_file in addons_dir.glob("*.py"):
                if addon_file.name.startswith('__'):
                    continue
                result = self.test_plugin_file(addon_file)
                self.results[f"addons/{result.name}"] = result
        
        # Specific Google Drive tests
        self.log("\n🔍 Testing Google Drive specific functionality...")
        gdrive_results = self.test_gdrive_specific()
        
        # Generate report
        self.generate_report(gdrive_results)
    
    def generate_report(self, gdrive_results: Dict[str, Any]):
        """Generate a comprehensive diagnostic report"""
        self.log("\n" + "=" * 60)
        self.log("📊 DIAGNOSTIC REPORT")
        self.log("=" * 60)
        
        # Summary stats
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r.status == 'passed')
        failed = sum(1 for r in self.results.values() if r.status == 'failed')
        warnings = sum(1 for r in self.results.values() if r.status == 'warning')
        
        self.log(f"📈 Summary: {total} files tested")
        self.log(f"   ✅ Passed: {passed}")
        self.log(f"   ⚠️  Warnings: {warnings}")
        self.log(f"   ❌ Failed: {failed}")
        
        # Failed plugins
        if failed > 0:
            self.log(f"\n❌ FAILED PLUGINS ({failed}):")
            for name, result in self.results.items():
                if result.status == 'failed':
                    self.log(f"   • {name}")
                    for issue in result.issues[:3]:  # Show first 3 issues
                        self.log(f"     - {issue}")
                    if result.dependencies_missing:
                        self.log(f"     - Missing deps: {', '.join(result.dependencies_missing)}")
        
        # Warning plugins
        if warnings > 0:
            self.log(f"\n⚠️  WARNING PLUGINS ({warnings}):")
            for name, result in self.results.items():
                if result.status == 'warning':
                    self.log(f"   • {name}")
                    if result.dependencies_missing:
                        self.log(f"     - Missing deps: {', '.join(result.dependencies_missing)}")
        
        # Google Drive specific report
        self.log(f"\n🔧 GOOGLE DRIVE DIAGNOSTIC:")
        for key, value in gdrive_results.items():
            status_icon = "✅" if value in ['installed', 'configured', 'exists'] else "❌"
            self.log(f"   {status_icon} {key}: {value}")
        
        # Recommendations
        self.log(f"\n💡 RECOMMENDATIONS:")
        
        # Check for common missing dependencies
        all_missing_deps = []
        for result in self.results.values():
            all_missing_deps.extend(result.dependencies_missing)
        
        unique_deps = list(set(all_missing_deps))
        if unique_deps:
            self.log("   📦 Install missing dependencies:")
            for dep in unique_deps:
                if 'Google' in dep:
                    self.log("      pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
                elif 'requests' in dep:
                    self.log("      pip3 install requests")
                elif 'aiohttp' in dep:
                    self.log("      pip3 install aiohttp")
        
        # Google Drive specific recommendations
        if gdrive_results.get('google_libs') != 'installed':
            self.log("   🔧 For Google Drive: pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        
        if gdrive_results.get('auth_token') != 'configured':
            self.log("   🔑 Set up Google Drive authentication using your assistant bot")
        
        # Generate fixes script
        self.generate_fixes_script()
    
    def generate_fixes_script(self):
        """Generate a script to fix common issues"""
        fixes_script = """#!/bin/bash
# Auto-generated Ultroid Plugin Fixes Script

echo "🔧 Installing missing dependencies..."

# Install Google API dependencies
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Install common web dependencies
pip3 install requests aiohttp

# Install media dependencies
pip3 install Pillow

# Install other common dependencies
pip3 install beautifulsoup4 lxml

echo "✅ Dependencies installation complete!"
echo ""
echo "🔑 Next steps for Google Drive:"
echo "1. Message your assistant bot with /start"
echo "2. Follow the setup process for Google Drive"
echo "3. Set GDRIVE_CLIENT_ID and GDRIVE_CLIENT_SECRET if using custom credentials"
echo ""
echo "🧪 Run the diagnostic again: python3 diagnose_plugins.py"
"""
        with open("fix_plugins.sh", "w", encoding="utf-8") as f:
            f.write(fixes_script)
        
        self.log(f"\n📝 Generated fix_plugins.sh script")
        self.log("   Run: chmod +x fix_plugins.sh && ./fix_plugins.sh")

def main():
    """Main entry point"""
    diagnostic = UltroidPluginDiagnostic()
    diagnostic.run_diagnostics()

if __name__ == "__main__":
    main()
