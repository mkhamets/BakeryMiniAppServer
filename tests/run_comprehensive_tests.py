#!/usr/bin/env python3
"""
Comprehensive Test Runner for Bakery Mini App Server
Runs all unit tests, integration tests, security tests, and web app tests
"""

import unittest
import sys
import os
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_python_unit_tests():
    """Run all Python unit tests."""
    print("🧪 Running Python Unit Tests...")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'unit')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests."""
    print("\n🧪 Running Integration Tests...")
    print("=" * 50)
    
    # Discover and run integration tests
    loader = unittest.TestLoader()
    integration_dir = os.path.join(os.path.dirname(__file__), 'integration')
    suite = loader.discover(integration_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_javascript_tests():
    """Run JavaScript tests for web app functionality."""
    print("\n🧪 Running JavaScript Tests...")
    print("=" * 50)
    
    js_test_files = [
        os.path.join(os.path.dirname(__file__), 'web_app', 'test_script.js'),
        os.path.join(os.path.dirname(__file__), 'web_app', 'test_web_app_comprehensive.js')
    ]
    
    all_passed = True
    
    for js_test_file in js_test_files:
        if not os.path.exists(js_test_file):
            print(f"❌ JavaScript test file not found: {js_test_file}")
            all_passed = False
            continue
        
        print(f"Running: {os.path.basename(js_test_file)}")
        
        try:
            # Use Node.js to run JavaScript tests
            result = subprocess.run(['node', js_test_file], 
                                  capture_output=True, text=True, timeout=60)
            
            print(result.stdout)
            if result.stderr:
                print("JavaScript Test Errors:")
                print(result.stderr)
            
            if result.returncode != 0:
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print(f"❌ JavaScript tests timed out: {js_test_file}")
            all_passed = False
        except FileNotFoundError:
            print("❌ Node.js not found. Install Node.js to run JavaScript tests.")
            all_passed = False
        except Exception as e:
            print(f"❌ Error running JavaScript tests: {e}")
            all_passed = False
    
    return all_passed

def run_security_tests():
    """Run security-specific tests."""
    print("\n🔒 Running Security Tests...")
    print("=" * 50)
    
    # Run security test files specifically
    security_test_files = [
        'test_security.py',
        'test_security_middleware.py'
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_file in security_test_files:
        test_path = os.path.join(os.path.dirname(__file__), 'unit', test_file)
        if os.path.exists(test_path):
            # Import and run the test module
            module_name = f"tests.unit.{test_file[:-3]}"
            try:
                module = __import__(module_name, fromlist=[''])
                suite.addTests(loader.loadTestsFromModule(module))
            except Exception as e:
                print(f"❌ Error loading security test {test_file}: {e}")
    
    if suite.countTestCases() > 0:
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    else:
        print("No security tests found")
        return True

def run_coverage_analysis():
    """Run tests with coverage reporting."""
    print("\n📊 Running Coverage Analysis...")
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
            
            # Generate HTML report
            html_result = subprocess.run([
                'coverage', 'html'
            ], capture_output=True, text=True)
            
            if html_result.returncode == 0:
                print("📁 HTML coverage report generated in htmlcov/")
            
            return True
        else:
            print("❌ Coverage run failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running coverage: {e}")
        return False

def generate_test_report(results):
    """Generate a comprehensive test report."""
    print("\n📋 Test Report Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Categories: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if failed_tests > 0:
        print(f"\n❌ {failed_tests} test category(ies) failed!")
        return False
    else:
        print(f"\n🎉 All {total_tests} test categories passed!")
        return True

def check_test_coverage():
    """Check which modules are covered by tests."""
    print("\n🔍 Test Coverage Analysis...")
    print("=" * 50)
    
    # List all Python modules in the bot directory
    bot_dir = os.path.join(project_root, 'bot')
    test_dir = os.path.join(project_root, 'tests', 'unit')
    
    bot_modules = []
    for root, dirs, files in os.walk(bot_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                module_path = os.path.relpath(os.path.join(root, file), project_root)
                module_name = module_path.replace('/', '.').replace('.py', '')
                bot_modules.append(module_name)
    
    # List all test files
    test_files = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_name = file.replace('.py', '')
                test_files.append(test_name)
    
    print(f"Bot Modules ({len(bot_modules)}):")
    for module in sorted(bot_modules):
        print(f"  - {module}")
    
    print(f"\nTest Files ({len(test_files)}):")
    for test in sorted(test_files):
        print(f"  - {test}")
    
    # Check for untested modules
    untested_modules = []
    for module in bot_modules:
        module_name = module.split('.')[-1]  # Get the last part of the module name
        has_test = any(f"test_{module_name}" in test for test in test_files)
        if not has_test:
            untested_modules.append(module)
    
    if untested_modules:
        print(f"\n⚠️  Untested Modules ({len(untested_modules)}):")
        for module in untested_modules:
            print(f"  - {module}")
    else:
        print(f"\n✅ All modules have corresponding tests!")

def main():
    """Main test runner function."""
    print("🚀 Bakery Mini App Server - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Running tests at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Run all test categories
    results['Python Unit Tests'] = run_python_unit_tests()
    results['Integration Tests'] = run_integration_tests()
    results['Security Tests'] = run_security_tests()
    results['JavaScript Tests'] = run_javascript_tests()
    results['Coverage Analysis'] = run_coverage_analysis()
    
    # Generate comprehensive report
    overall_success = generate_test_report(results)
    
    # Check test coverage
    check_test_coverage()
    
    print(f"\n🏁 Test Suite Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if overall_success else 1

if __name__ == '__main__':
    sys.exit(main())

