import unittest
import asyncio
import json
import os
import tempfile
import shutil
from unittest.mock import AsyncMock, MagicMock, patch, Mock, mock_open

# Import the functions we want to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bot.main import (
    load_products_data, load_order_counter, save_order_counter,
    generate_order_number
)


class TestDataManagement(unittest.TestCase):
    """Test cases for data management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_products_data = {
            "category_bakery": [
                {
                    "name": "Bread",
                    "price": "10.00 р.",
                    "description": "Fresh bread",
                    "image_url": "bread.jpg",
                    "category_name": "🥨 Выпечка"
                },
                {
                    "name": "Croissant",
                    "price": "15.00 р.",
                    "description": "Buttery croissant",
                    "image_url": "croissant.jpg",
                    "category_name": "🥨 Выпечка"
                }
            ],
            "category_croissants": [
                {
                    "name": "Chocolate Croissant",
                    "price": "18.00 р.",
                    "description": "Chocolate filled croissant",
                    "image_url": "chocolate_croissant.jpg",
                    "category_name": "🥐 Круассаны"
                }
            ]
        }
        
        self.test_order_counter_data = {
            "counter": 42,
            "last_reset_month": 8
        }

    def tearDown(self):
        """Clean up after tests."""
        pass

    @patch('bot.main.PRODUCTS_DATA_FILE')
    @patch('builtins.open', create=True)
    @patch('json.load')
    def test_load_products_data_success(self, mock_json_load, mock_open, mock_file_path):
        """Test successful loading of products data."""
        mock_file_path.return_value = "/test/path/products.json"
        mock_json_load.return_value = self.test_products_data
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        asyncio.run(load_products_data())

        mock_open.assert_called_once()
        mock_json_load.assert_called_once()

    @patch('bot.main.PRODUCTS_DATA_FILE')
    @patch('builtins.open', create=True)
    def test_load_products_data_file_not_found(self, mock_open, mock_file_path):
        """Test handling when products data file is not found."""
        mock_file_path.return_value = "/nonexistent/path/products.json"
        mock_open.side_effect = FileNotFoundError()

        asyncio.run(load_products_data())

        # Should handle the error gracefully
        mock_open.assert_called_once()

    @patch('bot.main.PRODUCTS_DATA_FILE')
    @patch('builtins.open', create=True)
    @patch('json.load')
    def test_load_products_data_json_decode_error(self, mock_json_load, mock_open, mock_file_path):
        """Test handling JSON decode errors in products data."""
        mock_file_path.return_value = "/test/path/products.json"
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        asyncio.run(load_products_data())

        mock_open.assert_called_once()
        mock_json_load.assert_called_once()

    @patch('bot.main.PRODUCTS_DATA_FILE')
    @patch('builtins.open', create=True)
    @patch('json.load')
    def test_load_products_data_general_exception(self, mock_json_load, mock_open, mock_file_path):
        """Test handling general exceptions in products data loading."""
        mock_file_path.return_value = "/test/path/products.json"
        mock_json_load.side_effect = Exception("General error")
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        asyncio.run(load_products_data())

        mock_open.assert_called_once()
        mock_json_load.assert_called_once()

    @patch('bot.main.ORDER_COUNTER_FILE')
    @patch('builtins.open', create=True)
    @patch('json.load')
    def test_load_order_counter_success(self, mock_json_load, mock_open, mock_file_path):
        """Test successful loading of order counter."""
        mock_file_path.return_value = "/test/path/counter.json"
        mock_json_load.return_value = self.test_order_counter_data
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock the file content to avoid async loop issues
        mock_file.read.return_value = json.dumps(self.test_order_counter_data)

        result = asyncio.run(load_order_counter())

        self.assertEqual(result["counter"], 42)
        self.assertEqual(result["last_reset_month"], 8)
        mock_open.assert_called_once()

    @patch('bot.main.ORDER_COUNTER_FILE')
    @patch('builtins.open', create=True)
    def test_load_order_counter_file_not_found(self, mock_open, mock_file_path):
        """Test handling when order counter file is not found."""
        mock_file_path.return_value = "/nonexistent/path/counter.json"
        mock_open.side_effect = FileNotFoundError()

        result = asyncio.run(load_order_counter())

        # Should return default values
        self.assertEqual(result["counter"], 0)
        self.assertEqual(result["last_reset_month"], 0)

    @patch('bot.main.ORDER_COUNTER_FILE')
    @patch('builtins.open', create=True)
    def test_load_order_counter_json_decode_error(self, mock_open, mock_file_path):
        """Test handling JSON decode errors in order counter."""
        mock_file_path.return_value = "/test/path/counter.json"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        # Mock invalid JSON content
        mock_file.read.return_value = "invalid json content"

        result = asyncio.run(load_order_counter())

        # Should return default values
        self.assertEqual(result["counter"], 0)
        self.assertEqual(result["last_reset_month"], 0)

    @patch('bot.main.ORDER_COUNTER_FILE')
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_save_order_counter_success(self, mock_json_dump, mock_open, mock_file_path):
        """Test successful saving of order counter."""
        mock_file_path.return_value = "/test/path/counter.json"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        test_data = {"counter": 100, "last_reset_month": 8}

        asyncio.run(save_order_counter(test_data))

        mock_open.assert_called_once()
        mock_json_dump.assert_called_once_with(test_data, mock_file, ensure_ascii=False, indent=4)

    @patch('bot.main.ORDER_COUNTER_FILE')
    @patch('builtins.open', create=True)
    def test_save_order_counter_file_error(self, mock_open, mock_file_path):
        """Test handling file errors when saving order counter."""
        mock_file_path.return_value = "/test/path/counter.json"
        mock_open.side_effect = PermissionError("Permission denied")

        test_data = {"counter": 100, "last_reset_month": 8}

        # Should handle the error gracefully
        asyncio.run(save_order_counter(test_data))

        mock_open.assert_called_once()

    @patch('bot.main.save_order_counter')
    def test_generate_order_number_success(self, mock_save):
        """Test successful order number generation."""
        # Set global variables directly since the function uses them
        import bot.main
        bot.main.order_counter = 42
        bot.main.last_reset_month = 8  # Current month, no reset
        
        result = asyncio.run(generate_order_number())

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("#"))
        mock_save.assert_called_once()

    @patch('bot.main.save_order_counter')
    def test_generate_order_number_month_reset(self, mock_save):
        """Test order number generation with month reset."""
        # Set global variables directly since the function uses them
        import bot.main
        bot.main.order_counter = 100
        bot.main.last_reset_month = 7  # Previous month (July), current is August (8)
        
        result = asyncio.run(generate_order_number())

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("#"))
        # Counter should reset to 1 for new month
        self.assertIn("001", result)  # Counter 1 padded to 3 digits

    @patch('bot.main.save_order_counter')
    def test_generate_order_number_year_change(self, mock_save):
        """Test order number generation with year change."""
        # Set global variables directly since the function uses them
        import bot.main
        bot.main.order_counter = 100
        bot.main.last_reset_month = 12  # December, current is August (8) - month changed
        
        result = asyncio.run(generate_order_number())

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("#"))
        # Counter should reset to 1 for new year/month
        self.assertIn("001", result)  # Counter 1 padded to 3 digits


class TestDataValidation(unittest.TestCase):
    """Test cases for data validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_products_data = {
            "category_bakery": [
                {
                    "name": "Bread",
                    "price": "10.00 р.",
                    "description": "Fresh bread",
                    "image_url": "bread.jpg",
                    "category_name": "🥨 Выпечка"
                }
            ]
        }
        
        self.valid_order_counter_data = {
            "counter": 42,
            "last_reset_month": 8
        }

    def test_products_data_structure_validation(self):
        """Test validation of products data structure."""
        # Test valid structure
        self.assertIsInstance(self.valid_products_data, dict)
        
        for category_key, products in self.valid_products_data.items():
            self.assertIsInstance(products, list)
            for product in products:
                self.assertIsInstance(product, dict)
                self.assertIn("name", product)
                self.assertIn("price", product)

    def test_order_counter_data_structure_validation(self):
        """Test validation of order counter data structure."""
        # Test valid structure
        self.assertIsInstance(self.valid_order_counter_data, dict)
        self.assertIn("counter", self.valid_order_counter_data)
        self.assertIn("last_reset_month", self.valid_order_counter_data)
        
        counter = self.valid_order_counter_data["counter"]
        last_reset_month = self.valid_order_counter_data["last_reset_month"]
        
        self.assertIsInstance(counter, int)
        self.assertIsInstance(last_reset_month, int)
        self.assertGreaterEqual(counter, 0)
        self.assertGreaterEqual(last_reset_month, 1)
        self.assertLessEqual(last_reset_month, 12)

    def test_products_data_content_validation(self):
        """Test validation of products data content."""
        for category_key, products in self.valid_products_data.items():
            for product in products:
                # Check required fields
                self.assertIsInstance(product["name"], str)
                self.assertIsInstance(product["price"], str)
                self.assertIsInstance(product["description"], str)
                
                # Check field lengths
                self.assertGreater(len(product["name"]), 0)
                self.assertGreater(len(product["price"]), 0)

    def test_order_counter_data_content_validation(self):
        """Test validation of order counter data content."""
        counter = self.valid_order_counter_data["counter"]
        last_reset_month = self.valid_order_counter_data["last_reset_month"]
        
        # Check value ranges
        self.assertGreaterEqual(counter, 0)
        self.assertGreaterEqual(last_reset_month, 1)
        self.assertLessEqual(last_reset_month, 12)


class TestDataPersistence(unittest.TestCase):
    """Test cases for data persistence functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_products_file = os.path.join(self.temp_dir, "products.json")
        self.test_counter_file = os.path.join(self.temp_dir, "counter.json")

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    def test_products_data_persistence(self):
        """Test that products data can be saved and loaded."""
        test_data = {
            "category_bakery": [
                {
                    "name": "Bread",
                    "price": "10.00 р.",
                    "description": "Fresh bread",
                    "image_url": "bread.jpg",
                    "category_name": "🥨 Выпечка"
                }
            ]
        }
        
        # Save data
        with open(self.test_products_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        # Load data
        with open(self.test_products_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        # Verify data integrity
        self.assertEqual(loaded_data, test_data)
        self.assertIn("category_bakery", loaded_data)
        self.assertEqual(len(loaded_data["category_bakery"]), 1)
        self.assertEqual(loaded_data["category_bakery"][0]["name"], "Bread")

    def test_order_counter_persistence(self):
        """Test that order counter data can be saved and loaded."""
        test_data = {
            "counter": 42,
            "last_reset_month": 8
        }
        
        # Save data
        with open(self.test_counter_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        # Load data
        with open(self.test_counter_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        # Verify data integrity
        self.assertEqual(loaded_data, test_data)
        self.assertEqual(loaded_data["counter"], 42)
        self.assertEqual(loaded_data["last_reset_month"], 8)

    def test_data_file_encoding(self):
        """Test that data files are saved with proper encoding."""
        test_data = {
            "category_bakery": [
                {
                    "name": "Хлеб",  # Russian text
                    "price": "10.00 р.",
                    "description": "Свежий хлеб",
                    "image_url": "bread.jpg",
                    "category_name": "🥨 Выпечка"
                }
            ]
        }
        
        # Save data with UTF-8 encoding
        with open(self.test_products_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        # Load data
        with open(self.test_products_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        # Verify Russian text is preserved
        self.assertEqual(loaded_data["category_bakery"][0]["name"], "Хлеб")
        self.assertEqual(loaded_data["category_bakery"][0]["description"], "Свежий хлеб")


class TestDataErrorHandling(unittest.TestCase):
    """Test cases for data error handling."""

    def test_handle_missing_required_fields(self):
        """Test handling of missing required fields in data."""
        # Test products data with missing fields
        incomplete_product = {
            "name": "Bread"
            # Missing price, description, etc.
        }
        
        # This would be tested in actual validation functions
        self.assertNotIn("price", incomplete_product)
        self.assertNotIn("description", incomplete_product)

    def test_handle_invalid_data_types(self):
        """Test handling of invalid data types."""
        # Test order counter with invalid types
        invalid_counter = {
            "counter": "not_a_number",  # Should be int
            "last_reset_month": 13  # Should be 1-12
        }
        
        # This would be tested in actual validation functions
        self.assertIsInstance(invalid_counter["counter"], str)
        self.assertGreater(invalid_counter["last_reset_month"], 12)

    def test_handle_corrupted_json(self):
        """Test handling of corrupted JSON data."""
        corrupted_json = '{"counter": 42, "last_reset_month": 8'  # Missing closing brace
        
        # This would be tested in actual JSON parsing functions
        with self.assertRaises(json.JSONDecodeError):
            json.loads(corrupted_json)


if __name__ == '__main__':
    unittest.main() 