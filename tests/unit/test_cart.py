import unittest
import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from aiogram.types import Message, User, Chat

# Import the functions we want to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bot.main import (
    get_user_cart, update_cart_item_quantity, clear_user_cart,
    _handle_update_cart
)


class TestCartManagement(unittest.TestCase):
    """Test cases for cart management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_user_id = 123456789
        self.test_product_id = "test_product_1"
        self.test_product_data = {
            "id": "test_product_1",
            "name": "Test Bread",
            "price": "10.00 р.",
            "description": "Test bread description"
        }

    def tearDown(self):
        """Clean up after tests."""
        # Clear test cart data
        from bot.main import user_carts
        if self.test_user_id in user_carts:
            del user_carts[self.test_user_id]

    def test_get_user_cart_empty(self):
        """Test getting empty user cart."""
        result = get_user_cart(self.test_user_id)
        self.assertEqual(result, {})

    def test_get_user_cart_with_items(self):
        """Test getting user cart with items."""
        # Add items to cart
        update_cart_item_quantity(self.test_user_id, "product1", 2)
        update_cart_item_quantity(self.test_user_id, "product2", 1)

        result = get_user_cart(self.test_user_id)
        
        self.assertEqual(result["product1"], 2)
        self.assertEqual(result["product2"], 1)
        self.assertEqual(len(result), 2)

    def test_update_cart_item_quantity_add_new(self):
        """Test adding new item to cart."""
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 3)
        
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[self.test_product_id], 3)

    def test_update_cart_item_quantity_update_existing(self):
        """Test updating existing item quantity."""
        # Add item first
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 2)
        
        # Update quantity
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 5)
        
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[self.test_product_id], 5)

    def test_update_cart_item_quantity_remove_item(self):
        """Test removing item by setting quantity to 0."""
        # Add item first
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 2)
        
        # Remove item
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 0)
        
        cart = get_user_cart(self.test_user_id)
        self.assertNotIn(self.test_product_id, cart)

    def test_update_cart_item_quantity_negative_quantity(self):
        """Test handling negative quantity."""
        # Add item first
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 2)
        
        # Try to set negative quantity
        update_cart_item_quantity(self.test_user_id, self.test_product_id, -1)
        
        cart = get_user_cart(self.test_user_id)
        # Should remove the item
        self.assertNotIn(self.test_product_id, cart)

    def test_clear_user_cart(self):
        """Test clearing user cart."""
        # Add items to cart
        update_cart_item_quantity(self.test_user_id, "product1", 2)
        update_cart_item_quantity(self.test_user_id, "product2", 1)
        update_cart_item_quantity(self.test_user_id, "product3", 3)

        # Clear cart
        clear_user_cart(self.test_user_id)

        # Verify cart is empty
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart, {})

    def test_clear_user_cart_empty(self):
        """Test clearing already empty cart."""
        # Ensure cart is empty
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart, {})

        # Clear cart
        clear_user_cart(self.test_user_id)

        # Verify cart is still empty
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart, {})

    def test_cart_persistence_across_operations(self):
        """Test that cart persists across multiple operations."""
        # Add multiple items
        update_cart_item_quantity(self.test_user_id, "bread", 2)
        update_cart_item_quantity(self.test_user_id, "croissant", 1)
        update_cart_item_quantity(self.test_user_id, "cake", 3)

        # Verify cart state
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart["bread"], 2)
        self.assertEqual(cart["croissant"], 1)
        self.assertEqual(cart["cake"], 3)

        # Update some items
        update_cart_item_quantity(self.test_user_id, "bread", 5)
        update_cart_item_quantity(self.test_user_id, "croissant", 0)  # Remove

        # Verify updated cart state
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart["bread"], 5)
        self.assertNotIn("croissant", cart)
        self.assertEqual(cart["cake"], 3)

    def test_multiple_users_cart_isolation(self):
        """Test that different users have isolated carts."""
        user1_id = 111111111
        user2_id = 222222222

        # Add items to user1's cart
        update_cart_item_quantity(user1_id, "bread", 2)
        update_cart_item_quantity(user1_id, "croissant", 1)

        # Add items to user2's cart
        update_cart_item_quantity(user2_id, "cake", 3)
        update_cart_item_quantity(user2_id, "muffin", 2)

        # Verify carts are isolated
        user1_cart = get_user_cart(user1_id)
        user2_cart = get_user_cart(user2_id)

        self.assertEqual(user1_cart["bread"], 2)
        self.assertEqual(user1_cart["croissant"], 1)
        self.assertNotIn("cake", user1_cart)
        self.assertNotIn("muffin", user1_cart)

        self.assertEqual(user2_cart["cake"], 3)
        self.assertEqual(user2_cart["muffin"], 2)
        self.assertNotIn("bread", user2_cart)
        self.assertNotIn("croissant", user2_cart)

        # Clean up
        clear_user_cart(user1_id)
        clear_user_cart(user2_id)

    @patch('bot.main.bot')
    async def test_handle_update_cart_add_action(self, mock_bot):
        """Test handling cart update with add action."""
        mock_message = MagicMock()
        mock_message.chat.id = self.test_user_id
        
        test_data = {
            "action": "add",
            "productId": self.test_product_id,
            "quantity": 2
        }

        await _handle_update_cart(mock_message, test_data, self.test_user_id)

        # Verify cart was updated
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[self.test_product_id], 2)

    @patch('bot.main.bot')
    async def test_handle_update_cart_remove_action(self, mock_bot):
        """Test handling cart update with remove action."""
        # Add item first
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 3)
        
        mock_message = MagicMock()
        mock_message.chat.id = self.test_user_id
        
        test_data = {
            "action": "remove",
            "productId": self.test_product_id,
            "quantity": 0
        }

        await _handle_update_cart(mock_message, test_data, self.test_user_id)

        # Verify item was removed
        cart = get_user_cart(self.test_user_id)
        self.assertNotIn(self.test_product_id, cart)

    @patch('bot.main.bot')
    async def test_handle_update_cart_update_action(self, mock_bot):
        """Test handling cart update with update action."""
        # Add item first
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 2)
        
        mock_message = MagicMock()
        mock_message.chat.id = self.test_user_id
        
        test_data = {
            "action": "update",
            "productId": self.test_product_id,
            "quantity": 5
        }

        await _handle_update_cart(mock_message, test_data, self.test_user_id)

        # Verify quantity was updated
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[self.test_product_id], 5)

    @patch('bot.main.bot')
    async def test_handle_update_cart_invalid_action(self, mock_bot):
        """Test handling cart update with invalid action."""
        mock_message = MagicMock()
        mock_message.chat.id = self.test_user_id
        
        test_data = {
            "action": "invalid_action",
            "productId": self.test_product_id,
            "quantity": 2
        }

        # Should handle gracefully without error
        await _handle_update_cart(mock_message, test_data, self.test_user_id)

        # Cart should remain unchanged
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart, {})

    def test_cart_validation_edge_cases(self):
        """Test cart validation with edge cases."""
        # Test with very large quantity
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 999999)
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[self.test_product_id], 999999)

        # Test with zero quantity
        update_cart_item_quantity(self.test_user_id, self.test_product_id, 0)
        cart = get_user_cart(self.test_user_id)
        self.assertNotIn(self.test_product_id, cart)

        # Test with empty product ID
        update_cart_item_quantity(self.test_user_id, "", 2)
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart[""], 2)

    def test_cart_performance_with_many_items(self):
        """Test cart performance with many items."""
        # Add many items
        for i in range(100):
            product_id = f"product_{i}"
            update_cart_item_quantity(self.test_user_id, product_id, i + 1)

        # Verify all items are present
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(len(cart), 100)
        
        for i in range(100):
            product_id = f"product_{i}"
            self.assertEqual(cart[product_id], i + 1)

        # Clear cart
        clear_user_cart(self.test_user_id)
        cart = get_user_cart(self.test_user_id)
        self.assertEqual(cart, {})


class TestCartDataStructures(unittest.TestCase):
    """Test cases for cart data structure integrity."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_user_id = 987654321

    def tearDown(self):
        """Clean up after tests."""
        from bot.main import user_carts
        if self.test_user_id in user_carts:
            del user_carts[self.test_user_id]

    def test_cart_data_structure_integrity(self):
        """Test that cart data structure maintains integrity."""
        from bot.main import user_carts

        # Initially should be empty
        self.assertNotIn(self.test_user_id, user_carts)

        # Add item
        update_cart_item_quantity(self.test_user_id, "test_product", 2)
        
        # Verify structure
        self.assertIn(self.test_user_id, user_carts)
        self.assertIsInstance(user_carts[self.test_user_id], dict)
        self.assertEqual(user_carts[self.test_user_id]["test_product"], 2)

        # Remove item
        update_cart_item_quantity(self.test_user_id, "test_product", 0)
        
        # Verify structure is maintained
        self.assertIn(self.test_user_id, user_carts)
        self.assertIsInstance(user_carts[self.test_user_id], dict)
        self.assertEqual(user_carts[self.test_user_id], {})

    def test_cart_memory_cleanup(self):
        """Test that cart memory is properly managed."""
        from bot.main import user_carts

        # Add items to multiple users
        user_ids = [111, 222, 333, 444, 555]
        
        for user_id in user_ids:
            update_cart_item_quantity(user_id, "product", 1)

        # Verify all users have carts
        for user_id in user_ids:
            self.assertIn(user_id, user_carts)

        # Clear carts for all users
        for user_id in user_ids:
            clear_user_cart(user_id)

        # Verify carts are empty but still exist
        for user_id in user_ids:
            self.assertIn(user_id, user_carts)
            self.assertEqual(user_carts[user_id], {})

        # Clean up - remove all test carts
        for user_id in user_ids:
            if user_id in user_carts:
                del user_carts[user_id]
        
        # Verify all test carts are removed
        for user_id in user_ids:
            self.assertNotIn(user_id, user_carts)


if __name__ == '__main__':
    unittest.main() 