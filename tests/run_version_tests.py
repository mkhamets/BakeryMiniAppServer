#!/usr/bin/env python3
"""
Test runner for version consistency tests.
Runs all version-related tests to ensure consistency.
"""

import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.unit.test_version_consistency import TestVersionConsistency


def run_version_tests():
    """Run all version consistency tests."""
    print("🧪 Running Version Consistency Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all tests from TestVersionConsistency
    test_suite.addTest(unittest.makeSuite(TestVersionConsistency))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
            
    if result.errors:
        print("\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
            
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        print("🎯 All files have consistent version v=1.3.1")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("🔧 Please fix version inconsistencies")
        return False


if __name__ == '__main__':
    success = run_version_tests()
    sys.exit(0 if success else 1)
