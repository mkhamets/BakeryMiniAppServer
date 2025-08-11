#!/usr/bin/env python3
"""
Order Placement Test Runner
Runs comprehensive tests for order placement functionality
"""

import unittest
import sys
import os
import time
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_order_tests():
    """Run all order placement related tests."""
    print("🧪 Order Placement Test Suite")
    print("=" * 50)
    
    # Test categories
    test_categories = [
        "Order Processing",
        "Order Validation", 
        "Order Formatting Edge Cases",
        "Order Processing Integration",
        "Order Error Handling"
    ]
    
    # Load test suite
    loader = unittest.TestLoader()
    
    # Import and load tests
    try:
        from unit.test_orders import (
            TestOrderProcessing,
            TestOrderValidation,
            TestOrderFormattingEdgeCases,
            TestOrderProcessingIntegration,
            TestOrderErrorHandling
        )
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add test classes
        test_classes = [
            TestOrderProcessing,
            TestOrderValidation,
            TestOrderFormattingEdgeCases,
            TestOrderProcessingIntegration,
            TestOrderErrorHandling
        ]
        
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
            
        print(f"📋 Loaded {suite.countTestCases()} test cases")
        print()
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=False
        )
        
        print("🚀 Starting test execution...")
        print("-" * 50)
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        print(f"⏱️  Total execution time: {end_time - start_time:.2f} seconds")
        print(f"✅ Tests run: {result.testsRun}")
        print(f"❌ Failures: {len(result.failures)}")
        print(f"⚠️  Errors: {len(result.errors)}")
        print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
        
        # Print detailed results
        if result.failures:
            print(f"\n❌ FAILURES ({len(result.failures)}):")
            for test, traceback in result.failures:
                print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\n⚠️  ERRORS ({len(result.errors)}):")
            for test, traceback in result.errors:
                print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
        
        # Success rate
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 All tests passed! Order placement system is working correctly.")
        elif success_rate >= 80:
            print("⚠️  Most tests passed, but some issues were found.")
        else:
            print("🚨 Many tests failed. Order placement system needs attention.")
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"❌ Error importing test modules: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def run_specific_test_category(category_name):
    """Run tests for a specific category."""
    print(f"🧪 Running tests for: {category_name}")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    
    # Map category names to test classes
    category_map = {
        "processing": "TestOrderProcessing",
        "validation": "TestOrderValidation", 
        "formatting": "TestOrderFormattingEdgeCases",
        "integration": "TestOrderProcessingIntegration",
        "error_handling": "TestOrderErrorHandling"
    }
    
    category_key = category_name.lower().replace(" ", "_")
    if category_key not in category_map:
        print(f"❌ Unknown category: {category_name}")
        return False
    
    try:
        from unit.test_orders import TestOrderProcessing, TestOrderValidation, TestOrderFormattingEdgeCases, TestOrderProcessingIntegration, TestOrderErrorHandling
        
        test_class_map = {
            "processing": TestOrderProcessing,
            "validation": TestOrderValidation,
            "formatting": TestOrderFormattingEdgeCases,
            "integration": TestOrderProcessingIntegration,
            "error_handling": TestOrderErrorHandling
        }
        
        test_class = test_class_map[category_key]
        suite = loader.loadTestsFromTestCase(test_class)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print(f"\n📊 {category_name} Test Results:")
        print(f"  Tests run: {result.testsRun}")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Error running {category_name} tests: {e}")
        return False

def main():
    """Main function to run tests."""
    if len(sys.argv) > 1:
        category = " ".join(sys.argv[1:])
        success = run_specific_test_category(category)
    else:
        success = run_order_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
