#!/usr/bin/env python3
"""
Test script for cache manager functionality
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from cache_manager import CacheManager

def create_test_files():
    """Create test files for testing"""
    test_dir = Path(tempfile.mkdtemp())
    
    # Create test HTML file
    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="style.css?v=1.3.100&t=1234567890">
    <script src="script.js?v=1.3.100&t=1234567890"></script>
</head>
<body>
    <img src="images/logo.svg?v=1.3.100&t=1234567890">
</body>
</html>
'''
    
    # Create test CSS file
    css_content = '''
body {
    background-image: url('images/bg.jpg?v=1.3.100&t=1234567890');
}
'''
    
    # Create test JS file
    js_content = '''
const CACHE_VERSION = '1.3.100';
const imageUrl = 'images/icon.svg?v=1.3.100&t=1234567890';
'''
    
    # Create test SVG file
    svg_content = '''
<svg xmlns="http://www.w3.org/2000/svg">
    <use xlink:href="sprite.svg#vegan"></use>
</svg>
'''
    
    # Write test files
    (test_dir / "index.html").write_text(html_content)
    (test_dir / "style.css").write_text(css_content)
    (test_dir / "script.js").write_text(js_content)
    (test_dir / "sprite.svg").write_text(svg_content)
    
    return test_dir

def test_cache_manager():
    """Test cache manager functionality"""
    print("🧪 Testing Cache Manager...")
    
    # Create test files
    test_dir = create_test_files()
    print(f"📁 Created test files in: {test_dir}")
    
    try:
        # Create a mock cache manager for testing
        class TestCacheManager(CacheManager):
            def __init__(self, version, timestamp=None, backup=False):
                super().__init__(version, timestamp, backup)
                # Override the webapp directory to use test directory
                self.webapp_dir = test_dir
                self.files = [
                    test_dir / "index.html",
                    test_dir / "style.css",
                    test_dir / "script.js",
                    test_dir / "sprite.svg"
                ]
        
        # Test version update
        manager = TestCacheManager("1.3.109", 1756284000, backup=False)
        
        print("🔄 Testing cache version update...")
        if manager.update_cache_versions():
            print("✅ Cache update successful!")
            
            # Verify changes
            print("🔍 Verifying changes...")
            if manager.validate_changes():
                print("✅ Validation successful!")
                manager.print_summary()
            else:
                print("❌ Validation failed!")
                return False
        else:
            print("❌ Cache update failed!")
            return False
        
        # Test validation
        print("\n🔍 Testing validation...")
        validator = TestCacheManager("1.3.109", 1756284000, backup=False)
        if validator.validate_changes():
            print("✅ Validation test successful!")
        else:
            print("❌ Validation test failed!")
            return False
        
        return True
        
    finally:
        # Cleanup test files
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test directory: {test_dir}")

def test_validation():
    """Test validation functionality"""
    print("\n🧪 Testing Validation...")
    
    # Create test files with issues
    test_dir = create_test_files()
    
    try:
        # Add some issues to test files
        html_file = test_dir / "index.html"
        content = html_file.read_text()
        # Add duplicate cache parameters
        content = content.replace('script.js?v=1.3.100&t=1234567890', 
                                'script.js?v=1.3.100&t=1234567890&v=1.3.101&t=1234567891')
        html_file.write_text(content)
        
        # Test validation
        from validate_cache import CacheValidator
        
        class TestValidator(CacheValidator):
            def __init__(self):
                super().__init__()
                self.webapp_dir = test_dir
                self.files = [
                    test_dir / "index.html",
                    test_dir / "style.css",
                    test_dir / "script.js",
                    test_dir / "sprite.svg"
                ]
        
        validator = TestValidator()
        if not validator.validate_all():
            print("✅ Validation correctly detected issues!")
            validator.print_issues()
            return True
        else:
            print("❌ Validation should have detected issues!")
            return False
            
    finally:
        shutil.rmtree(test_dir)

def main():
    """Main test function"""
    print("🚀 Cache Manager Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Cache Manager
    if test_cache_manager():
        tests_passed += 1
        print("✅ Test 1: Cache Manager - PASSED")
    else:
        print("❌ Test 1: Cache Manager - FAILED")
    
    # Test 2: Validation
    if test_validation():
        tests_passed += 1
        print("✅ Test 2: Validation - PASSED")
    else:
        print("❌ Test 2: Validation - FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

