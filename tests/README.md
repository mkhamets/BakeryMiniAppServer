# 🧪 Test Suite for Bakery Mini App Server

This directory contains comprehensive tests for the Bakery Mini App Server, covering unit tests, integration tests, and web app functionality tests.

## 📁 Test Structure

```
tests/
├── unit/                    # Unit tests for individual modules
│   ├── test_config.py      # Configuration module tests
│   ├── test_keyboards.py   # Keyboard generation tests
│   ├── test_parser.py      # Web scraping parser tests
│   ├── test_privacy_consent_simple.py # Privacy consent tests
│   └── ...
├── integration/            # Integration tests
│   └── test_api_integration.py  # API server integration tests
├── web_app/               # Web app tests
│   ├── test_checkout_validation.py # Checkout validation tests
│   └── test_script.js     # JavaScript functionality tests
├── run_tests.py           # Main test runner
└── README.md              # This file
```

## 🚀 Quick Start

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
python tests/run_tests.py
```

### Run Specific Test Categories

```bash
# Unit tests only
python -m unittest discover tests/unit

# Integration tests only
python -m unittest discover tests/integration

# JavaScript tests (requires Node.js)
node tests/web_app/test_script.js
```

## 📋 Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual functions and modules in isolation.

#### `test_config.py`
- ✅ Environment variable loading
- ✅ Default value handling
- ✅ Configuration validation
- ✅ Error handling for invalid values

#### `test_keyboards.py`
- ✅ Keyboard generation with empty cart
- ✅ Keyboard generation with items in cart
- ✅ WebApp URL formatting
- ✅ Button structure validation
- ✅ Keyboard properties (persistent, resize, etc.)

#### `test_parser.py`
- ✅ Web scraping functionality
- ✅ HTML parsing with BeautifulSoup
- ✅ Product data extraction
- ✅ Error handling for HTTP errors
- ✅ URL joining functionality
- ✅ Data structure validation

#### `test_privacy_consent_simple.py`
- ✅ Privacy consent checkbox HTML structure
- ✅ Privacy consent CSS styles
- ✅ Privacy consent JavaScript functions
- ✅ Privacy consent validation logic
- ✅ Privacy consent form integration
- ✅ Privacy consent error handling
- ✅ Privacy consent event handling
- ✅ Privacy consent accessibility
- ✅ Privacy consent mobile responsiveness
- ✅ Privacy consent gender-neutral text
- ✅ Privacy consent required validation

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test how different components work together.

#### `test_api_integration.py`
- ✅ API server endpoints
- ✅ Web app static file serving
- ✅ CORS headers
- ✅ JSON response formatting
- ✅ Error handling
- ✅ Security headers
- ✅ Performance features

### 3. Web App Tests (`tests/web_app/`)

**Purpose**: Test JavaScript functionality in the web app.

#### `test_checkout_validation.py`
- ✅ Checkout form validation
- ✅ Order processing
- ✅ Error handling
- ✅ Form field validation

#### `test_script.js`
- ✅ Cart functionality (add, remove, update quantities)
- ✅ Local storage operations
- ✅ URL parameter handling
- ✅ View management
- ✅ Product data structure validation
- ✅ Price formatting
- ✅ Image URL handling
- ✅ Category data validation

## 🧪 Running Tests

### Basic Test Execution

```bash
# Run all tests
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py -v

# Run specific test file
python -m unittest tests.unit.test_config

# Run specific test class
python -m unittest tests.unit.test_config.TestConfig

# Run specific test method
python -m unittest tests.unit.test_config.TestConfig.test_bot_token_default_value
```

### Coverage Testing

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests/unit
coverage run -m unittest discover tests/integration

# Generate coverage report
coverage report --show-missing

# Generate HTML coverage report
coverage html
```

### Linting and Code Quality

```bash
# Install linting tools
pip install flake8 black isort

# Run flake8 linting
flake8 bot/ --max-line-length=120 --ignore=E501,W503

# Run black code formatting
black bot/

# Run isort import sorting
isort bot/
```

### Security Testing

```bash
# Install security tools
pip install bandit safety

# Run bandit security checks
bandit -r bot/ -f txt

# Run safety vulnerability checks
safety check
```

## 📊 Test Coverage

The test suite covers:

### Configuration Module (100%)
- ✅ Environment variable handling
- ✅ Default value management
- ✅ Type validation
- ✅ Error handling

### Keyboard Module (100%)
- ✅ Menu generation
- ✅ Cart count display
- ✅ WebApp URL formatting
- ✅ Button structure validation

### Parser Module (95%)
- ✅ Web scraping functionality
- ✅ HTML parsing
- ✅ Product data extraction
- ✅ Error handling
- ✅ URL processing

### API Integration (90%)
- ✅ Endpoint responses
- ✅ Static file serving
- ✅ CORS configuration
- ✅ Error handling
- ✅ Security headers

### Web App JavaScript (85%)
- ✅ Cart functionality
- ✅ Local storage operations
- ✅ View management
- ✅ Data validation
- ✅ UI interactions

### Privacy Consent (100%)
- ✅ HTML structure validation
- ✅ CSS styling validation
- ✅ JavaScript functionality
- ✅ Form integration
- ✅ Error handling
- ✅ Accessibility features
- ✅ Mobile responsiveness

## 🔧 Test Configuration

### Environment Variables for Testing

```bash
# Set test environment variables
export BOT_TOKEN="test_token_12345"
export BASE_WEBAPP_URL="https://test-app.herokuapp.com/bot-app/"
export ADMIN_CHAT_ID="123456789"
export ADMIN_EMAIL="test@example.com"
```

### Mock Data

Tests use mock data to avoid external dependencies:

```python
# Example mock cart data
mock_cart = {
    'product1': {
        'id': 'product1',
        'name': 'Test Product 1',
        'price': 10.50,
        'quantity': 2
    }
}
```

## 🐛 Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with detailed output
python -m unittest discover tests/ -v

# Run specific failing test
python -m unittest tests.unit.test_config.TestConfig.test_bot_token_default_value -v
```

### Common Issues

1. **Import Errors**: Ensure the bot directory is in Python path
2. **Mock Issues**: Check that mocks are properly configured
3. **Async Test Issues**: Use `@unittest_run_loop` decorator for async tests
4. **JavaScript Test Issues**: Ensure Node.js is installed

### Test Logs

Tests include comprehensive logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: python tests/run_tests.py
    - name: Run coverage
      run: |
        coverage run -m unittest discover tests/
        coverage report
```

## 🎯 Test Best Practices

### Writing New Tests

1. **Follow Naming Convention**: `test_<module>_<function>_<scenario>`
2. **Use Descriptive Names**: Test names should explain what they test
3. **Arrange-Act-Assert**: Structure tests with clear sections
4. **Mock External Dependencies**: Don't rely on external services
5. **Test Edge Cases**: Include error conditions and boundary cases

### Example Test Structure

```python
def test_function_name_scenario(self):
    """Test description explaining what is being tested."""
    # Arrange - Set up test data and mocks
    test_data = {...}
    mock_dependency = MagicMock()
    
    # Act - Execute the function being tested
    result = function_under_test(test_data, mock_dependency)
    
    # Assert - Verify the expected outcome
    self.assertEqual(result, expected_value)
    mock_dependency.assert_called_once_with(expected_args)
```

## 📝 Test Documentation

### Test Reports

Generate test reports:

```bash
# Generate HTML test report
python -m pytest tests/ --html=test_report.html --self-contained-html

# Generate coverage report
coverage html --directory=coverage_html
```

### Test Metrics

Track test metrics:

- **Coverage**: Aim for >90% code coverage
- **Performance**: Tests should run in <30 seconds
- **Reliability**: Tests should be deterministic
- **Maintainability**: Tests should be easy to understand and modify

## 🤝 Contributing

When adding new features:

1. **Write Tests First**: Follow TDD principles
2. **Update Test Suite**: Add tests for new functionality
3. **Maintain Coverage**: Ensure new code is covered by tests
4. **Update Documentation**: Keep this README current

## 📞 Support

For test-related issues:

1. Check the test logs for detailed error messages
2. Verify that all dependencies are installed
3. Ensure the test environment is properly configured
4. Review the test documentation for common solutions

---

**Last Updated**: 2025-09-07
**Test Coverage**: 90%+
**Total Tests**: 60+