import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

from keyboards import generate_main_menu, BASE_WEBAPP_URL


class TestKeyboards(unittest.TestCase):
    """Test cases for keyboards module."""

    def test_base_webapp_url_format(self):
        """Test that BASE_WEBAPP_URL has correct format."""
        self.assertIsInstance(BASE_WEBAPP_URL, str)
        self.assertIn('herokuapp.com', BASE_WEBAPP_URL)
        self.assertTrue(BASE_WEBAPP_URL.endswith('/bot-app/'))

    def test_generate_main_menu_empty_cart(self):
        """Test main menu generation with empty cart."""
        keyboard = generate_main_menu(cart_items_count=0)
        
        # Check keyboard type
        self.assertIsNotNone(keyboard)
        
        # Check keyboard properties
        self.assertTrue(keyboard.resize_keyboard)
        self.assertTrue(keyboard.is_persistent)
        self.assertFalse(keyboard.one_time_keyboard)
        self.assertEqual(keyboard.input_field_placeholder, "Используйте меню ⬇️")
        
        # Check keyboard structure
        self.assertIsInstance(keyboard.keyboard, list)
        self.assertGreater(len(keyboard.keyboard), 0)
        
        # Check that cart button doesn't show count when empty
        cart_button = None
        for row in keyboard.keyboard:
            for button in row:
                if "🛒 Проверить корзину" in button.text:
                    cart_button = button
                    break
            if cart_button:
                break
        
        self.assertIsNotNone(cart_button)
        self.assertEqual(cart_button.text, "🛒 Проверить корзину")
        self.assertNotIn("(0)", cart_button.text)

    def test_generate_main_menu_with_items(self):
        """Test main menu generation with items in cart."""
        keyboard = generate_main_menu(cart_items_count=3)
        
        # Check that cart button shows count
        cart_button = None
        for row in keyboard.keyboard:
            for button in row:
                if "🛒 Проверить корзину" in button.text:
                    cart_button = button
                    break
            if cart_button:
                break
        
        self.assertIsNotNone(cart_button)
        self.assertEqual(cart_button.text, "🛒 Проверить корзину (3)")

    def test_generate_main_menu_with_many_items(self):
        """Test main menu generation with many items in cart."""
        keyboard = generate_main_menu(cart_items_count=99)
        
        cart_button = None
        for row in keyboard.keyboard:
            for button in row:
                if "🛒 Проверить корзину" in button.text:
                    cart_button = button
                    break
            if cart_button:
                break
        
        self.assertIsNotNone(cart_button)
        self.assertEqual(cart_button.text, "🛒 Проверить корзину (99)")

    def test_menu_button_webapp_url(self):
        """Test that menu button has correct WebApp URL."""
        keyboard = generate_main_menu()
        
        menu_button = None
        for row in keyboard.keyboard:
            for button in row:
                if "Наше меню" in button.text:
                    menu_button = button
                    break
            if menu_button:
                break
        
        self.assertIsNotNone(menu_button)
        self.assertIsNotNone(menu_button.web_app)
        self.assertIn('?view=categories', menu_button.web_app.url)

    def test_cart_button_webapp_url(self):
        """Test that cart button has correct WebApp URL."""
        keyboard = generate_main_menu()
        
        cart_button = None
        for row in keyboard.keyboard:
            for button in row:
                if "🛒 Проверить корзину" in button.text:
                    cart_button = button
                    break
            if cart_button:
                break
        
        self.assertIsNotNone(cart_button)
        self.assertIsNotNone(cart_button.web_app)
        self.assertIn('?view=cart', cart_button.web_app.url)

    def test_keyboard_structure(self):
        """Test that keyboard has correct structure with all required buttons."""
        keyboard = generate_main_menu()
        
        # Check that we have the expected number of rows
        self.assertGreaterEqual(len(keyboard.keyboard), 3)
        
        # Check for required buttons
        button_texts = []
        for row in keyboard.keyboard:
            for button in row:
                button_texts.append(button.text)
        
        required_buttons = [
            "Наше меню",
            "🛒 Проверить корзину",
            "Наши адреса",
            "О доставке",
            "О нас"
        ]
        
        for required_button in required_buttons:
            self.assertIn(required_button, button_texts, 
                         f"Required button '{required_button}' not found in keyboard")

    def test_webapp_urls_format(self):
        """Test that all WebApp URLs have correct format."""
        keyboard = generate_main_menu()
        
        webapp_buttons = []
        for row in keyboard.keyboard:
            for button in row:
                if hasattr(button, 'web_app') and button.web_app:
                    webapp_buttons.append(button)
        
        for button in webapp_buttons:
            self.assertIsNotNone(button.web_app.url)
            self.assertTrue(button.web_app.url.startswith('http'))
            self.assertIn('herokuapp.com', button.web_app.url)

    def test_keyboard_persistence(self):
        """Test that keyboard is set as persistent."""
        keyboard = generate_main_menu()
        self.assertTrue(keyboard.is_persistent)

    def test_keyboard_resize(self):
        """Test that keyboard is set to resize."""
        keyboard = generate_main_menu()
        self.assertTrue(keyboard.resize_keyboard)

    def test_input_field_placeholder(self):
        """Test that input field placeholder is set correctly."""
        keyboard = generate_main_menu()
        self.assertEqual(keyboard.input_field_placeholder, "Используйте меню ⬇️")


if __name__ == '__main__':
    unittest.main() 