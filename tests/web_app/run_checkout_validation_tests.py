#!/usr/bin/env python3
"""
Test runner for checkout validation tests
Runs comprehensive tests for checkout form validation logic, order, and error styles
"""

import sys
import os
import subprocess
import unittest

# Add the tests directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_checkout_validation_tests():
    """Run all checkout validation tests"""
    
    print("🧪 CHECKOUT VALIDATION TEST SUITE")
    print("=" * 50)
    
    # Import and run the test suite
    from test_checkout_validation import TestCheckoutValidation
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCheckoutValidation)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print detailed summary
    print("\n" + "=" * 60)
    print("📊 CHECKOUT VALIDATION TEST RESULTS")
    print("=" * 60)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"📈 Success rate: {success_rate:.1f}%")
    
    # Show failures if any
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        print("-" * 40)
        for test, traceback in result.failures:
            print(f"  🔴 {test}")
            print(f"     {traceback.split('AssertionError:')[-1].strip()}")
            print()
    
    # Show errors if any
    if result.errors:
        print(f"\n⚠️  ERRORS ({len(result.errors)}):")
        print("-" * 40)
        for test, traceback in result.errors:
            print(f"  🟡 {test}")
            print(f"     {traceback.split('Exception:')[-1].strip()}")
            print()
    
    # Show test categories
    print(f"\n📋 TEST CATEGORIES:")
    print("-" * 40)
    print("  🔍 Field Validation Tests:")
    print("     - Name field validation (Cyrillic/Latin, hyphens, apostrophes)")
    print("     - Phone field validation (international formats)")
    print("     - Email field validation (standard email formats)")
    print("     - Delivery date validation (today/tomorrow only)")
    print("     - Address field validation (Cyrillic/Latin, numbers, symbols)")
    print("     - Radio button group validation")
    
    print("\n  📝 Validation Order Tests:")
    print("     - Courier delivery method field order")
    print("     - Pickup delivery method field order")
    print("     - Conditional field validation")
    print("     - Field priority sequence")
    
    print("\n  🎨 Error Display Tests:")
    print("     - Error message formatting")
    print("     - Radio group error handling")
    print("     - Partial data validation")
    print("     - Whitespace handling")
    
    print("\n" + "=" * 60)
    
    # Return appropriate exit code
    return len(result.failures) + len(result.errors)

def run_specific_test_category(category):
    """Run tests from a specific category"""
    
    categories = {
        'field': ['test_validate_name_field', 'test_validate_phone_field', 'test_validate_email_field'],
        'order': ['test_validation_order', 'test_validation_condition'],
        'error': ['test_error_message', 'test_radio_group'],
        'all': None
    }
    
    if category not in categories:
        print(f"❌ Unknown category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return 1
    
    print(f"🧪 Running {category.upper()} tests...")
    
    if category == 'all':
        return run_checkout_validation_tests()
    
    # Run specific category tests
    from test_checkout_validation import TestCheckoutValidation
    
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    for test_name in categories[category]:
        try:
            test_suite.addTest(loader.loadTestsFromName(test_name, TestCheckoutValidation))
        except AttributeError:
            print(f"⚠️  Test {test_name} not found, skipping...")
    
    if test_suite.countTestCases() == 0:
        print("❌ No tests found for the specified category")
        return 1
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return len(result.failures) + len(result.errors)

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        exit_code = run_specific_test_category(category)
    else:
        exit_code = run_checkout_validation_tests()
    
    print(f"\n🏁 Test run completed with exit code: {exit_code}")
    
    if exit_code == 0:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed. Check the output above for details.")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
