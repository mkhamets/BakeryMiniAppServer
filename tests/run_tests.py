#!/usr/bin/env python3
"""
Test runner for Bakery Mini App Server
Runs all unit tests, integration tests, and web app tests
"""

import unittest
import sys
import os
import subprocess
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_python_tests():
    """Run all Python unit and integration tests."""
    print("🧪 Running Python Tests...")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'unit')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Add integration tests
    integration_dir = os.path.join(os.path.dirname(__file__), 'integration')
    integration_suite = loader.discover(integration_dir, pattern='test_*.py')
    suite.addTests(integration_suite)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_javascript_tests():
    """Run JavaScript tests for web app functionality."""
    print("\n🧪 Running JavaScript Tests...")
    print("=" * 50)
    
    js_test_file = os.path.join(os.path.dirname(__file__), 'web_app', 'test_script.js')
    
    if not os.path.exists(js_test_file):
        print("❌ JavaScript test file not found")
        return False
    
    try:
        # Use Node.js to run JavaScript tests
        result = subprocess.run(['node', js_test_file], 
                              capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("JavaScript Test Errors:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ JavaScript tests timed out")
        return False
    except FileNotFoundError:
        print("❌ Node.js not found. Install Node.js to run JavaScript tests.")
        return False
    except Exception as e:
        print(f"❌ Error running JavaScript tests: {e}")
        return False

def run_coverage_tests():
    """Run tests with coverage reporting."""
    print("\n📊 Running Tests with Coverage...")
    print("=" * 50)
    
    try:
        # Check if coverage is installed
        import coverage
    except ImportError:
        print("❌ Coverage not installed. Install with: pip install coverage")
        return False
    
    try:
        # Run coverage
        result = subprocess.run([
            'coverage', 'run', '-m', 'unittest', 'discover', 
            '-s', 'tests/unit', '-p', 'test_*.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Generate coverage report
            report_result = subprocess.run([
                'coverage', 'report', '--show-missing'
            ], capture_output=True, text=True)
            
            print("Coverage Report:")
            print(report_result.stdout)
            
            return True
        else:
            print("❌ Coverage tests failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running coverage tests: {e}")
        return False

def run_linting():
    """Run code linting checks."""
    print("\n🔍 Running Code Linting...")
    print("=" * 50)
    
    try:
        # Check if flake8 is available
        result = subprocess.run(['flake8', '--version'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Run flake8 on bot directory
            lint_result = subprocess.run([
                'flake8', 'bot/', '--max-line-length=120', '--ignore=E501,W503'
            ], capture_output=True, text=True)
            
            if lint_result.returncode == 0:
                print("✅ No linting issues found")
                return True
            else:
                print("❌ Linting issues found:")
                print(lint_result.stdout)
                return False
        else:
            print("❌ Flake8 not available. Install with: pip install flake8")
            return False
            
    except FileNotFoundError:
        print("❌ Flake8 not found. Install with: pip install flake8")
        return False
    except Exception as e:
        print(f"❌ Error running linting: {e}")
        return False

def run_security_checks():
    """Run security checks on the codebase."""
    print("\n🔒 Running Security Checks...")
    print("=" * 50)
    
    try:
        # Check if bandit is available
        result = subprocess.run(['bandit', '--version'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Run bandit security checks
            security_result = subprocess.run([
                'bandit', '-r', 'bot/', '-f', 'txt'
            ], capture_output=True, text=True)
            
            if security_result.returncode == 0:
                print("✅ No security issues found")
                return True
            else:
                print("⚠️ Security issues found:")
                print(security_result.stdout)
                return False
        else:
            print("❌ Bandit not available. Install with: pip install bandit")
            return False
            
    except FileNotFoundError:
        print("❌ Bandit not found. Install with: pip install bandit")
        return False
    except Exception as e:
        print(f"❌ Error running security checks: {e}")
        return False

def main():
    """Main test runner function."""
    print("🚀 Bakery Mini App Server - Test Suite")
    print("=" * 50)
    print(f"Running tests at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Run Python tests
    results['python_tests'] = run_python_tests()
    
    # Run JavaScript tests
    results['javascript_tests'] = run_javascript_tests()
    
    # Run coverage tests
    results['coverage_tests'] = run_coverage_tests()
    
    # Run linting
    results['linting'] = run_linting()
    
    # Run security checks
    results['security_checks'] = run_security_checks()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 