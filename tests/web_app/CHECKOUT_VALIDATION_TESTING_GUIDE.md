# 🧪 Checkout Validation Testing Guide

## Overview
This guide covers comprehensive unit testing for the checkout form validation logic, validation order, and error styles on the checkout screen.

## 📁 Test Files

### Core Test Files
- **`test_checkout_validation.py`** - Main test suite with all validation tests
- **`run_checkout_validation_tests.py`** - Test runner with category filtering
- **`CHECKOUT_VALIDATION_TESTING_GUIDE.md`** - This documentation

## 🚀 Running Tests

### Run All Tests
```bash
cd tests/web_app
python run_checkout_validation_tests.py
```

### Run Specific Categories
```bash
# Field validation tests only
python run_checkout_validation_tests.py field

# Validation order tests only
python run_checkout_validation_tests.py order

# Error display tests only
python run_checkout_validation_tests.py error

# All tests (default)
python run_checkout_validation_tests.py all
```

### Run Individual Tests
```bash
# Run specific test method
python -m unittest test_checkout_validation.TestCheckoutValidation.test_validate_name_field_valid

# Run with verbose output
python -m unittest -v test_checkout_validation.TestCheckoutValidation
```

## 🧪 Test Categories

### 1. 🔍 Field Validation Tests

#### Name Field Validation
- **Valid inputs**: Cyrillic names, Latin names, hyphenated names, names with apostrophes
- **Invalid inputs**: Empty strings, whitespace-only, numbers, special characters
- **Regex pattern**: `/^[\p{Script=Latin}\p{Script=Cyrillic}\s\-']+$/u`

#### Phone Field Validation
- **Valid inputs**: International formats, Belarusian numbers, Russian numbers, US numbers
- **Invalid inputs**: Empty strings, letters, too short, too long, invalid characters
- **Regex pattern**: `/^\+?[\d\s\-\(\)]{7,20}$/`

#### Email Field Validation
- **Valid inputs**: Standard email formats, subdomains, user+tag format
- **Invalid inputs**: Empty strings, missing @, missing domain, spaces, invalid characters
- **Regex pattern**: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

#### Delivery Date Validation
- **Valid inputs**: Today's date, tomorrow's date (DD.MM.YYYY format)
- **Invalid inputs**: Empty strings, past dates, future dates beyond tomorrow, wrong format
- **Business logic**: Only allows delivery on current day or next day

#### Address Field Validation
- **Valid inputs**: Cyrillic/Latin text, numbers, common address symbols
- **Invalid inputs**: Empty strings, special characters not allowed in addresses
- **Regex pattern**: `/^[\p{Script=Latin}\p{Script=Cyrillic}\p{N}\s\-\.,\/#№()]+$/u`

#### Radio Button Group Validation
- **Delivery Method**: Must be 'courier' or 'pickup'
- **Payment Method**: Must have a selected value
- **Pickup Address**: Must have a selected value

### 2. 📝 Validation Order Tests

#### Courier Delivery Method
**Required fields in order:**
1. `lastName` - Фамилия
2. `firstName` - Имя
3. `middleName` - Отчество
4. `phoneNumber` - Номер телефона
5. `email` - Email
6. `deliveryDate` - Дата доставки
7. `deliveryMethod` - Способ получения
8. `city` - Город для доставки
9. `addressLine` - Адрес доставки
10. `paymentMethod` - Способ оплаты

#### Pickup Delivery Method
**Required fields in order:**
1. `lastName` - Фамилия
2. `firstName` - Имя
3. `middleName` - Отчество
4. `phoneNumber` - Номер телефона
5. `email` - Email
6. `deliveryDate` - Дата самовывоза
7. `deliveryMethod` - Способ получения
8. `pickupAddress` - Адрес самовывоза
9. `paymentMethodPickup` - Способ оплаты

#### Conditional Validation
- **Courier fields** (`city`, `addressLine`, `paymentMethod`) only validated when `deliveryMethod === 'courier'`
- **Pickup fields** (`pickupAddress`, `paymentMethodPickup`) only validated when `deliveryMethod === 'pickup'`

### 3. 🎨 Error Display Tests

#### Error Message Formatting
- **Standard format**: `"Пожалуйста, введите {field_label}."`
- **Field labels**: Proper Russian labels for each field type
- **Consistent styling**: All error messages follow same pattern

#### Radio Group Error Handling
- **Container styling**: Error styling applied to radio group containers
- **Element references**: Proper handling of `elementType: 'radio'` and `errorElement`
- **Focus management**: First radio button in group receives focus

#### Partial Data Validation
- **Mixed valid/invalid**: Tests scenarios with some fields filled and others empty
- **Error isolation**: Only empty/invalid fields appear in error list
- **Validation completeness**: All required fields are checked regardless of partial completion

#### Whitespace Handling
- **Empty strings**: Treated as invalid
- **Whitespace-only**: Treated as invalid (trimmed before validation)
- **Mixed content**: Valid content with leading/trailing whitespace is valid

## 🔧 Test Setup and Mocking

### DOM Element Mocking
```python
self.mock_dom_elements = {
    'last-name': Mock(value='', id='last-name'),
    'first-name': Mock(value='', id='first-name'),
    # ... more elements
}
```

### Error Element Mocking
```python
self.mock_error_elements = {
    'lastName-error': Mock(id='lastName-error'),
    'firstName-error': Mock(id='firstName-error'),
    # ... more error elements
}
```

### Container Element Mocking
```python
self.mock_containers = {
    'payment-method-section': Mock(id='payment-method-section'),
    'pickup-radio-group': Mock(id='pickup-radio-group'),
    # ... more containers
}
```

## 📊 Test Coverage

### Field Validation Coverage
- ✅ Name fields (lastName, firstName, middleName)
- ✅ Contact fields (phoneNumber, email)
- ✅ Delivery fields (deliveryDate, deliveryMethod)
- ✅ Address fields (city, addressLine)
- ✅ Pickup fields (pickupAddress)
- ✅ Payment fields (paymentMethod, paymentMethodPickup)

### Validation Logic Coverage
- ✅ Empty value validation
- ✅ Whitespace handling
- ✅ Regex pattern matching
- ✅ Custom validation functions
- ✅ Conditional field validation
- ✅ Radio group handling

### Error Handling Coverage
- ✅ Error message generation
- ✅ Error field identification
- ✅ Error container styling
- ✅ Focus management
- ✅ Validation order preservation

## 🐛 Common Test Issues

### Import Errors
**Problem**: `ModuleNotFoundError: No module named 'web_app.script'`
**Solution**: Ensure the bot directory is in the Python path:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))
```

### Mock Object Issues
**Problem**: Mock objects not behaving as expected
**Solution**: Use proper Mock configuration:
```python
mock_element = Mock(value='test', id='test-id')
mock_element.classList = Mock()
mock_element.style = Mock()
```

### Date Mocking Issues
**Problem**: Date validation tests failing due to timezone/date differences
**Solution**: Use proper date mocking:
```python
with patch('web_app.script.Date') as mock_date:
    mock_today = Mock()
    mock_today.getDate.return_value = 15
    mock_today.getMonth.return_value = 0
    mock_today.getFullYear.return_value = 2024
```

## 📈 Performance Considerations

### Test Execution Time
- **Individual tests**: < 100ms each
- **Full suite**: < 5 seconds
- **Mock overhead**: Minimal impact

### Memory Usage
- **Mock objects**: Lightweight, cleaned up automatically
- **Test data**: Small datasets, no large file operations
- **Cleanup**: Automatic via unittest framework

## 🔍 Debugging Tests

### Verbose Output
```bash
python -m unittest -v test_checkout_validation.TestCheckoutValidation
```

### Single Test Debugging
```bash
python -m unittest test_checkout_validation.TestCheckoutValidation.test_validate_name_field_valid -v
```

### Test Isolation
```bash
# Run only failing tests
python -m unittest test_checkout_validation.TestCheckoutValidation.test_specific_failing_test
```

## 📝 Adding New Tests

### Test Method Naming Convention
```python
def test_[function_name]_[scenario]_[expected_result](self):
    """Test description"""
    # Test implementation
```

### Example New Test
```python
def test_validate_custom_field_edge_case(self):
    """Test custom field validation with edge case input"""
    from web_app.script import validateCustomField
    
    # Test edge case
    result = validateCustomField('edge_case_input')
    
    # Assert expected behavior
    self.assertTrue(result, "Edge case should be handled correctly")
```

## 🎯 Test Goals

### Primary Objectives
1. **Ensure validation logic correctness** for all field types
2. **Verify validation order** matches business requirements
3. **Test error display** functionality and styling
4. **Cover edge cases** and boundary conditions
5. **Maintain test maintainability** with clear structure

### Success Criteria
- ✅ All tests pass consistently
- ✅ 100% coverage of validation functions
- ✅ Edge cases properly handled
- ✅ Error scenarios correctly identified
- ✅ Performance within acceptable limits

## 📚 Related Documentation

- **Main Test Guide**: `../README.md`
- **Order Testing Guide**: `../ORDER_TESTING_GUIDE.md`
- **Integration Tests**: `../integration/test_api_integration.py`
- **Security Tests**: `../unit/test_security_features.py`

---

**Last Updated**: 2024-01-27  
**Test Suite Version**: 1.0.0  
**Coverage Target**: 100% validation logic coverage
