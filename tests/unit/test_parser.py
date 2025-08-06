import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

from parser import get_products_from_category_page, get_product_details, main


class TestParser(unittest.TestCase):
    """Test cases for parser module."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.test_data_dir, exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    @patch('parser.logger')
    def test_get_products_from_category_page_empty_response(self, mock_logger):
        """Test handling of empty response from category page."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text.return_value = ""
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        # Mock BeautifulSoup to return empty product list
        with patch('parser.BeautifulSoup') as mock_soup:
            mock_soup_instance = MagicMock()
            mock_soup_instance.select.return_value = []
            mock_soup.return_value = mock_soup_instance
            
            result = asyncio.run(get_products_from_category_page(mock_session, "https://test.com"))
            
            self.assertEqual(result, [])
            mock_logger.debug.assert_called()

    @patch('parser.logger')
    def test_get_products_from_category_page_valid_response(self, mock_logger):
        """Test parsing of valid category page response."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text.return_value = """
        <html>
            <div class="product-item">
                <a class="open-product-modal product-item__title" href="/product/1">Test Product 1</a>
                <img src="/image1.jpg" alt="Product 1">
            </div>
            <div class="product-item">
                <a class="open-product-modal product-item__title" href="/product/2">Test Product 2</a>
                <img src="/image2.jpg" alt="Product 2">
            </div>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch('parser.BeautifulSoup') as mock_soup:
            mock_soup_instance = MagicMock()
            # Mock product elements
            product1 = MagicMock()
            product1.select_one.return_value = MagicMock(
                get_text=lambda strip=True: "Test Product 1",
                get=lambda key: "/product/1" if key == "href" else None
            )
            
            product2 = MagicMock()
            product2.select_one.return_value = MagicMock(
                get_text=lambda strip=True: "Test Product 2",
                get=lambda key: "/product/2" if key == "href" else None
            )
            
            mock_soup_instance.select.return_value = [product1, product2]
            mock_soup.return_value = mock_soup_instance
            
            result = asyncio.run(get_products_from_category_page(mock_session, "https://test.com"))
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['name'], "Test Product 1")
            self.assertEqual(result[0]['url'], "https://drazhin.by/product/1")
            self.assertEqual(result[1]['name'], "Test Product 2")
            self.assertEqual(result[1]['url'], "https://drazhin.by/product/2")

    @patch('parser.logger')
    def test_get_products_from_category_page_http_error(self, mock_logger):
        """Test handling of HTTP errors."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = asyncio.run(get_products_from_category_page(mock_session, "https://test.com"))
        
        self.assertEqual(result, [])
        mock_logger.error.assert_called()

    @patch('parser.logger')
    def test_get_product_details_valid_response(self, mock_logger):
        """Test parsing of valid product details page."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text.return_value = """
        <html>
            <div class="product-details">
                <h1>Test Product</h1>
                <div class="product-price">25.50 р.</div>
                <div class="product-description">Test description</div>
                <div class="product-weight">500 г</div>
                <div class="product-ingredients">Flour, Sugar, Eggs</div>
                <div class="product-nutrition">
                    <div>Calories: 250</div>
                    <div>Protein: 5g</div>
                </div>
            </div>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch('parser.BeautifulSoup') as mock_soup:
            mock_soup_instance = MagicMock()
            
            # Mock select_one to return different elements based on selector
            def mock_select_one(selector):
                mock_element = MagicMock()
                if 'h1' in selector:
                    mock_element.get_text.return_value = "Test Product"
                elif 'product-price' in selector:
                    mock_element.get_text.return_value = "25.50 р."
                elif 'product-description' in selector:
                    mock_element.get_text.return_value = "Test description"
                elif 'product-weight' in selector:
                    mock_element.get_text.return_value = "500 г"
                elif 'product-ingredients' in selector:
                    mock_element.get_text.return_value = "Flour, Sugar, Eggs"
                elif 'product-nutrition' in selector:
                    mock_element.get_text.return_value = "Calories: 250\nProtein: 5g"
                else:
                    return None
                return mock_element
            
            mock_soup_instance.select_one.side_effect = mock_select_one
            mock_soup.return_value = mock_soup_instance
            
            result = asyncio.run(get_product_details(mock_session, "https://test.com/product/1"))
            
            self.assertIsNotNone(result)
            self.assertEqual(result['name'], "Test Product")
            self.assertEqual(result['price'], "25.50 р.")
            self.assertEqual(result['description'], "Test description")
            self.assertEqual(result['weight'], "500 г")
            self.assertEqual(result['ingredients'], "Flour, Sugar, Eggs")

    @patch('parser.logger')
    def test_get_product_details_missing_data(self, mock_logger):
        """Test handling of missing data in product details."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text.return_value = "<html><body></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch('parser.BeautifulSoup') as mock_soup:
            mock_soup_instance = MagicMock()
            mock_soup_instance.select_one.return_value = None
            mock_soup.return_value = mock_soup_instance
            
            result = asyncio.run(get_product_details(mock_session, "https://test.com/product/1"))
            
            self.assertIsNotNone(result)
            # Should have default values for missing data
            self.assertIn('name', result)
            self.assertIn('price', result)
            self.assertIn('description', result)

    @patch('parser.logger')
    def test_get_product_details_http_error(self, mock_logger):
        """Test handling of HTTP errors in product details."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = asyncio.run(get_product_details(mock_session, "https://test.com/product/1"))
        
        self.assertIsNone(result)
        mock_logger.error.assert_called()

    @patch('parser.logger')
    @patch('parser.get_products_from_category_page')
    @patch('parser.get_product_details')
    @patch('parser.json.dump')
    @patch('builtins.open', create=True)
    def test_main_function_success(self, mock_open, mock_json_dump, mock_get_details, mock_get_products, mock_logger):
        """Test successful execution of main function."""
        # Mock data
        mock_products = [
            {'name': 'Product 1', 'url': 'https://test.com/product/1'},
            {'name': 'Product 2', 'url': 'https://test.com/product/2'}
        ]
        mock_details = [
            {'name': 'Product 1', 'price': '10.00 р.', 'description': 'Test 1'},
            {'name': 'Product 2', 'price': '20.00 р.', 'description': 'Test 2'}
        ]
        
        mock_get_products.return_value = mock_products
        mock_get_details.side_effect = mock_details
        
        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Run main function
        asyncio.run(main())
        
        # Verify calls
        mock_get_products.assert_called()
        self.assertEqual(mock_get_details.call_count, 2)
        mock_json_dump.assert_called()

    @patch('parser.logger')
    @patch('parser.get_products_from_category_page')
    def test_main_function_no_products(self, mock_get_products, mock_logger):
        """Test main function when no products are found."""
        mock_get_products.return_value = []
        
        asyncio.run(main())
        
        mock_logger.warning.assert_called()

    def test_url_join_functionality(self):
        """Test that URL joining works correctly."""
        from urllib.parse import urljoin
        from parser import BASE_URL
        
        relative_url = "/product/123"
        full_url = urljoin(BASE_URL, relative_url)
        
        self.assertEqual(full_url, "https://drazhin.by/product/123")

    def test_base_url_format(self):
        """Test that BASE_URL has correct format."""
        from parser import BASE_URL
        
        self.assertEqual(BASE_URL, "https://drazhin.by/")
        self.assertTrue(BASE_URL.startswith('https://'))
        self.assertTrue(BASE_URL.endswith('/'))


if __name__ == '__main__':
    unittest.main() 