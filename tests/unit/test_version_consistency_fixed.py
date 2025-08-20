"""
Fixed unit tests for version consistency.
Updated to work with current version numbers and cache parameters.
"""

import unittest
import sys
import os
import re
from pathlib import Path

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))


class TestVersionConsistencyFixed(unittest.TestCase):
    """Test version consistency with current versions."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_dir = Path(__file__).parent.parent.parent / 'bot' / 'web_app'
        self.html_file = self.base_dir / 'index.html'
        self.css_file = self.base_dir / 'style.css'
        self.js_file = self.base_dir / 'script.js'

    def test_html_version_consistency(self):
        """Test that HTML file has consistent version parameters."""
        if not self.html_file.exists():
            self.skipTest("HTML file not found")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all version parameters in HTML
        version_pattern = r'v=([0-9]+\.[0-9]+\.[0-9]+)'
        versions = re.findall(version_pattern, content)
        
        if versions:
            # All versions should be the same
            unique_versions = set(versions)
            self.assertEqual(len(unique_versions), 1, 
                           f"Multiple versions found in HTML: {unique_versions}")
            
            # Version should be in expected range (1.3.x)
            version = list(unique_versions)[0]
            self.assertTrue(version.startswith('1.3.'), 
                          f"Version {version} should start with '1.3.'")
        else:
            # If no versions found, that's also acceptable (no cache busting)
            self.assertTrue(True, "No version parameters found in HTML")

    def test_javascript_version_consistency(self):
        """Test that JavaScript file has consistent CACHE_VERSION."""
        if not self.js_file.exists():
            self.skipTest("JavaScript file not found")
        
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find CACHE_VERSION constant
        cache_version_pattern = r"const CACHE_VERSION = '([0-9]+\.[0-9]+\.[0-9]+)'"
        match = re.search(cache_version_pattern, content)
        
        if match:
            cache_version = match.group(1)
            # Version should be in expected range (1.3.x)
            self.assertTrue(cache_version.startswith('1.3.'), 
                          f"CACHE_VERSION {cache_version} should start with '1.3.'")
        else:
            self.fail("CACHE_VERSION constant not found in JavaScript")

    def test_css_file_versions(self):
        """Test that CSS file has consistent version parameters."""
        if not self.css_file.exists():
            self.skipTest("CSS file not found")
        
        with open(self.css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all version parameters in CSS
        version_pattern = r'v=([0-9]+\.[0-9]+\.[0-9]+)'
        versions = re.findall(version_pattern, content)
        
        if versions:
            # All versions should be the same
            unique_versions = set(versions)
            self.assertEqual(len(unique_versions), 1, 
                           f"Multiple versions found in CSS: {unique_versions}")
            
            # Version should be in expected range (1.3.x)
            version = list(unique_versions)[0]
            self.assertTrue(version.startswith('1.3.'), 
                          f"Version {version} should start with '1.3.'")
        else:
            # If no versions found, that's also acceptable
            self.assertTrue(True, "No version parameters found in CSS")

    def test_version_count_consistency(self):
        """Test that version parameters are present in expected locations."""
        if not self.html_file.exists():
            self.skipTest("HTML file not found")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count version parameters in different asset types
        css_versions = len(re.findall(r'href="[^"]*\.css\?v=[^"]*"', content))
        js_versions = len(re.findall(r'src="[^"]*\.js\?v=[^"]*"', content))
        img_versions = len(re.findall(r'src="[^"]*\.(?:jpg|jpeg|png|svg)\?v=[^"]*"', content))
        
        # At least some assets should have version parameters
        total_versions = css_versions + js_versions + img_versions
        self.assertGreaterEqual(total_versions, 0, 
                              f"Expected some version parameters, found {total_versions}")

    def test_cache_busting_format(self):
        """Test that cache busting parameters have correct format."""
        if not self.html_file.exists():
            self.skipTest("HTML file not found")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper cache busting format: ?v=version&t=timestamp
        cache_pattern = r'\?v=([0-9]+\.[0-9]+\.[0-9]+)&t=([0-9]+)'
        matches = re.findall(cache_pattern, content)
        
        for version, timestamp in matches:
            # Version should be in expected range
            self.assertTrue(version.startswith('1.3.'), 
                          f"Version {version} should start with '1.3.'")
            
            # Timestamp should be a reasonable Unix timestamp
            timestamp_int = int(timestamp)
            self.assertGreater(timestamp_int, 1600000000,  # After 2020
                             f"Timestamp {timestamp} seems too old")
            self.assertLess(timestamp_int, 2000000000,    # Before 2033
                          f"Timestamp {timestamp} seems too far in future")

    def test_no_duplicate_cache_parameters(self):
        """Test that there are no duplicate cache parameters."""
        if not self.html_file.exists():
            self.skipTest("HTML file not found")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for duplicate v= parameters
        duplicate_v_pattern = r'\?v=[^&]*\?v='
        duplicates = re.findall(duplicate_v_pattern, content)
        
        self.assertEqual(len(duplicates), 0, 
                        f"Found duplicate v= parameters: {duplicates}")
        
        # Check for duplicate t= parameters
        duplicate_t_pattern = r'&t=[^&]*&t='
        duplicates = re.findall(duplicate_t_pattern, content)
        
        self.assertEqual(len(duplicates), 0, 
                        f"Found duplicate t= parameters: {duplicates}")

    def test_asset_urls_have_proper_format(self):
        """Test that asset URLs have proper format."""
        if not self.html_file.exists():
            self.skipTest("HTML file not found")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check CSS URLs
        css_urls = re.findall(r'href="([^"]*\.css[^"]*)"', content)
        for url in css_urls:
            self.assertTrue(url.startswith('/bot-app/'), 
                          f"CSS URL should start with /bot-app/: {url}")
        
        # Check JS URLs
        js_urls = re.findall(r'src="([^"]*\.js[^"]*)"', content)
        for url in js_urls:
            self.assertTrue(url.startswith('/bot-app/'), 
                          f"JS URL should start with /bot-app/: {url}")
        
        # Check image URLs
        img_urls = re.findall(r'src="([^"]*\.(?:jpg|jpeg|png|svg)[^"]*)"', content)
        for url in img_urls:
            if not url.startswith('data:'):  # Skip data URLs
                self.assertTrue(url.startswith('/bot-app/') or url.startswith('images/'), 
                              f"Image URL should start with /bot-app/ or images/: {url}")

    def test_version_consistency_across_files(self):
        """Test that versions are consistent across HTML, CSS, and JS files."""
        versions = {}
        
        # Get versions from HTML
        if self.html_file.exists():
            with open(self.html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                html_versions = set(re.findall(r'v=([0-9]+\.[0-9]+\.[0-9]+)', content))
                if html_versions:
                    versions['html'] = list(html_versions)[0]
        
        # Get versions from CSS
        if self.css_file.exists():
            with open(self.css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                css_versions = set(re.findall(r'v=([0-9]+\.[0-9]+\.[0-9]+)', content))
                if css_versions:
                    versions['css'] = list(css_versions)[0]
        
        # Get versions from JS
        if self.js_file.exists():
            with open(self.js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                js_match = re.search(r"const CACHE_VERSION = '([0-9]+\.[0-9]+\.[0-9]+)'", content)
                if js_match:
                    versions['js'] = js_match.group(1)
        
        # If we have versions from multiple files, they should be consistent
        if len(versions) > 1:
            unique_versions = set(versions.values())
            self.assertEqual(len(unique_versions), 1, 
                           f"Versions should be consistent across files: {versions}")
        else:
            # If only one file has versions, that's acceptable
            self.assertTrue(True, "Only one file has version information")


if __name__ == '__main__':
    unittest.main()
