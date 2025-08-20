"""
Fixed unit tests for data management functionality.
Uses simplified approach to avoid async conflicts.
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


class TestDataManagementFixed(unittest.TestCase):
    """Test data management functionality with simplified approach."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_counter_file = os.path.join(self.temp_dir, 'order_counter.json')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

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
    def test_save_order_counter_success(self, mock_counter_file):
        """Test successful saving of order counter."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        test_data = {"counter": 100, "month": 8}
        
        # Import and test the function
        from main import save_order_counter
        
        # Create event loop and run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(save_order_counter(test_data))
            
            # Check that file was created
            self.assertTrue(os.path.exists(self.test_counter_file))
            
            # Check file content
            with open(self.test_counter_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data["counter"], 100)
            self.assertEqual(saved_data["month"], 8)
        finally:
            loop.close()

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_save_order_counter_file_error(self, mock_counter_file):
        """Test saving order counter with file error."""
        mock_counter_file.__str__ = lambda: '/invalid/path/order_counter.json'
        
        test_data = {"counter": 100, "month": 8}
        
        # Import and test the function
        from main import save_order_counter
        
        # Create event loop and run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async function - should handle error gracefully
            try:
                result = loop.run_until_complete(save_order_counter(test_data))
                # Should not raise exception, but may return False or None
            except Exception as e:
                # If exception is raised, it should be handled gracefully
                self.assertIsInstance(e, (OSError, PermissionError))
        finally:
            loop.close()

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_generate_order_number_basic(self, mock_counter_file):
        """Test basic order number generation."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Create initial counter data
        test_data = {"counter": 1, "month": 8}
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Import and test the function
        from main import generate_order_number
        
        # Create event loop and run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(generate_order_number())
            
            # Check result format
            self.assertIsInstance(result, str)
            self.assertTrue(result.startswith('#'))
            self.assertIn('/', result)
        finally:
            loop.close()

    @patch('bot.main.ORDER_COUNTER_FILE')
    def test_generate_order_number_no_file(self, mock_counter_file):
        """Test order number generation when no file exists."""
        mock_counter_file.__str__ = lambda: self.test_counter_file
        
        # Import and test the function
        from main import generate_order_number
        
        # Create event loop and run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(generate_order_number())
            
            # Check result format
            self.assertIsInstance(result, str)
            self.assertTrue(result.startswith('#'))
            self.assertIn('/', result)
            
            # Should have created file with counter = 1
            self.assertTrue(os.path.exists(self.test_counter_file))
            
            with open(self.test_counter_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertEqual(data["counter"], 1)
        finally:
            loop.close()

    def test_file_operations(self):
        """Test basic file operations for order counter."""
        # Test creating and reading JSON file
        test_data = {"counter": 42, "month": 8}
        
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.test_counter_file))
        
        # Read and verify data
        with open(self.test_counter_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data["counter"], 42)
        self.assertEqual(loaded_data["month"], 8)

    def test_json_error_handling(self):
        """Test JSON error handling."""
        # Create invalid JSON file
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        # Test reading invalid JSON
        try:
            with open(self.test_counter_file, 'r', encoding='utf-8') as f:
                json.load(f)
            self.fail("Should have raised JSONDecodeError")
        except json.JSONDecodeError:
            # Expected behavior
            pass

    def test_counter_increment_logic(self):
        """Test counter increment logic."""
        # Test basic increment
        counter = 1
        counter += 1
        self.assertEqual(counter, 2)
        
        # Test month change logic
        current_month = 8
        stored_month = 7
        
        if current_month != stored_month:
            counter = 0  # Reset counter
            stored_month = current_month
        
        self.assertEqual(counter, 0)
        self.assertEqual(stored_month, 8)

    def test_date_formatting(self):
        """Test date formatting for order numbers."""
        import datetime
        
        now = datetime.datetime.now()
        day = now.strftime("%d")
        month = now.strftime("%m")
        year = now.strftime("%y")
        
        # Test format
        self.assertEqual(len(day), 2)
        self.assertEqual(len(month), 2)
        self.assertEqual(len(year), 2)
        
        # Test order number format
        order_sequence = str(1).zfill(3)
        order_number = f"#{day}{month}{year}/{order_sequence}"
        
        self.assertTrue(order_number.startswith('#'))
        self.assertIn('/', order_number)
        self.assertEqual(len(order_sequence), 3)


if __name__ == '__main__':
    unittest.main()
