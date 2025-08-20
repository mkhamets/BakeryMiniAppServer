"""
Fixed unit tests for keyboard functionality.
Updated to work with InlineKeyboardMarkup instead of ReplyKeyboardMarkup.
"""

import unittest
import sys
import os

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

from keyboards import generate_main_menu


class TestKeyboardsFixed(unittest.TestCase):
    """Test keyboard functionality with InlineKeyboardMarkup."""

    def test_generate_main_menu_empty_cart(self):
        """Test main menu generation with empty cart."""
        keyboard = generate_main_menu(0)
        
        # Check that it's an InlineKeyboardMarkup
        self.assertIsNotNone(keyboard)
        self.assertTrue(hasattr(keyboard, 'inline_keyboard'))
        
        # Check that it has the expected structure
        self.assertIsInstance(keyboard.inline_keyboard, list)
        self.assertGreaterEqual(len(keyboard.inline_keyboard), 3)

    def test_generate_main_menu_with_items(self):
        """Test main menu generation with items in cart."""
        keyboard = generate_main_menu(5)
        
        # Check that it's an InlineKeyboardMarkup
        self.assertIsNotNone(keyboard)
        self.assertTrue(hasattr(keyboard, 'inline_keyboard'))
        
        # Check that it has the expected structure
        self.assertIsInstance(keyboard.inline_keyboard, list)
        self.assertGreaterEqual(len(keyboard.inline_keyboard), 3)
        
        # Check that cart button shows the count
        cart_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Проверить корзину" in button.text:
                    self.assertIn("(5)", button.text)
                    cart_button_found = True
                    break
            if cart_button_found:
                break
        
        self.assertTrue(cart_button_found)

    def test_generate_main_menu_with_many_items(self):
        """Test main menu generation with many items in cart."""
        keyboard = generate_main_menu(99)
        
        # Check that it's an InlineKeyboardMarkup
        self.assertIsNotNone(keyboard)
        self.assertTrue(hasattr(keyboard, 'inline_keyboard'))
        
        # Check that it has the expected structure
        self.assertIsInstance(keyboard.inline_keyboard, list)
        self.assertGreaterEqual(len(keyboard.inline_keyboard), 3)
        
        # Check that cart button shows the count
        cart_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Проверить корзину" in button.text:
                    self.assertIn("(99)", button.text)
                    cart_button_found = True
                    break
            if cart_button_found:
                break
        
        self.assertTrue(cart_button_found)

    def test_menu_button_webapp_url(self):
        """Test that menu button has correct WebApp URL."""
        keyboard = generate_main_menu(0)
        
        menu_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Наше меню" in button.text:
                    self.assertIsNotNone(button.web_app)
                    self.assertIn("bot-app", button.web_app.url)
                    self.assertIn("view=categories", button.web_app.url)
                    menu_button_found = True
                    break
            if menu_button_found:
                break
        
        self.assertTrue(menu_button_found)

    def test_cart_button_webapp_url(self):
        """Test that cart button has correct WebApp URL."""
        keyboard = generate_main_menu(0)
        
        cart_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Проверить корзину" in button.text:
                    self.assertIsNotNone(button.web_app)
                    self.assertIn("bot-app", button.web_app.url)
                    self.assertIn("view=cart", button.web_app.url)
                    cart_button_found = True
                    break
            if cart_button_found:
                break
        
        self.assertTrue(cart_button_found)

    def test_keyboard_structure(self):
        """Test that keyboard has correct structure."""
        keyboard = generate_main_menu(0)
        
        # Should have at least 3 rows
        self.assertGreaterEqual(len(keyboard.inline_keyboard), 3)
        
        # First row should have menu button
        first_row = keyboard.inline_keyboard[0]
        self.assertEqual(len(first_row), 1)
        self.assertIn("Наше меню", first_row[0].text)
        
        # Second row should have cart button
        second_row = keyboard.inline_keyboard[1]
        self.assertEqual(len(second_row), 1)
        self.assertIn("Проверить корзину", second_row[0].text)
        
        # Third row should have info buttons
        third_row = keyboard.inline_keyboard[2]
        self.assertGreaterEqual(len(third_row), 2)
        
        info_buttons = [button.text for button in third_row]
        self.assertIn("Наши адреса", info_buttons)
        self.assertIn("О доставке", info_buttons)
        self.assertIn("О нас", info_buttons)

    def test_webapp_urls_format(self):
        """Test that WebApp URLs have correct format."""
        keyboard = generate_main_menu(0)
        
        for row in keyboard.inline_keyboard:
            for button in row:
                if hasattr(button, 'web_app') and button.web_app:
                    # Check URL format
                    self.assertIsInstance(button.web_app.url, str)
                    self.assertTrue(button.web_app.url.startswith('http'))
                    self.assertIn('herokuapp.com', button.web_app.url)

    def test_info_buttons_callback_data(self):
        """Test that info buttons have correct callback data."""
        keyboard = generate_main_menu(0)
        
        info_buttons = {
            "Наши адреса": "info:addresses",
            "О доставке": "info:delivery", 
            "О нас": "info:about"
        }
        
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.text in info_buttons:
                    self.assertEqual(button.callback_data, info_buttons[button.text])

    def test_inline_keyboard_properties(self):
        """Test that InlineKeyboardMarkup has correct properties."""
        keyboard = generate_main_menu(0)
        
        # InlineKeyboardMarkup should have inline_keyboard property
        self.assertTrue(hasattr(keyboard, 'inline_keyboard'))
        self.assertIsInstance(keyboard.inline_keyboard, list)
        
        # Should not have ReplyKeyboardMarkup properties
        self.assertFalse(hasattr(keyboard, 'resize_keyboard'))
        self.assertFalse(hasattr(keyboard, 'is_persistent'))
        self.assertFalse(hasattr(keyboard, 'one_time_keyboard'))
        self.assertFalse(hasattr(keyboard, 'input_field_placeholder'))


if __name__ == '__main__':
    unittest.main()
