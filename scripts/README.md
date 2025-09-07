# 🚀 Cache Management Scripts

Collection of scripts for managing cache versions in Bakery Mini App.

## 📋 Overview

This system replaces the old `bump_cache.sh` with a more reliable and extensible Python solution with bash wrapper for compatibility.

## 🔧 Scripts

### 1. `cache_manager.py` - Main Cache Manager

**Description:** Comprehensive cache version management system for all file types.

**Features:**
- ✅ Update cache versions in all WebApp files
- ✅ Automatic backup creation
- ✅ Change validation
- ✅ Rollback from backup
- ✅ Support for all file types (HTML, CSS, JS, SVG)
- ✅ Handle `sprite.svg`, `main.min.css`, and all SVG files in `images/`

**Usage:**
```bash
# Update cache version
python3 scripts/cache_manager.py 1.3.111

# Update with custom timestamp
python3 scripts/cache_manager.py 1.3.111 --timestamp 1756284000

# Validation only (no changes)
python3 scripts/cache_manager.py 1.3.111 --validate-only

# No backup creation
python3 scripts/cache_manager.py 1.3.111 --no-backup

# Rollback from backup
python3 scripts/cache_manager.py 1.3.111 --rollback
```

**What gets updated:**
- `bot/web_app/index.html` - all resource links
- `bot/web_app/style.css` - all `url()` links
- `bot/web_app/main.min.css` - all `url()` links
- `bot/web_app/script.js` - `CACHE_VERSION` constant and all file links
- `bot/web_app/sprite.svg` - any resource links
- `bot/web_app/images/*.svg` - all SVG files in images folder

### 2. `bump_cache.sh` - Bash Wrapper

**Description:** Bash wrapper for backward compatibility with existing workflows.

**Usage:**
```bash
# Update cache version
bash scripts/bump_cache.sh 1.3.111

# Update with custom timestamp
bash scripts/bump_cache.sh 1.3.111 1756284000

# Validation only
bash scripts/bump_cache.sh 1.3.111 --validate-only

# No backup
bash scripts/bump_cache.sh 1.3.111 --no-backup

# Rollback
bash scripts/bump_cache.sh 1.3.111 --rollback
```

### 3. `validate_cache.py` - Cache Validator

**Description:** Validates cache version consistency across all files.

**Features:**
- ✅ Detect duplicate parameters
- ✅ Detect malformed parameters
- ✅ Detect unclosed quotes
- ✅ Version consistency report

**Usage:**
```bash
# Validate current cache state
python3 scripts/validate_cache.py

# Validate specific version
python3 scripts/validate_cache.py 1.3.111
```

### 4. `test_cache_manager.py` - Unit Tests

**Description:** Unit tests for cache management functionality.

**Usage:**
```bash
# Run all tests
python3 -m pytest scripts/test_cache_manager.py -v

# Run specific test
python3 -m pytest scripts/test_cache_manager.py::TestCacheManager::test_update_html_file -v
```

## 🛠️ Technical Details

### Cache Version Format

Cache versions use the format: `?v=1.3.xxx&t=timestamp`

- `v` - version number (e.g., 1.3.111)
- `t` - timestamp for additional cache busting

### File Processing

#### HTML Files
- Updates all `src` and `href` attributes
- Handles both relative and absolute URLs
- Preserves existing query parameters

#### CSS Files
- Updates all `url()` references
- Handles both relative and absolute URLs
- Preserves existing query parameters

#### JavaScript Files
- Updates `CACHE_VERSION` constant
- Updates all file references in strings
- Uses ultra-safe regex to prevent code corruption

#### SVG Files
- Updates any resource references
- Handles both relative and absolute URLs
- Preserves existing query parameters

### Backup System

#### Automatic Backups
- Created before any changes
- Stored in `cache_backups/` directory
- Timestamped for easy identification
- Can be used for rollback

#### Rollback Process
1. Identify backup to restore
2. Copy backup files to original locations
3. Verify restoration
4. Clean up backup files

### Validation System

#### Pre-Update Validation
- Check file accessibility
- Verify version format
- Validate timestamp format
- Check for existing cache parameters

#### Post-Update Validation
- Verify all files were updated
- Check for syntax errors
- Validate cache parameter format
- Ensure no file corruption

## 🔍 Error Handling

### Common Issues

#### 1. File Access Errors
```bash
# Check file permissions
ls -la bot/web_app/

# Fix permissions if needed
chmod 644 bot/web_app/*.html
chmod 644 bot/web_app/*.css
chmod 644 bot/web_app/*.js
```

#### 2. Backup Errors
```bash
# Check backup directory
ls -la cache_backups/

# Create backup directory if missing
mkdir -p cache_backups/
```

#### 3. Validation Errors
```bash
# Run validation to see issues
python3 scripts/validate_cache.py

# Fix issues manually or use rollback
python3 scripts/cache_manager.py 1.3.111 --rollback
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set debug environment variable
export DEBUG=1

# Run with debug output
python3 scripts/cache_manager.py 1.3.111
```

## 📊 Performance

### Optimization Features

- **Parallel Processing:** Multiple files processed simultaneously
- **Incremental Updates:** Only changed files are processed
- **Memory Efficient:** Large files processed in chunks
- **Fast Validation:** Quick syntax checking

### Benchmarks

- **Small Project (< 10 files):** < 1 second
- **Medium Project (10-50 files):** < 3 seconds
- **Large Project (50+ files):** < 10 seconds

## 🔧 Configuration

### Environment Variables

```bash
# Debug mode
export DEBUG=1

# Backup directory
export CACHE_BACKUP_DIR="cache_backups/"

# Log level
export LOG_LEVEL="INFO"
```

### Configuration File

Create `cache_config.json` for custom settings:

```json
{
  "backup_dir": "cache_backups/",
  "log_level": "INFO",
  "parallel_workers": 4,
  "validation_enabled": true,
  "auto_backup": true
}
```

## 🚀 Integration

### CI/CD Integration

#### GitHub Actions
```yaml
name: Update Cache
on:
  push:
    branches: [main]
jobs:
  update-cache:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Update cache version
      run: |
        python3 scripts/cache_manager.py 1.3.111
        git add .
        git commit -m "Update cache version to 1.3.111"
        git push
```

#### Heroku Deployment
```bash
# Add to build script
echo "Updating cache version..."
python3 scripts/cache_manager.py 1.3.111
echo "Cache version updated successfully"
```

### Development Workflow

#### Pre-commit Hook
```bash
#!/bin/sh
# .git/hooks/pre-commit
python3 scripts/validate_cache.py
if [ $? -ne 0 ]; then
    echo "Cache validation failed"
    exit 1
fi
```

#### Post-merge Hook
```bash
#!/bin/sh
# .git/hooks/post-merge
echo "Updating cache version after merge..."
python3 scripts/cache_manager.py 1.3.111
```

## 📝 Best Practices

### Version Management

1. **Increment Version:** Always increment version number
2. **Use Timestamps:** Include timestamp for additional cache busting
3. **Validate Changes:** Always validate after updates
4. **Create Backups:** Keep backups for rollback capability

### File Organization

1. **Consistent Naming:** Use consistent file naming conventions
2. **Relative Paths:** Prefer relative paths over absolute
3. **Resource Grouping:** Group related resources together
4. **Documentation:** Document any custom cache parameters

### Testing

1. **Unit Tests:** Test individual functions
2. **Integration Tests:** Test full workflow
3. **Validation Tests:** Test validation logic
4. **Performance Tests:** Test with large files

## 🤝 Contributing

### Adding New File Types

1. **Create Handler:** Add new file type handler
2. **Add Tests:** Create unit tests for new handler
3. **Update Documentation:** Document new file type support
4. **Test Integration:** Test with existing workflow

### Improving Performance

1. **Profile Code:** Identify bottlenecks
2. **Optimize Algorithms:** Improve processing speed
3. **Add Caching:** Cache frequently used data
4. **Parallel Processing:** Use multiple workers

## 📞 Support

### Getting Help

1. **Check Logs:** Review error logs for details
2. **Run Validation:** Use validation script to identify issues
3. **Check Documentation:** Review this README for solutions
4. **Create Issue:** Report bugs with detailed information

### Common Solutions

#### Cache Not Updating
```bash
# Check file permissions
ls -la bot/web_app/

# Run validation
python3 scripts/validate_cache.py

# Force update
python3 scripts/cache_manager.py 1.3.111 --no-backup
```

#### Backup Issues
```bash
# Check backup directory
ls -la cache_backups/

# Create backup directory
mkdir -p cache_backups/

# Fix permissions
chmod 755 cache_backups/
```

#### Validation Failures
```bash
# Run detailed validation
python3 scripts/validate_cache.py --verbose

# Check for syntax errors
python3 -m py_compile bot/web_app/script.js

# Use rollback if needed
python3 scripts/cache_manager.py 1.3.111 --rollback
```

---

**Last Updated**: 2025-09-07
**Version**: 1.0.0
**Maintained by**: Development Team