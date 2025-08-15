# Quick Start Test Fixes

## Immediate Actions (No Risk)

### 1. Install Dependencies
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Install coverage tool
pip install coverage

# Verify Node.js (optional for now)
node --version
```

### 2. Fix Security Middleware Tests (Low Risk)
```bash
# Edit tests/unit/test_security_middleware.py
# The file is already updated with aiogram pattern
# Just run the tests to verify
python3 -m unittest tests.unit.test_security_middleware -v
```

### 3. Fix Version Consistency Tests (Low Risk)
```bash
# Edit tests/unit/test_version_consistency.py
# Change line 34: expected_version = "1.3.28"  # was "1.3.18"
# Change line 74: expected_version = "1.3.28"  # was "1.3.18"
```

### 4. Fix Keyboard Tests (Low Risk)
```bash
# Edit tests/unit/test_keyboards.py
# Change line 32: "Используйте меню ⬇️"  # was "Выберите категорию или действие ⬇️"
# Change line 172: "Используйте меню ⬇️"  # was "Выберите категорию или действие ⬇️"
```

## Quick Test Commands

### Test Specific Modules
```bash
# Test keyboards only
python3 -m unittest tests.unit.test_keyboards -v

# Test version consistency only
python3 -m unittest tests.unit.test_version_consistency -v

# Test security only
python3 -m unittest tests.unit.test_security -v

# Test security middleware only
python3 -m unittest tests.unit.test_security_middleware -v
```

### Test All Unit Tests
```bash
python3 -m unittest discover tests/unit -v
```

### Test Everything
```bash
python3 tests/run_comprehensive_tests.py
```

## Expected Results After Quick Fixes

### Before Fixes
- **Total Tests:** 193
- **Passing:** 154 (80%)
- **Failing:** 23 (12%)
- **Errors:** 16 (8%)

### After Quick Fixes (Phases 1-2)
- **Total Tests:** 193
- **Passing:** ~170 (88%)
- **Failing:** ~15 (8%)
- **Errors:** ~8 (4%)

## Next Steps After Quick Fixes

1. **Verify Environment** - All dependencies installed
2. **Run Full Test Suite** - Check overall improvement
3. **Address Remaining Failures** - Follow detailed roadmap
4. **Document Changes** - Update test documentation

## Rollback Commands

If any fix causes issues:
```bash
# Revert specific test file
git checkout HEAD -- tests/unit/test_keyboards.py
git checkout HEAD -- tests/unit/test_version_consistency.py

# Revert all test changes
git checkout HEAD -- tests/

# Reinstall original dependencies
pip install -r requirements.txt
```
