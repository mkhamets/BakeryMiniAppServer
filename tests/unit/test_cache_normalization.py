"""
Unit tests for cache normalization functionality.
Tests the normalize_cache.py script and related cache busting features.
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from normalize_cache import normalize_cache_params, process_file


class TestCacheNormalization(unittest.TestCase):
    """Test cache parameter normalization."""

    def test_normalize_simple_cache_params(self):
        """Test normalization of simple cache parameters."""
        content = 'script.js?v=1.3.37&t=1234567890'
        normalized = normalize_cache_params(content)
        self.assertEqual(normalized, 'script.js?v=1.3.37&t=1234567890')

    def test_normalize_duplicate_cache_params(self):
        """Test normalization of duplicate cache parameters."""
        content = 'script.js?v=1.3.37?v=1.3.38?v=1.3.39&t=1234567890&t=9876543210&t=5555555555'
        normalized = normalize_cache_params(content)
        # Should keep only the first v and t parameters
        self.assertIn('script.js?v=1.3.37&t=1234567890', normalized)
        self.assertNotIn('v=1.3.38', normalized)
        self.assertNotIn('v=1.3.39', normalized)
        self.assertNotIn('t=9876543210', normalized)
        self.assertNotIn('t=5555555555', normalized)

    def test_normalize_mixed_cache_params(self):
        """Test normalization of mixed cache parameters."""
        content = '''
        <link href="style.css?v=1.3.37?v=1.3.38&t=1234567890&t=9876543210" rel="stylesheet">
        <script src="script.js?v=1.3.39?v=1.3.40&t=5555555555&t=6666666666"></script>
        <img src="image.jpg?v=1.3.41&t=7777777777">
        '''
        normalized = normalize_cache_params(content)
        
        # Check that duplicates are removed
        self.assertIn('style.css?v=1.3.37&t=1234567890', normalized)
        self.assertNotIn('v=1.3.38', normalized)
        self.assertNotIn('t=9876543210', normalized)
        
        self.assertIn('script.js?v=1.3.39&t=5555555555', normalized)
        self.assertNotIn('v=1.3.40', normalized)
        self.assertNotIn('t=6666666666', normalized)
        
        # Single parameters should remain unchanged
        self.assertIn('image.jpg?v=1.3.41&t=7777777777', normalized)

    def test_normalize_complex_urls(self):
        """Test normalization of complex URLs with cache parameters."""
        content = '''
        https://example.com/bot-app/script.js?v=1.3.37?v=1.3.38&t=1234567890&t=9876543210
        https://example.com/bot-app/style.css?v=1.3.39&t=5555555555
        https://example.com/bot-app/images/icon.svg?v=1.3.40?v=1.3.41&t=7777777777&t=8888888888
        '''
        normalized = normalize_cache_params(content)
        
        # Check that complex URLs are handled correctly
        self.assertIn('https://example.com/bot-app/script.js?v=1.3.37&t=1234567890', normalized)
        self.assertNotIn('v=1.3.38', normalized)
        self.assertNotIn('t=9876543210', normalized)
        
        self.assertIn('https://example.com/bot-app/style.css?v=1.3.39&t=5555555555', normalized)
        
        self.assertIn('https://example.com/bot-app/images/icon.svg?v=1.3.40&t=7777777777', normalized)
        self.assertNotIn('v=1.3.41', normalized)
        self.assertNotIn('t=8888888888', normalized)

    def test_normalize_no_cache_params(self):
        """Test normalization when no cache parameters are present."""
        content = '''
        <link href="style.css" rel="stylesheet">
        <script src="script.js"></script>
        <img src="image.jpg">
        '''
        normalized = normalize_cache_params(content)
        self.assertEqual(normalized, content)

    def test_normalize_only_version_param(self):
        """Test normalization when only version parameter is present."""
        content = 'script.js?v=1.3.37'
        normalized = normalize_cache_params(content)
        self.assertEqual(normalized, 'script.js?v=1.3.37')

    def test_normalize_only_timestamp_param(self):
        """Test normalization when only timestamp parameter is present."""
        content = 'script.js&t=1234567890'
        normalized = normalize_cache_params(content)
        self.assertEqual(normalized, 'script.js&t=1234567890')

    def test_normalize_malformed_params(self):
        """Test normalization of malformed cache parameters."""
        content = 'script.js?v=1.3.37&t=1234567890?v=1.3.38&t=9876543210'
        normalized = normalize_cache_params(content)
        # Should handle malformed parameters gracefully
        self.assertIn('script.js?v=1.3.37&t=1234567890', normalized)
        self.assertNotIn('v=1.3.38', normalized)
        self.assertNotIn('t=9876543210', normalized)


class TestCacheFileProcessing(unittest.TestCase):
    """Test file processing for cache normalization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.html')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_process_file_with_duplicates(self):
        """Test processing a file with duplicate cache parameters."""
        content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <link href="style.css?v=1.3.37?v=1.3.38&t=1234567890&t=9876543210" rel="stylesheet">
            <script src="script.js?v=1.3.39?v=1.3.40&t=5555555555&t=6666666666"></script>
        </head>
        <body>
            <img src="image.jpg?v=1.3.41&t=7777777777">
        </body>
        </html>
        '''
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Process the file
        process_file(Path(self.test_file))
        
        # Read the processed file
        with open(self.test_file, 'r', encoding='utf-8') as f:
            processed_content = f.read()
        
        # Check that duplicates are removed
        self.assertIn('style.css?v=1.3.37&t=1234567890', processed_content)
        self.assertNotIn('v=1.3.38', processed_content)
        self.assertNotIn('t=9876543210', processed_content)
        
        self.assertIn('script.js?v=1.3.39&t=5555555555', processed_content)
        self.assertNotIn('v=1.3.40', processed_content)
        self.assertNotIn('t=6666666666', processed_content)
        
        self.assertIn('image.jpg?v=1.3.41&t=7777777777', processed_content)

    def test_process_file_without_duplicates(self):
        """Test processing a file without duplicate cache parameters."""
        content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <link href="style.css?v=1.3.37&t=1234567890" rel="stylesheet">
            <script src="script.js?v=1.3.38&t=9876543210"></script>
        </head>
        <body>
            <img src="image.jpg?v=1.3.39&t=5555555555">
        </body>
        </html>
        '''
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Process the file
        process_file(Path(self.test_file))
        
        # Read the processed file
        with open(self.test_file, 'r', encoding='utf-8') as f:
            processed_content = f.read()
        
        # Content should remain unchanged
        self.assertEqual(processed_content, content)

    def test_process_nonexistent_file(self):
        """Test processing a non-existent file."""
        nonexistent_file = Path(self.temp_dir) / 'nonexistent.html'
        
        # Should not raise an exception
        try:
            process_file(nonexistent_file)
        except Exception as e:
            self.fail(f"Processing non-existent file should not raise exception: {e}")

    def test_process_file_with_encoding_issues(self):
        """Test processing a file with encoding issues."""
        # Create a file with invalid encoding
        with open(self.test_file, 'wb') as f:
            f.write(b'<html>\xff\xfe<script src="test.js?v=1.3.37&t=1234567890"></script></html>')
        
        # Should handle encoding issues gracefully
        try:
            process_file(Path(self.test_file))
        except Exception as e:
            # Should not raise a critical exception
            self.assertIsInstance(e, (UnicodeDecodeError, UnicodeError))


class TestCacheBustingIntegration(unittest.TestCase):
    """Test integration with cache busting functionality."""

    def test_cache_busting_patterns(self):
        """Test various cache busting patterns."""
        test_cases = [
            # Simple case
            ('script.js?v=1.3.37&t=1234567890', 'script.js?v=1.3.37&t=1234567890'),
            
            # Duplicate version
            ('script.js?v=1.3.37?v=1.3.38&t=1234567890', 'script.js?v=1.3.37&t=1234567890'),
            
            # Duplicate timestamp
            ('script.js?v=1.3.37&t=1234567890&t=9876543210', 'script.js?v=1.3.37&t=1234567890'),
            
            # Both duplicates
            ('script.js?v=1.3.37?v=1.3.38&t=1234567890&t=9876543210', 'script.js?v=1.3.37&t=1234567890'),
            
            # Complex URL
            ('https://example.com/bot-app/script.js?v=1.3.37?v=1.3.38&t=1234567890&t=9876543210', 
             'https://example.com/bot-app/script.js?v=1.3.37&t=1234567890'),
        ]
        
        for input_content, expected_output in test_cases:
            with self.subTest(input_content=input_content):
                normalized = normalize_cache_params(input_content)
                self.assertEqual(normalized, expected_output)

    def test_cache_busting_file_types(self):
        """Test cache busting with different file types."""
        file_types = ['css', 'js', 'png', 'jpg', 'jpeg', 'svg', 'ico']
        
        for file_type in file_types:
            with self.subTest(file_type=file_type):
                content = f'file.{file_type}?v=1.3.37?v=1.3.38&t=1234567890&t=9876543210'
                normalized = normalize_cache_params(content)
                
                # Should normalize to first parameters
                expected = f'file.{file_type}?v=1.3.37&t=1234567890'
                self.assertEqual(normalized, expected)


if __name__ == '__main__':
    unittest.main()
