#!/usr/bin/env python3
"""
Ultroid Test Runner
Cross-platform test runner for the Ultroid bot test suite.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def install_test_dependencies():
    """Install test dependencies if not already installed."""
    print("📦 Installing test dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "pytest", "pytest-asyncio", "pytest-cov", "pytest-mock"
        ])
        print("✅ Test dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install test dependencies: {e}")
        return False

def run_tests(args):
    """Run the test suite with pytest."""
    # Change to project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=pyUltroid", "--cov-report=html", "--cov-report=term"])
    
    if args.fast:
        cmd.extend(["-x", "--tb=short"])
    
    if args.pattern:
        cmd.extend(["-k", args.pattern])
    
    if args.directory:
        cmd.append(args.directory)
    else:
        cmd.append("tests/")
    
    # Add any additional pytest arguments
    if args.pytest_args:
        cmd.extend(args.pytest_args.split())
    
    print(f"🚀 Running tests with command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Ultroid test suite")
    
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true",
                       help="Run with coverage report")
    parser.add_argument("-f", "--fast", action="store_true",
                       help="Stop on first failure")
    parser.add_argument("-k", "--pattern", type=str,
                       help="Run tests matching pattern")
    parser.add_argument("-d", "--directory", type=str,
                       help="Run tests in specific directory")
    parser.add_argument("--install-deps", action="store_true",
                       help="Install test dependencies")
    parser.add_argument("--pytest-args", type=str,
                       help="Additional arguments to pass to pytest")
    
    args = parser.parse_args()
    
    print("🧪 Ultroid Test Runner")
    print("=" * 40)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            return 1
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing test dependencies...")
        if not install_test_dependencies():
            return 1
    
    # Run tests
    success = run_tests(args)
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
