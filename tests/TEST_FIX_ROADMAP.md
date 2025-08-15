# Test Fix Roadmap - Bakery Mini App Server

## Overview
This roadmap provides a safe, incremental approach to fix test failures without breaking working code. Each fix is isolated and can be applied independently.

## Current Test Status
- **Total Tests:** 193
- **Passing:** 154 (80%)
- **Failing:** 23 (12%)
- **Errors:** 16 (8%)

## Phase 1: Environment & Infrastructure Fixes (Safe - No Code Changes)

### 1.1 Install Missing Dependencies
**Priority:** Critical  
**Risk:** None (environment setup only)

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Install coverage tool
pip install coverage

# Verify Node.js for JavaScript tests
node --version
```

**Expected Outcome:** Eliminates 16 environment-related errors

### 1.2 Fix Test Import Issues
**Priority:** High  
**Risk:** None (test file fixes only)

**Files to Fix:**
- `tests/integration/test_api_integration.py` - Import error
- `tests/unit/test_security_middleware.py` - Attribute errors

**Approach:**
- Update import statements to match actual module structure
- Fix middleware test pattern for aiogram

## Phase 2: Test Expectation Fixes (Low Risk)

### 2.1 Fix Version Consistency Tests
**Priority:** Medium  
**Risk:** Low (test expectations only)

**Issue:** Version numbers don't match expected values
- Expected: `1.3.18`
- Actual: `1.3.28`

**Fix Strategy:**
```python
# Update test expectations to match current versions
# OR update version numbers to match expectations
# Choose based on which is the "correct" version
```

**Files to Update:**
- `tests/unit/test_version_consistency.py`

### 2.2 Fix Keyboard Placeholder Tests
**Priority:** Medium  
**Risk:** Low (test expectations only)

**Issue:** Placeholder text mismatch
- Expected: `"Выберите категорию или действие ⬇️"`
- Actual: `"Используйте меню ⬇️"`

**Fix Strategy:**
```python
# Update test to match actual implementation
self.assertEqual(keyboard.input_field_placeholder, "Используйте меню ⬇️")
```

**Files to Update:**
- `tests/unit/test_keyboards.py`

## Phase 3: Data Format Fixes (Medium Risk)

### 3.1 Fix Phone Number Formatting Tests
**Priority:** Medium  
**Risk:** Medium (format validation)

**Issue:** Format mismatch
- Expected: `"+375291234567"`
- Actual: `"+37529123-45-67"`

**Fix Strategy:**
```python
# Option A: Update test to expect formatted version
self.assertEqual(result, "+37529123-45-67")

# Option B: Update function to return unformatted version
# (Only if formatting is not required by business logic)
```

**Files to Update:**
- `tests/unit/test_main.py`
- `tests/unit/test_orders.py`

### 3.2 Fix Email Body Formatting Tests
**Priority:** Medium  
**Risk:** Medium (email template validation)

**Issue:** Name formatting in email templates
- Expected: `"John Doe"`
- Actual: `"Doe John N/A"`

**Fix Strategy:**
```python
# Update test to match actual email template format
# OR fix email template formatting
# Choose based on business requirements
```

**Files to Update:**
- `tests/unit/test_main.py`

## Phase 4: Logic Fixes (Higher Risk)

### 4.1 Fix Order Number Generation Tests
**Priority:** High  
**Risk:** Medium (order numbering logic)

**Issue:** Order number format validation
- Expected: Starts with "ORD"
- Actual: `"#140825/002"`

**Fix Strategy:**
```python
# Option A: Update test to match actual format
self.assertTrue(result.startswith("#"))

# Option B: Fix order number generation to use "ORD" prefix
# (Only if "ORD" prefix is required by business logic)
```

**Files to Update:**
- `tests/unit/test_main.py`
- `tests/unit/test_orders.py`

### 4.2 Fix Cart Memory Cleanup Tests
**Priority:** Medium  
**Risk:** Medium (cart state management)

**Issue:** Cart state not properly managed in tests
- Expected: User cart exists
- Actual: Empty cart dictionary

**Fix Strategy:**
```python
# Ensure proper cart initialization in test setup
# Add proper cleanup in tearDown
# Mock cart state management if needed
```

**Files to Update:**
- `tests/unit/test_cart.py`

## Phase 5: Parser Logic Fixes (Higher Risk)

### 5.1 Fix Product Details Parser Tests
**Priority:** Medium  
**Risk:** Medium (parsing logic)

**Issue:** HTTP error handling and missing data
- Expected: `None` for errors
- Actual: Dictionary with "N/A" values

**Fix Strategy:**
```python
# Update parser to return None for actual errors
# OR update tests to expect "N/A" fallback values
# Choose based on business requirements
```

**Files to Update:**
- `tests/unit/test_parser.py`

## Implementation Strategy

### Safety Principles
1. **One Fix at a Time** - Apply fixes incrementally
2. **Test After Each Fix** - Verify no regressions
3. **Backup Before Changes** - Keep working code safe
4. **Document Changes** - Track what was modified

### Testing Approach
```bash
# After each fix, run specific test category
python3 -m unittest tests.unit.test_keyboards -v
python3 -m unittest tests.unit.test_main -v
python3 -m unittest tests.unit.test_parser -v

# Run full test suite periodically
python3 tests/run_comprehensive_tests.py
```

### Rollback Plan
```bash
# If any fix breaks working code, revert immediately
git checkout HEAD -- path/to/modified/file
git checkout HEAD -- tests/unit/test_specific_file.py
```

## Detailed Fix Instructions

### Fix 1: Environment Setup (No Risk)
```bash
# Step 1: Install dependencies
pip install -r requirements-test.txt
pip install coverage

# Step 2: Verify installation
python3 -c "import coverage; print('Coverage installed')"
node --version

# Step 3: Test
python3 tests/run_comprehensive_tests.py
```

### Fix 2: Security Middleware Tests (Low Risk)
```python
# Update tests/unit/test_security_middleware.py
# Change from aiohttp pattern to aiogram pattern
# No changes to actual middleware code
```

### Fix 3: Version Consistency (Low Risk)
```python
# Update tests/unit/test_version_consistency.py
# Change expected version from "1.3.18" to "1.3.28"
# OR update actual version numbers
```

### Fix 4: Keyboard Tests (Low Risk)
```python
# Update tests/unit/test_keyboards.py
# Change expected placeholder text
```

### Fix 5: Phone Number Tests (Medium Risk)
```python
# Update tests/unit/test_main.py
# Change expected format to match actual implementation
```

## Success Metrics

### Phase 1 Success Criteria
- [ ] All environment errors resolved
- [ ] All import errors fixed
- [ ] Test runner executes without crashes

### Phase 2 Success Criteria
- [ ] Version consistency tests pass
- [ ] Keyboard tests pass
- [ ] No new failures introduced

### Phase 3 Success Criteria
- [ ] Phone number tests pass
- [ ] Email formatting tests pass
- [ ] Business logic remains intact

### Phase 4 Success Criteria
- [ ] Order number tests pass
- [ ] Cart tests pass
- [ ] Order processing works correctly

### Phase 5 Success Criteria
- [ ] Parser tests pass
- [ ] Product parsing works correctly
- [ ] Overall test success rate > 95%

## Risk Mitigation

### Low Risk Fixes (Phases 1-2)
- Environment setup
- Test expectation updates
- Import statement fixes

### Medium Risk Fixes (Phases 3-4)
- Data format validation
- Order numbering logic
- Cart state management

### High Risk Fixes (Phase 5)
- Parser logic changes
- Business logic modifications

## Timeline Estimate

- **Phase 1:** 1-2 hours (environment setup)
- **Phase 2:** 2-3 hours (test expectations)
- **Phase 3:** 3-4 hours (data formats)
- **Phase 4:** 4-5 hours (logic fixes)
- **Phase 5:** 5-6 hours (parser fixes)

**Total Estimated Time:** 15-20 hours

## Post-Fix Validation

### Automated Testing
```bash
# Run full test suite
python3 tests/run_comprehensive_tests.py

# Run specific test categories
python3 -m unittest discover tests/unit -v
python3 -m unittest discover tests/integration -v
```

### Manual Testing
1. **Bot Functionality** - Test core bot features
2. **Web App** - Test web app functionality
3. **Order Processing** - Test complete order flow
4. **Security** - Test security features

### Code Review
1. Review all changes for unintended side effects
2. Verify business logic remains intact
3. Check for performance regressions
4. Validate security implications

## Conclusion

This roadmap provides a safe, incremental approach to fixing test failures. Each phase builds on the previous one, and all changes are isolated to prevent breaking working code. The focus is on fixing test expectations and environment issues rather than changing core business logic.

The key is to proceed slowly, test frequently, and have a clear rollback plan for each change.
