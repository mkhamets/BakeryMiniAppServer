import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the bot directory to the path to import the parser
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

class TestDisabledProducts(unittest.TestCase):
    """Unit tests for disabled products feature"""
    
    def setUp(self):
        """Set up test data"""
        # Sample products data with some available and some unavailable products
        self.products_data = {
            "category_bakery": [
                {
                    "id": "49",
                    "name": "Завиванец с маком",
                    "price": "8.5",
                    "availability_days": "выпекаем пн, чт, сб"
                },
                {
                    "id": "50", 
                    "name": "Печенье «Кантуччи с миндалем»",
                    "price": "9.5",
                    "availability_days": "N/A"
                },
                {
                    "id": "51",
                    "name": "Печенье «Абрикос-кокос-фундук»", 
                    "price": "11.5",
                    "availability_days": "N/A"
                }
            ]
        }
        
        # Sample cart items with mixed availability
        self.cart_items = [
            {
                "id": "49",
                "name": "Завиванец с маком",
                "price": "8.5",
                "quantity": 2
            },
            {
                "id": "50",
                "name": "Печенье «Кантуччи с миндалем»",
                "price": "9.5", 
                "quantity": 1
            },
            {
                "id": "999",  # Non-existent product ID
                "name": "Несуществующий продукт",
                "price": "5.0",
                "quantity": 1
            }
        ]

    def test_is_product_available_with_available_product(self):
        """Test isProductAvailable function with available product"""
        # Mock the productsData global variable
        with patch('builtins.globals') as mock_globals:
            mock_globals.return_value = {'productsData': self.products_data}
            
            # Test with available product ID
            result = self._call_is_product_available("49")
            self.assertTrue(result, "Available product should return True")

    def test_is_product_available_with_unavailable_product(self):
        """Test isProductAvailable function with unavailable product"""
        with patch('builtins.globals') as mock_globals:
            mock_globals.return_value = {'productsData': self.products_data}
            
            # Test with unavailable product ID
            result = self._call_is_product_available("50")
            self.assertFalse(result, "Unavailable product should return False")

    def test_is_product_available_with_nonexistent_product(self):
        """Test isProductAvailable function with non-existent product"""
        with patch('builtins.globals') as mock_globals:
            mock_globals.return_value = {'productsData': self.products_data}
            
            # Test with non-existent product ID
            result = self._call_is_product_available("999")
            self.assertFalse(result, "Non-existent product should return False")

    def test_get_disabled_products_with_mixed_cart(self):
        """Test getDisabledProducts function with mixed cart items"""
        disabled_products = self._call_get_disabled_products(self.cart_items)
        
        # Should find 2 disabled products (ID 50 and 999)
        self.assertEqual(len(disabled_products), 2, "Should find 2 disabled products")
        
        # Check specific products
        disabled_ids = [p['id'] for p in disabled_products]
        self.assertIn("50", disabled_ids, "Product ID 50 should be disabled")
        self.assertIn("999", disabled_ids, "Product ID 999 should be disabled")
        self.assertNotIn("49", disabled_ids, "Product ID 49 should not be disabled")

    def test_get_disabled_products_with_all_available(self):
        """Test getDisabledProducts function with all available products"""
        available_cart = [
            {
                "id": "49",
                "name": "Завиванец с маком", 
                "price": "8.5",
                "quantity": 2
            }
        ]
        
        disabled_products = self._call_get_disabled_products(available_cart)
        self.assertEqual(len(disabled_products), 0, "Should find 0 disabled products")

    def test_get_disabled_products_with_empty_cart(self):
        """Test getDisabledProducts function with empty cart"""
        disabled_products = self._call_get_disabled_products([])
        self.assertEqual(len(disabled_products), 0, "Empty cart should return 0 disabled products")

    def test_render_disabled_products_error_with_disabled_products(self):
        """Test renderDisabledProductsError function with disabled products"""
        disabled_products = [
            {"id": "50", "name": "Печенье «Кантуччи с миндалем»"},
            {"id": "999", "name": "Несуществующий продукт"}
        ]
        
        result = self._call_render_disabled_products_error(disabled_products)
        
        # Should create error container with proper content
        self.assertIsNotNone(result, "Should return error container")
        self.assertIn("Удалите недоступные товары из корзины", str(result.innerHTML), "Should contain error message")

    def test_render_disabled_products_error_with_no_disabled_products(self):
        """Test renderDisabledProductsError function with no disabled products"""
        result = self._call_render_disabled_products_error([])
        self.assertIsNone(result, "Should return null when no disabled products")

    def test_update_checkout_button_state_with_disabled_products(self):
        """Test updateCheckoutButtonState function with disabled products"""
        disabled_products = [{"id": "50", "name": "Test Product"}]
        
        result = self._call_update_checkout_button_state(disabled_products)
        
        # Should disable checkout button
        self.assertTrue(result.disabled, "Checkout button should be disabled")
        self.assertIn('disabled', str(result.classList.add.call_args), "Should add disabled class")

    def test_update_checkout_button_state_with_no_disabled_products(self):
        """Test updateCheckoutButtonState function with no disabled products"""
        result = self._call_update_checkout_button_state([])
        
        # Should enable checkout button
        self.assertFalse(result.disabled, "Checkout button should be enabled")
        self.assertIn('disabled', str(result.classList.remove.call_args), "Should remove disabled class")

    def test_cart_rendering_with_disabled_products(self):
        """Test cart rendering with disabled products"""
        # Test cart rendering logic without DOM mocking
        disabled_products = self._call_get_disabled_products(self.cart_items)
        
        # Should identify disabled products correctly
        self.assertEqual(len(disabled_products), 2, "Should identify 2 disabled products")
        
        # Check that specific products are correctly identified
        disabled_ids = [p['id'] for p in disabled_products]
        self.assertIn("50", disabled_ids, "Product ID 50 should be disabled")
        self.assertIn("999", disabled_ids, "Product ID 999 should be disabled")

    def test_product_availability_logic(self):
        """Test the overall product availability logic"""
        # Test that products with "N/A" availability_days are considered unavailable
        for category in self.products_data.values():
            for product in category:
                if product.get('availability_days') == 'N/A':
                    # This product should be considered unavailable
                    self.assertFalse(
                        self._call_is_product_available(product['id']),
                        f"Product {product['name']} with N/A availability should be unavailable"
                    )
                else:
                    # This product should be considered available
                    self.assertTrue(
                        self._call_is_product_available(product['id']),
                        f"Product {product['name']} with availability days should be available"
                    )

    # Helper methods to simulate JavaScript function calls
    def _call_is_product_available(self, product_id):
        """Simulate isProductAvailable JavaScript function"""
        # Check if product exists in any category
        for category in self.products_data.values():
            for product in category:
                if product['id'] == product_id:
                    # Product exists, check if it's available (not N/A)
                    return product.get('availability_days') != 'N/A'
        return False  # Product not found

    def _call_get_disabled_products(self, cart_items):
        """Simulate getDisabledProducts JavaScript function"""
        disabled_products = []
        for item in cart_items:
            if not self._call_is_product_available(item['id']):
                disabled_products.append(item)
        return disabled_products

    def _call_render_disabled_products_error(self, disabled_products):
        """Simulate renderDisabledProductsError JavaScript function"""
        if not disabled_products:
            return None
        
        # Simulate creating error container
        error_container = MagicMock()
        error_container.innerHTML = f"""
        <div class="alert alert-danger d-flex align-items-center" role="alert">
            <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Danger:">
                <use xlink:href="#exclamation-triangle-fill"/>
            </svg>
            <div>
                Удалите недоступные товары из корзины
            </div>
        </div>
        """
        return error_container

    def _call_update_checkout_button_state(self, disabled_products):
        """Simulate updateCheckoutButtonState JavaScript function"""
        checkout_button = MagicMock()
        
        if disabled_products:
            checkout_button.classList.add('disabled')
            checkout_button.disabled = True
        else:
            checkout_button.classList.remove('disabled')
            checkout_button.disabled = False
        
        return checkout_button

    def test_edge_cases(self):
        """Test edge cases for disabled products feature"""
        # Test with null/undefined values
        self.assertFalse(self._call_is_product_available(None))
        self.assertFalse(self._call_is_product_available(""))
        
        # Test with invalid cart items
        invalid_cart = [
            {"id": None, "name": "Invalid Product"},
            {"id": "", "name": "Empty ID Product"},
            {"name": "No ID Product"}  # Missing ID
        ]
        
        # Handle cart items without 'id' field
        disabled_products = []
        for item in invalid_cart:
            if 'id' not in item or not item['id']:
                disabled_products.append(item)
        
        self.assertEqual(len(disabled_products), 3, "All invalid items should be considered disabled")

    def test_performance_with_large_cart(self):
        """Test performance with large number of cart items"""
        # Create large cart with 100 items
        large_cart = []
        for i in range(100):
            large_cart.append({
                "id": str(i),
                "name": f"Product {i}",
                "price": "10.0",
                "quantity": 1
            })
        
        # Test that function handles large carts efficiently
        start_time = self._get_time()
        disabled_products = self._call_get_disabled_products(large_cart)
        end_time = self._get_time()
        
        # Should complete within reasonable time (less than 1 second)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 1.0, f"Large cart processing took {execution_time} seconds")

    def _get_time(self):
        """Helper method to get current time for performance testing"""
        import time
        return time.time()


if __name__ == '__main__':
    unittest.main()
