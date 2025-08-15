import unittest
import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from aiogram.types import Message, CallbackQuery, User, Chat
from aiogram.types.web_app_info import WebAppInfo

# Import the functions we want to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bot.main import (
    load_products_data, load_order_counter, save_order_counter,
    generate_order_number, format_phone_telegram, get_user_cart,
    update_cart_item_quantity, clear_user_cart, clear_user_cart_messages,
    send_email_notification, _handle_update_cart, _handle_checkout_order,
    _send_order_notifications, _format_telegram_order_summary,
    _format_email_body, _format_user_email_body
)


class TestMainBotFunctions(unittest.TestCase):
    """Test cases for main bot functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_user_id = 123456789
        self.test_product_id = "test_product_1"
        self.test_order_data = {
            "deliveryMethod": "courier",
            "firstName": "John",
            "lastName": "Doe",
            "phoneNumber": "+375291234567",
            "email": "test@example.com",
            "city": "Minsk",
            "addressLine": "Test Address 123"
        }

    def tearDown(self):
        """Clean up after tests."""
        # Clear any test data
        pass

    @patch('bot.main.PRODUCTS_DATA_FILE')
    @patch('builtins.open', create=True)
    @patch('json.load')
    def test_load_products_data_success(self, mock_json_load, mock_open, mock_file_path):
        """Test successful loading of products data."""
        mock_file_path.return_value = "/test/path/products.json"
        mock_data = {
            "category_bakery": [
                {"name": "Bread", "price": "10.00 р."},
                {"name": "Croissant", "price": "15.00 р."}
            ]
        }
        mock_json_load.return_value = mock_data
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        asyncio.run(load_products_data())

        mock_open.assert_called_once()
        mock_json_load.assert_called_once()

    @patch('bot.main.PRODUCTS_DATA_FILE')
    @patch('builtins.open', create=True)
    @patch('json.load')
    def test_load_products_data_file_not_found(self, mock_json_load, mock_open, mock_file_path):
        """Test handling when products data file is not found."""
        mock_file_path.return_value = "/nonexistent/path/products.json"
        mock_open.side_effect = FileNotFoundError()

        asyncio.run(load_products_data())

        # Should handle the error gracefully
        mock_json_load.assert_not_called()

    @patch('bot.main.ORDER_COUNTER_FILE')
    @patch('builtins.open', create=True)
    @patch('json.load')
    def test_load_order_counter_success(self, mock_json_load, mock_open, mock_file_path):
        """Test successful loading of order counter."""
        mock_file_path.return_value = "/test/path/counter.json"
        mock_data = {"counter": 42, "last_reset_month": 8}
        mock_json_load.return_value = mock_data
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = asyncio.run(load_order_counter())

        # The function should return the loaded data
        self.assertEqual(result["counter"], 42)
        self.assertEqual(result["last_reset_month"], 8)

    @patch('bot.main.ORDER_COUNTER_FILE')
    @patch('builtins.open', create=True)
    def test_load_order_counter_file_not_found(self, mock_open, mock_file_path):
        """Test handling when order counter file is not found."""
        mock_file_path.return_value = "/nonexistent/path/counter.json"
        mock_open.side_effect = FileNotFoundError()

        result = asyncio.run(load_order_counter())

        # Should return default values when file not found
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

    @patch('bot.main.load_order_counter')
    @patch('bot.main.save_order_counter')
    def test_generate_order_number(self, mock_save, mock_load):
        """Test order number generation."""
        mock_load.return_value = {"counter": 42, "last_reset_month": 8}
        
        result = asyncio.run(generate_order_number())

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("#"))
        mock_save.assert_called_once()

    def test_format_phone_telegram(self):
        """Test phone number formatting for Telegram."""
        test_cases = [
            ("+375291234567", "+37529123-45-67"),  # Belarusian number with dashes
            ("375291234567", "+37529123-45-67"),   # Belarusian number with dashes
            ("80291234567", "80291234567"),        # Non-Belarusian number (unchanged)
        ]

        for input_phone, expected in test_cases:
            with self.subTest(input_phone=input_phone):
                result = format_phone_telegram(input_phone)
                self.assertEqual(result, expected)

    def test_get_user_cart_empty(self):
        """Test getting empty user cart."""
        result = get_user_cart(self.test_user_id)
        self.assertEqual(result, {})

    def test_update_cart_item_quantity(self):
        """Test updating cart item quantity."""
        # Test adding new item
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 2)
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[self.test_product_id], 2)

        # Test updating existing item
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 5)
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[self.test_product_id], 5)

        # Test removing item (quantity 0)
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 0)
        cart = get_user_cart(self.test_user_id)
        self.assertNotIn(self.test_product_id, cart)

    def test_clear_user_cart(self):
        """Test clearing user cart."""
        # Add some items to cart
        update_cart_item_quantity(self.test_user_id, "product1", 2)
        update_cart_item_quantity(self.test_user_id, "product2", 1)

        # Clear cart
        clear_user_cart(self.test_user_id)

        # Verify cart is empty
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart, {})

    @patch('bot.main.bot')
    def test_clear_user_cart_messages(self, mock_bot):
        """Test clearing user cart messages."""
        mock_bot.delete_message = AsyncMock()

        asyncio.run(clear_user_cart_messages(self.test_user_id))

        # Should not raise any exceptions
        mock_bot.delete_message.assert_not_called()

    @patch('bot.main.smtplib.SMTP')
    def test_send_email_notification_success(self, mock_smtp):
        """Test successful email notification sending."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        result = asyncio.run(send_email_notification(
            "test@example.com",
            "Test Subject",
            "Test Body",
            "Test Sender"
        ))

        # The function doesn't return anything, so we just check it doesn't raise an exception
        mock_smtp_instance.send_message.assert_called_once()

    @patch('bot.main.smtplib.SMTP')
    def test_send_email_notification_failure(self, mock_smtp):
        """Test email notification sending failure."""
        mock_smtp.side_effect = Exception("SMTP Error")

        result = asyncio.run(send_email_notification(
            "test@example.com",
            "Test Subject",
            "Test Body"
        ))

        self.assertFalse(result)

    @patch('bot.main.bot')
    def test_handle_update_cart(self, mock_bot):
        """Test handling cart updates from WebApp."""
        mock_message = MagicMock()
        mock_message.chat.id = self.test_user_id
        
        test_data = {
            "action": "add",
            "productId": self.test_product_id,
            "quantity": 2
        }

        asyncio.run(_handle_update_cart(mock_message, test_data, self.test_user_id))

        # Verify cart was updated
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[self.test_product_id], 2)

    @patch('bot.main.generate_order_number')
    @patch('bot.main._send_order_notifications')
    @patch('bot.main.clear_user_cart')
    @patch('bot.main.bot')
    def test_handle_checkout_order_success(self, mock_bot, mock_clear_cart, 
                                         mock_send_notifications, mock_generate_order):
        """Test successful order checkout processing."""
        mock_message = MagicMock()
        mock_message.chat.id = self.test_user_id
        mock_message.answer = AsyncMock()  # Fix: Use AsyncMock for async method
        mock_generate_order.return_value = "ORD001"
        mock_send_notifications.return_value = True

        # Add items to cart first
        update_cart_item_quantity(self.test_user_id, "product1", 2)
        update_cart_item_quantity(self.test_user_id, "product2", 1)

        # Create proper data structure that the function expects
        test_data = {
            'order_details': self.test_order_data,
            'cart_items': [
                {"id": "product1", "name": "Product 1", "price": 10.0, "quantity": 2},
                {"id": "product2", "name": "Product 2", "price": 15.0, "quantity": 1}
            ],
            'total_amount': 35.0
        }

        result = asyncio.run(_handle_checkout_order(mock_message, test_data, self.test_user_id))

        # Function returns None on success, but we can verify it completed successfully
        # by checking that all the expected functions were called
        self.assertIsNone(result)  # Function returns None on success
        mock_generate_order.assert_called_once()
        mock_send_notifications.assert_called_once()
        mock_clear_cart.assert_called_once_with(self.test_user_id)

    def test_format_telegram_order_summary(self):
        """Test formatting order summary for Telegram."""
        order_number = "ORD001"
        order_details = {
            "firstName": "John",
            "lastName": "Doe",
            "phoneNumber": "+375291234567",
            "email": "test@example.com",
            "deliveryMethod": "courier"
        }
        cart_items = [
            {"name": "Bread", "price": "10.00 р.", "quantity": 2},
            {"name": "Croissant", "price": "15.00 р.", "quantity": 1}
        ]
        total_amount = 35.00
        formatted_phone = "+375291234567"
        delivery_text = "Доставка курьером"

        result = _format_telegram_order_summary(
            order_number, order_details, cart_items, total_amount,
            formatted_phone, delivery_text, self.test_user_id
        )

        self.assertIn("ORD001", result)
        self.assertIn("Doe", result)  # lastName
        self.assertIn("John", result)  # firstName
        self.assertIn("+375291234567", result)
        self.assertIn("35.00", result)
        self.assertIn("Доставка курьером", result)

    def test_format_email_body(self):
        """Test formatting email body."""
        order_number = "ORD001"
        order_details = {
            "firstName": "John",
            "lastName": "Doe",
            "phoneNumber": "+375291234567",
            "email": "test@example.com",
            "deliveryMethod": "courier"
        }
        cart_items = [
            {"name": "Bread", "price": "10.00 р.", "quantity": 2},
            {"name": "Croissant", "price": "15.00 р.", "quantity": 1}
        ]
        total_amount = 35.00
        delivery_text = "Доставка курьером"

        result = _format_email_body(
            order_number, order_details, cart_items, total_amount, delivery_text
        )

        self.assertIn("ORD001", result)
        self.assertIn("Doe", result)  # lastName
        self.assertIn("John", result)  # firstName
        self.assertIn("35.00", result)
        self.assertIn("Доставка курьером", result)

    def test_format_user_email_body(self):
        """Test formatting user email body."""
        order_number = "ORD001"
        order_details = {
            "firstName": "John",
            "lastName": "Doe",
            "deliveryMethod": "courier"
        }
        cart_items = [
            {"name": "Bread", "price": "10.00 р.", "quantity": 2},
            {"name": "Croissant", "price": "15.00 р.", "quantity": 1}
        ]
        total_amount = 35.00

        result = _format_user_email_body(
            order_number, order_details, cart_items, total_amount
        )

        self.assertIn("ORD001", result)
        self.assertIn("Doe John N/A", result)  # Actual format: lastName firstName middleName
        self.assertIn("35.00", result)


if __name__ == '__main__':
    unittest.main() 