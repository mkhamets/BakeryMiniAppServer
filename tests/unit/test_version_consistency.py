#!/usr/bin/env python3
"""
Unit tests for version consistency across all files.
Ensures all resources have the same version v=1.3.18
"""

import os
import re
import unittest
from pathlib import Path


class TestVersionConsistency(unittest.TestCase):
    """Test suite for version consistency across all files."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.web_app_dir = self.project_root / "bot" / "web_app"
        self.expected_version = "1.3.18"
        
    def test_html_version_consistency(self):
        """Test that all version references in HTML files are consistent."""
        html_file = self.web_app_dir / "index.html"
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all version patterns in HTML
        version_patterns = re.findall(r'v=(\d+\.\d+\.\d+)', content)
        
        # Check that all versions match expected version
        for version in version_patterns:
            self.assertEqual(
                version, 
                self.expected_version,
                f"Version mismatch in {html_file}: found {version}, expected {self.expected_version}"
            )
            
        # Verify specific resources
        resources_to_check = [
            'main.min.css',
            'style.css', 
            'script.js',
            'logo-dark.svg',
            'logo.svg'
        ]
        
        for resource in resources_to_check:
            # Escape special regex characters in resource name
            escaped_resource = re.escape(resource)
            pattern = rf'{escaped_resource}\?v={self.expected_version}'
            match = re.search(pattern, content)
            self.assertIsNotNone(
                match, 
                f"Resource {resource} not found with version {self.expected_version} in {html_file}"
            )
            
    def test_javascript_version_consistency(self):
        """Test that all version references in JavaScript files are consistent."""
        js_file = self.web_app_dir / "script.js"
        
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Test CACHE_VERSION constant
        cache_version_match = re.search(r'const CACHE_VERSION = [\'"](\d+\.\d+\.\d+)[\'"]', content)
        self.assertIsNotNone(
            cache_version_match,
            f"CACHE_VERSION constant not found in {js_file}"
        )
        
        cache_version = cache_version_match.group(1)
        self.assertEqual(
            cache_version,
            self.expected_version,
            f"CACHE_VERSION mismatch in {js_file}: found {cache_version}, expected {self.expected_version}"
        )
        
        # Find all version patterns in JavaScript
        version_patterns = re.findall(r'v=(\d+\.\d+\.\d+)', content)
        
        # Check that all versions match expected version
        for version in version_patterns:
            self.assertEqual(
                version,
                self.expected_version,
                f"Version mismatch in {js_file}: found {version}, expected {self.expected_version}"
            )
            
        # Verify specific resources in JavaScript
        js_resources_to_check = [
            'bakery.svg',
            'crouasan.svg', 
            'bread1.svg',
            'cookie.svg',
            'Hleb.jpg'
        ]
        
        for resource in js_resources_to_check:
            pattern = rf'{resource}\?v={self.expected_version}'
            matches = re.findall(pattern, content)
            self.assertGreater(
                len(matches),
                0,
                f"Resource {resource} not found with version {self.expected_version} in {js_file}"
            )
            
    def test_no_old_versions_present(self):
        """Test that no old versions are present in any files."""
        old_versions = ['1.2.0', '1.2.1', '1.2.2', '1.2.3', '1.2.4', '1.2.5', '1.2.6', '1.2.7', '1.2.8', '1.2.9', '1.3.0']
        
        files_to_check = [
            self.web_app_dir / "index.html",
            self.web_app_dir / "script.js"
        ]
        
        for file_path in files_to_check:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for old_version in old_versions:
                # Look for old versions in version patterns
                old_version_patterns = re.findall(rf'v={old_version}', content)
                self.assertEqual(
                    len(old_version_patterns),
                    0,
                    f"Old version {old_version} found in {file_path}: {old_version_patterns}"
                )
                
    def test_version_count_consistency(self):
        """Test that the number of version references is consistent."""
        html_file = self.web_app_dir / "index.html"
        js_file = self.web_app_dir / "script.js"
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
            
        # Count expected version references
        html_versions = re.findall(rf'v={self.expected_version}', html_content)
        js_versions = re.findall(rf'v={self.expected_version}', js_content)
        
        # HTML should have 6 version references (CSS, JS, 3 images)
        self.assertEqual(
            len(html_versions),
            6,
            f"Expected 6 version references in HTML, found {len(html_versions)}"
        )
        
        # JavaScript should have 9 version references (4 category icons × 2 each + 1 background image)
        self.assertEqual(
            len(js_versions),
            9,
            f"Expected 9 version references in JavaScript, found {len(js_versions)}"
        )
        
    def test_file_existence(self):
        """Test that all referenced files actually exist."""
        html_file = self.web_app_dir / "index.html"
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract all file paths from HTML
        file_patterns = re.findall(r'src="([^"]+)"', content)
        file_patterns.extend(re.findall(r'href="([^"]+)"', content))
        
        for file_path in file_patterns:
            # Skip external URLs
            if file_path.startswith('http'):
                continue
                
            # Skip SVG fragment identifiers (like #beSVGID_1_)
            if file_path.startswith('#'):
                continue
                
            # Skip telephone links
            if file_path.startswith('tel:'):
                continue
                
            # Remove version parameters
            clean_path = file_path.split('?')[0]
            
            # Convert to absolute path
            if clean_path.startswith('/'):
                clean_path = clean_path[1:]  # Remove leading slash
                
            # Handle different path patterns
            if clean_path.startswith('bot-app/'):
                # These are served by the Flask app, so they exist in the web_app directory
                clean_path = clean_path.replace('bot-app/', 'bot/web_app/')
            elif clean_path.startswith('images/'):
                # These are relative to the web_app directory
                clean_path = f'bot/web_app/{clean_path}'
                
            full_path = self.project_root / clean_path
            
            self.assertTrue(
                full_path.exists(),
                f"Referenced file does not exist: {full_path}"
            )
            
    def test_css_file_versions(self):
        """Test that CSS files have correct version references."""
        css_file = self.web_app_dir / "style.css"
        
        if css_file.exists():
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for any version patterns in CSS
            version_patterns = re.findall(r'v=(\d+\.\d+\.\d+)', content)
            
            # CSS should contain the expected version reference
            self.assertIn(
                self.expected_version,
                version_patterns,
                f"CSS file should contain version {self.expected_version}, found: {version_patterns}"
            )
            
            # All versions in CSS should be the expected version
            for version in version_patterns:
                self.assertEqual(
                    version,
                    self.expected_version,
                    f"CSS file contains incorrect version {version}, expected {self.expected_version}"
                )
            
    def test_version_format_consistency(self):
        """Test that all version numbers follow the correct format."""
        files_to_check = [
            self.web_app_dir / "index.html",
            self.web_app_dir / "script.js"
        ]
        
        version_pattern = r'v=(\d+\.\d+\.\d+)'
        
        for file_path in files_to_check:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            versions = re.findall(version_pattern, content)
            
            for version in versions:
                # Check format: major.minor.patch
                parts = version.split('.')
                self.assertEqual(
                    len(parts),
                    3,
                    f"Version {version} in {file_path} does not follow major.minor.patch format"
                )
                
                # Check that all parts are numeric
                for part in parts:
                    self.assertTrue(
                        part.isdigit(),
                        f"Version part {part} in {version} is not numeric"
                    )


if __name__ == '__main__':
    unittest.main()
