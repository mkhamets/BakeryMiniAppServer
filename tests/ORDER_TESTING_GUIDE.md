# 🧪 Order Placement Testing Guide

## Overview
This guide covers comprehensive testing of the order placement functionality in the bakery bot. The tests ensure that orders are processed correctly, validated properly, and all edge cases are handled gracefully.

## 🏗️ Test Structure

### Test Categories

#### 1. **Order Processing Tests** (`TestOrderProcessing`)
- ✅ **Order number generation** - Tests order counter and month reset logic
- ✅ **Email notifications** - Tests SMTP functionality and error handling
- ✅ **Order checkout flow** - Tests complete order processing pipeline
- ✅ **Cart management** - Tests cart operations during order processing

#### 2. **Order Validation Tests** (`TestOrderValidation`)
- ✅ **Required fields validation** - Ensures all necessary data is present
- ✅ **Delivery method validation** - Tests courier vs pickup logic
- ✅ **Email format validation** - Validates email address formats
- ✅ **Data structure validation** - Ensures proper JSON structure

#### 3. **Order Formatting Edge Cases** (`TestOrderFormattingEdgeCases`)
- ✅ **Empty cart handling** - Tests orders with no items
- ✅ **Missing optional fields** - Tests partial data scenarios
- ✅ **Pickup vs courier formatting** - Tests different delivery methods
- ✅ **Price formatting** - Tests various price formats

#### 4. **Order Processing Integration** (`TestOrderProcessingIntegration`)
- ✅ **Complete order flow** - End-to-end order processing
- ✅ **Pickup delivery processing** - Tests pickup-specific logic
- ✅ **Cart integration** - Tests cart operations with orders
- ✅ **Notification integration** - Tests all notification systems

#### 5. **Order Error Handling** (`TestOrderErrorHandling`)
- ✅ **Exception handling** - Tests graceful error handling
- ✅ **Invalid data handling** - Tests malformed order data
- ✅ **System failure recovery** - Tests recovery from failures
- ✅ **User feedback** - Tests error messages to users

## 🚀 Running Tests

### Run All Order Tests
```bash
# From project root
python3 tests/run_order_tests.py

# From tests directory
python3 run_order_tests.py
```

### Run Specific Test Categories
```bash
# Run only order processing tests
python3 tests/run_order_tests.py processing

# Run only validation tests
python3 tests/run_order_tests.py validation

# Run only formatting tests
python3 tests/run_order_tests.py formatting

# Run only integration tests
python3 tests/run_order_tests.py integration

# Run only error handling tests
python3 tests/run_order_tests.py error_handling
```

### Run Individual Test Classes
```bash
# Run specific test class
python3 -m unittest tests.unit.test_orders.TestOrderProcessing

# Run specific test method
python3 -m unittest tests.unit.test_orders.TestOrderProcessing.test_handle_checkout_order_success
```

### Run with Coverage
```bash
# Install coverage if not installed
pip install coverage

# Run tests with coverage
coverage run -m unittest tests.unit.test_orders
coverage report
coverage html  # Generate HTML report
```

## 📋 Test Data

### Sample Order Data Structure
```json
{
  "order_details": {
    "deliveryMethod": "courier",
    "firstName": "John",
    "lastName": "Doe",
    "middleName": "Smith",
    "phone": "+375291234567",
    "email": "test@example.com",
    "city": "Minsk",
    "addressLine": "Test Address 123",
    "deliveryDate": "2025-08-11",
    "comment": "Test comment"
  },
  "cart_items": [
    {
      "id": "4e736e2b-5ce0-434e-af44-7df5bae477ea",
      "name": "Завиванец с маком",
      "price": "18",
      "quantity": 5
    }
  ],
  "total_amount": 90.0
}
```

### Test Environment Variables
```bash
ENVIRONMENT=test
BOT_TOKEN=test_token_123456789
BASE_WEBAPP_URL=http://localhost:8000/test/
ADMIN_CHAT_ID=123456789
ADMIN_EMAIL=test@example.com
ADMIN_EMAIL_PASSWORD=test_password
SMTP_SERVER=smtp.test.com
ENABLE_EMAIL_NOTIFICATIONS=false
```

## 🔧 Test Configuration

### Test Environment Setup
The `tests/test_config.py` file provides utilities for:
- Setting up test environment variables
- Creating temporary test data files
- Mocking bot functions
- Creating test message objects
- Generating test order data

### Mocking Strategy
- **Bot functions**: Mocked to avoid actual Telegram API calls
- **File operations**: Use temporary directories and files
- **External services**: SMTP, HTTP requests are mocked
- **Async functions**: Properly mocked with async/await support

## 📊 Test Coverage

### Functions Tested
- `generate_order_number()` - Order number generation
- `send_email_notification()` - Email sending functionality
- `_handle_checkout_order()` - Main order processing
- `_send_order_notifications()` - Notification system
- `_format_telegram_order_summary()` - Telegram formatting
- `_format_email_body()` - Admin email formatting
- `_format_user_email_body()` - User email formatting
- `format_phone_telegram()` - Phone number formatting

### Edge Cases Covered
- Empty cart orders
- Missing required fields
- Invalid email formats
- Zero amount orders
- Exception handling
- Notification failures
- Cart clearing errors
- Message sending errors

## 🚨 Common Test Issues

### Import Errors
```bash
# If you get import errors, ensure you're running from project root
cd /path/to/BakeryMiniAppServer
python3 tests/run_order_tests.py
```

### Environment Issues
```bash
# If tests fail due to missing environment, check:
echo $ENVIRONMENT
echo $BOT_TOKEN
echo $DATA_DIR
```

### Mock Issues
```bash
# If mocks aren't working, check test configuration
python3 -c "from tests.test_config import setup_test_environment; print('Config OK')"
```

## 📈 Performance Testing

### Load Testing
```bash
# Run tests multiple times to check performance
for i in {1..10}; do
  echo "Run $i"
  time python3 tests/run_order_tests.py
done
```

### Memory Testing
```bash
# Monitor memory usage during tests
python3 -m memory_profiler tests/run_order_tests.py
```

## 🔍 Debugging Tests

### Verbose Output
```bash
# Run with maximum verbosity
python3 -m unittest tests.unit.test_orders -v
```

### Debug Mode
```bash
# Run with debugger
python3 -m pdb tests/run_order_tests.py
```

### Logging
```bash
# Enable debug logging
export PYTHONPATH=.
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from tests.unit.test_orders import *
"
```

## 📝 Adding New Tests

### Test Template
```python
def test_new_functionality(self):
    """Test description."""
    # Arrange
    test_data = "test_value"
    
    # Act
    result = function_under_test(test_data)
    
    # Assert
    self.assertEqual(result, "expected_value")
```

### Async Test Template
```python
async def test_async_functionality(self):
    """Test async function description."""
    # Arrange
    mock_message = create_test_message()
    
    # Act
    result = await async_function_under_test(mock_message)
    
    # Assert
    self.assertTrue(result)
```

## 🎯 Test Goals

### Primary Objectives
1. **Ensure order placement works correctly** under normal conditions
2. **Validate error handling** for edge cases and failures
3. **Test data validation** for all input scenarios
4. **Verify notification systems** work properly
5. **Test cart integration** during order processing

### Quality Metrics
- **Test coverage**: >90% for order-related functions
- **Test execution time**: <30 seconds for full suite
- **Test reliability**: 100% pass rate on stable code
- **Edge case coverage**: All identified scenarios tested

## 🔄 Continuous Integration

### Automated Testing
- Tests run automatically on every commit
- Coverage reports generated automatically
- Performance metrics tracked over time
- Test results reported to development team

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run tests before commit
pre-commit run --all-files
```

---

**Remember**: Good tests are the foundation of reliable order placement functionality. Run tests frequently and add new tests for any new features or edge cases you discover! 🧪✨
