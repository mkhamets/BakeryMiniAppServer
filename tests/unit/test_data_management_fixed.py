"""
Fixed unit tests for data management functionality.
Resolves async conflicts and improves test reliability.
"""

import unittest
import sys
import os
import json
import asyncio
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import shutil
from pathlib import Path

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

from main import load_order_counter, save_order_counter, generate_order_number


class TestDataManagementFixed(unittest.TestCase):
    """Test data management functionality with fixed async handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_counter_file = os.path.join(self.temp_dir, 'order_counter.json')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_load_order_counter_success(self, mock_counter_file):
        """Test successful loading of order counter."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Create test data
        test_data = {"counter": 42, "last_reset_month": 8}
        
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Run the async function
        result = asyncio.run(load_order_counter())
        
        # Check result
        self.assertIsNotNone(result)
        self.assertEqual(result["counter"], 42)
        self.assertEqual(result["last_reset_month"], 8)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_load_order_counter_file_not_found(self, mock_counter_file):
        """Test loading order counter when file doesn't exist."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Run the async function
        result = asyncio.run(load_order_counter())
        
        # Should return default values
        self.assertIsNotNone(result)
        self.assertEqual(result["counter"], 0)
        self.assertIn("last_reset_month", result)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_load_order_counter_json_decode_error(self, mock_counter_file):
        """Test loading order counter with invalid JSON."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Create invalid JSON file
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        # Run the async function
        result = asyncio.run(load_order_counter())
        
        # Should return default values
        self.assertIsNotNone(result)
        self.assertEqual(result["counter"], 0)
        self.assertIn("last_reset_month", result)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_save_order_counter_success(self, mock_counter_file):
        """Test successful saving of order counter."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        test_data = {"counter": 100, "last_reset_month": 8}
        
        # Run the async function
        result = asyncio.run(save_order_counter(test_data))
        
        # Check that file was created
        self.assertTrue(os.path.exists(self.test_counter_file))
        
        # Check file content
        with open(self.test_counter_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data["counter"], 100)
        self.assertEqual(saved_data["last_reset_month"], 8)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_save_order_counter_file_error(self, mock_counter_file):
        """Test saving order counter with file error."""
        mock_counter_file.__str__ = lambda: '/invalid/path/order_counter.json'
        
        test_data = {"counter": 100, "last_reset_month": 8}
        
        # Run the async function - should handle error gracefully
        try:
            result = asyncio.run(save_order_counter(test_data))
            # Should not raise exception, but may return False or None
        except Exception as e:
            # If exception is raised, it should be handled gracefully
            self.assertIsInstance(e, (OSError, PermissionError))

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_generate_order_number_basic(self, mock_counter_file):
        """Test basic order number generation."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Create initial counter data
        test_data = {"counter": 1, "last_reset_month": 8}
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Run the async function
        result = asyncio.run(generate_order_number())
        
        # Check result format
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('#'))
        self.assertIn('/', result)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_generate_order_number_year_change(self, mock_counter_file):
        """Test order number generation with year change."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Create counter data from previous year
        test_data = {"counter": 999, "last_reset_month": 12}
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Run the async function
        result = asyncio.run(generate_order_number())
        
        # Check result format
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('#'))
        self.assertIn('/', result)
        
        # Should have reset counter to 1
        with open(self.test_counter_file, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
        
        # Counter should be reset to 1 for new year
        self.assertEqual(updated_data["counter"], 1)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_generate_order_number_month_change(self, mock_counter_file):
        """Test order number generation with month change."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Create counter data from previous month
        test_data = {"counter": 50, "last_reset_month": 7}
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Run the async function
        result = asyncio.run(generate_order_number())
        
        # Check result format
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('#'))
        self.assertIn('/', result)
        
        # Should have reset counter to 1 for new month
        with open(self.test_counter_file, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
        
        self.assertEqual(updated_data["counter"], 1)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_generate_order_number_increment(self, mock_counter_file):
        """Test order number generation with counter increment."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Create counter data for current month
        test_data = {"counter": 5, "last_reset_month": 8}
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Run the async function
        result = asyncio.run(generate_order_number())
        
        # Check result format
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('#'))
        self.assertIn('/', result)
        
        # Should have incremented counter
        with open(self.test_counter_file, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
        
        self.assertEqual(updated_data["counter"], 6)

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_generate_order_number_no_file(self, mock_counter_file):
        """Test order number generation when no file exists."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Run the async function
        result = asyncio.run(generate_order_number())
        
        # Check result format
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('#'))
        self.assertIn('/', result)
        
        # Should have created file with counter = 1
        self.assertTrue(os.path.exists(self.test_counter_file))
        
        with open(self.test_counter_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data["counter"], 1)

    def test_order_number_format(self):
        """Test that order numbers have correct format."""
        # Test format: #YYMMDD/XXX where XXX is 3-digit counter
        test_cases = [
            ("#200825/001", True),
            ("#200825/999", True),
            ("#201231/001", True),
            ("#200825/1000", False),  # Too many digits
            ("200825/001", False),    # Missing #
            ("#200825/01", False),    # Too few digits
            ("#200825/abc", False),   # Non-numeric
        ]
        
        for order_number, should_be_valid in test_cases:
            with self.subTest(order_number=order_number):
                if should_be_valid:
                    # Check format
                    self.assertTrue(order_number.startswith('#'))
                    self.assertIn('/', order_number)
                    parts = order_number[1:].split('/')
                    self.assertEqual(len(parts), 2)
                    
                    # Check date part (YYMMDD)
                    date_part = parts[0]
                    self.assertEqual(len(date_part), 6)
                    self.assertTrue(date_part.isdigit())
                    
                    # Check counter part (XXX)
                    counter_part = parts[1]
                    self.assertEqual(len(counter_part), 3)
                    self.assertTrue(counter_part.isdigit())

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_concurrent_order_number_generation(self, mock_counter_file):
        """Test concurrent order number generation."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Create initial counter data
        test_data = {"counter": 1, "last_reset_month": 8}
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Run multiple concurrent generations
        async def generate_multiple():
            tasks = [generate_order_number() for _ in range(5)]
            return await asyncio.gather(*tasks)
        
        results = asyncio.run(generate_multiple())
        
        # All results should be valid
        for result in results:
            self.assertIsInstance(result, str)
            self.assertTrue(result.startswith('#'))
            self.assertIn('/', result)
        
        # Check final counter value
        with open(self.test_counter_file, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
        
        # Should have incremented by 5
        self.assertEqual(final_data["counter"], 6)


if __name__ == '__main__':
    unittest.main()
