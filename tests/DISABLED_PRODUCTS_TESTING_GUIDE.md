# Disabled Products Feature - Testing Guide

## Overview

This document describes the comprehensive unit tests for the disabled products feature, which handles products that are no longer available in the catalog but remain in user carts.

## Feature Description

The disabled products feature includes:

1. **Product Availability Checking**: Determines if a product is still available in the catalog
2. **Disabled Product Detection**: Identifies unavailable products in the cart
3. **Error Message Display**: Shows warning when disabled products are present
4. **Checkout Button Management**: Disables checkout when disabled products exist
5. **Visual Styling**: Applies disabled styling to unavailable products

## Test Coverage

### Core Function Tests

#### 1. `isProductAvailable(productId)`
- ✅ **Available Product**: Returns `true` for products with valid availability days
- ✅ **Unavailable Product**: Returns `false` for products with "N/A" availability
- ✅ **Non-existent Product**: Returns `false` for products not in catalog
- ✅ **Edge Cases**: Handles null, empty, and invalid product IDs

#### 2. `getDisabledProducts(cartItems)`
- ✅ **Mixed Cart**: Correctly identifies disabled products in mixed availability cart
- ✅ **All Available**: Returns empty array when all products are available
- ✅ **Empty Cart**: Returns empty array for empty cart
- ✅ **Large Cart**: Handles performance with 100+ cart items

#### 3. `renderDisabledProductsError(disabledProducts)`
- ✅ **With Disabled Products**: Creates Bootstrap alert with warning message
- ✅ **No Disabled Products**: Returns null when no disabled products exist
- ✅ **DOM Integration**: Properly inserts error message in correct location

#### 4. `updateCheckoutButtonState(disabledProducts)`
- ✅ **With Disabled Products**: Disables checkout button and adds 'disabled' class
- ✅ **No Disabled Products**: Enables checkout button and removes 'disabled' class

### Integration Tests

#### 5. Cart Rendering with Disabled Products
- ✅ **Visual Styling**: Applies disabled styling to unavailable products
- ✅ **Button States**: Disables quantity controls for disabled products
- ✅ **Error Display**: Shows error message when disabled products exist

#### 6. Product Availability Logic
- ✅ **Availability Days**: Products with "N/A" are considered unavailable
- ✅ **Valid Availability**: Products with specific days are considered available
- ✅ **Consistency**: Same product always has same availability status

### Edge Cases and Performance

#### 7. Edge Cases
- ✅ **Null Values**: Handles null product IDs gracefully
- ✅ **Empty Strings**: Handles empty product IDs
- ✅ **Missing IDs**: Handles cart items without ID field
- ✅ **Invalid Data**: Handles malformed cart items

#### 8. Performance Testing
- ✅ **Large Carts**: Processes 100+ items within 1 second
- ✅ **Memory Usage**: Efficient memory usage with large datasets
- ✅ **Scalability**: Maintains performance as cart size increases

## Running the Tests

### Prerequisites
```bash
# Ensure you're in the project root directory
cd /path/to/BakeryMiniAppServer

# Install test dependencies (if any)
pip install -r requirements-test.txt
```

### Running All Disabled Products Tests
```bash
# Run the dedicated test runner
python tests/run_disabled_products_tests.py
```

### Running Individual Test File
```bash
# Run just the disabled products unit tests
python -m unittest tests.unit.test_disabled_products -v
```

### Running Specific Test Methods
```bash
# Run a specific test method
python -m unittest tests.unit.test_disabled_products.TestDisabledProducts.test_is_product_available_with_available_product -v
```

## Test Data

### Sample Products Data
```json
{
  "category_bakery": [
    {
      "id": "49",
      "name": "Завиванец с маком",
      "price": "8.5",
      "availability_days": "выпекаем пн, чт, сб"
    },
    {
      "id": "50",
      "name": "Печенье «Кантуччи с миндалем»",
      "price": "9.5",
      "availability_days": "N/A"
    }
  ]
}
```

### Sample Cart Items
```json
[
  {
    "id": "49",
    "name": "Завиванец с маком",
    "price": "8.5",
    "quantity": 2
  },
  {
    "id": "50",
    "name": "Печенье «Кантуччи с миндалем»",
    "price": "9.5",
    "quantity": 1
  }
]
```

## Expected Test Results

### Successful Test Run
```
🧪 Running Disabled Products Unit Tests
==================================================
test_edge_cases (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_get_disabled_products_with_all_available (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_get_disabled_products_with_empty_cart (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_get_disabled_products_with_mixed_cart (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_is_product_available_with_available_product (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_is_product_available_with_nonexistent_product (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_is_product_available_with_unavailable_product (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_performance_with_large_cart (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_product_availability_logic (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_render_disabled_products_error_with_disabled_products (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_render_disabled_products_error_with_no_disabled_products (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_update_checkout_button_state_with_disabled_products (tests.unit.test_disabled_products.TestDisabledProducts) ... ok
test_update_checkout_button_state_with_no_disabled_products (tests.unit.test_disabled_products.TestDisabledProducts) ... ok

==================================================
📊 Test Results Summary:
   Tests run: 13
   Failures: 0
   Errors: 0
   Skipped: 0

✅ All disabled products tests passed!
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```
ModuleNotFoundError: No module named 'tests'
```
**Solution**: Ensure you're running tests from the project root directory.

#### 2. Mock Errors
```
AttributeError: 'MagicMock' object has no attribute 'innerHTML'
```
**Solution**: The test mocks DOM elements. Ensure proper mock setup.

#### 3. Performance Test Failures
```
AssertionError: Large cart processing took 1.5 seconds
```
**Solution**: Check system performance or increase timeout threshold.

### Debug Mode

To run tests with detailed debugging:
```bash
# Run with maximum verbosity
python -m unittest tests.unit.test_disabled_products -v -f

# Run with debug logging
python -m unittest tests.unit.test_disabled_products --debug
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Disabled Products Tests
  run: |
    python tests/run_disabled_products_tests.py
    if [ $? -ne 0 ]; then
      echo "❌ Disabled products tests failed"
      exit 1
    fi
```

## Maintenance

### Adding New Tests
1. Add test method to `TestDisabledProducts` class
2. Follow naming convention: `test_<function_name>_<scenario>`
3. Include docstring explaining test purpose
4. Update this documentation

### Updating Test Data
1. Modify `setUp()` method in test class
2. Ensure test data reflects real-world scenarios
3. Update sample data in this documentation

### Performance Thresholds
- Large cart processing: < 1 second
- Memory usage: < 100MB for 1000 items
- Test execution: < 5 seconds total

## Related Files

- `tests/unit/test_disabled_products.py` - Main test file
- `tests/run_disabled_products_tests.py` - Test runner
- `bot/web_app/script.js` - Implementation being tested
- `bot/web_app/style.css` - Styling for disabled products
