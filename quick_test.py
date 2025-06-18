#!/usr/bin/env python3
"""
Quick test runner for specific components
Usage: python quick_test.py [component]
Components: core, plugins, database, updates, all
"""

import sys
import subprocess
import argparse

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def run_tests(component="all", verbose=False):
    """Run tests for specified component"""
    
    # Test commands for different components
    test_commands = {
        "core": "pytest tests/test_core.py -v",
        "plugins": "pytest tests/test_plugins.py -v",
        "database": "pytest tests/test_database.py -v -m 'not slow'",
        "updates": "pytest tests/test_updates.py -v",
        "all": "pytest tests/ -v --tb=short"
    }
    
    if verbose:
        test_commands = {k: v + " --tb=long" for k, v in test_commands.items()}
    
    if component not in test_commands:
        print(f"❌ Unknown component: {component}")
        print(f"Available components: {', '.join(test_commands.keys())}")
        return False
    
    print(f"🧪 Running {component} tests...")
    print("=" * 50)
    
    cmd = test_commands[component]
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Tests passed!")
    else:
        print("❌ Tests failed!")
        if stderr:
            print("Errors:")
            print(stderr)
    
    if stdout:
        print(stdout)
    
    return success

def check_dependencies():
    """Check if test dependencies are installed"""
    try:
        import pytest
        import pytest_asyncio
        import pytest_cov
        return True
    except ImportError as e:
        print(f"❌ Missing test dependency: {e}")
        print("💡 Install with: pip install -r test-requirements.txt")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Quick test runner for Ultroid")
    parser.add_argument("component", nargs="?", default="all",
                      help="Component to test (core, plugins, database, updates, all)")
    parser.add_argument("-v", "--verbose", action="store_true",
                      help="Verbose output")
    parser.add_argument("--install-deps", action="store_true",
                      help="Install test dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        print("📦 Installing test dependencies...")
        success, _, _ = run_command("pip install -r test-requirements.txt")
        if success:
            print("✅ Dependencies installed!")
        else:
            print("❌ Failed to install dependencies!")
        return
    
    if not check_dependencies():
        print("💡 Use --install-deps to install missing dependencies")
        return
    
    success = run_tests(args.component, args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
