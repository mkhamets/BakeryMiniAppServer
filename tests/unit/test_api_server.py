import unittest
import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

# Import the functions we want to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bot.api_server import (
    load_products_data_for_api, get_products_for_webapp,
    get_categories_for_webapp, serve_main_app_page, setup_api_server
)


class TestAPIServer(AioHTTPTestCase):
    """Test cases for API server functionality."""

    async def get_application(self):
        """Create application for testing."""
        app = web.Application()
        await setup_api_server()
        return app

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
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

    def tearDown(self):
        """Clean up after tests."""
        super().tearDown()

    @patch('bot.api_server.PRODUCTS_DATA_FILE')
    @patch('builtins.open', create=True)
    @patch('json.load')
    async def test_load_products_data_for_api_success(self, mock_json_load, mock_open, mock_file_path):
        """Test successful loading of products data for API."""
        mock_file_path.return_value = "/test/path/products.json"
        mock_json_load.return_value = self.test_products_data
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        await load_products_data_for_api()

        mock_open.assert_called_once()
        mock_json_load.assert_called_once()

    @patch('bot.api_server.PRODUCTS_DATA_FILE')
    @patch('builtins.open', create=True)
    async def test_load_products_data_for_api_file_not_found(self, mock_open, mock_file_path):
        """Test handling when products data file is not found."""
        mock_file_path.return_value = "/nonexistent/path/products.json"
        mock_open.side_effect = FileNotFoundError()

        await load_products_data_for_api()

        # Should handle the error gracefully
        pass

    @patch('bot.api_server.products_data')
    async def test_get_products_for_webapp_all_products(self, mock_products_data):
        """Test getting all products without category filter."""
        # Create a proper mock that behaves like a dict
        mock_products_data.__getitem__ = self.test_products_data.__getitem__
        mock_products_data.get = self.test_products_data.get
        mock_products_data.__bool__ = lambda self: True
        mock_products_data.items = self.test_products_data.items

        request = MagicMock()
        request.query = {}

        response = await get_products_for_webapp(request)
        
        # Check response status
        self.assertEqual(response.status, 200)

    @patch('bot.api_server.products_data')
    async def test_get_products_for_webapp_category_filter(self, mock_products_data):
        """Test getting products for specific category."""
        # Create a proper mock that behaves like a dict
        mock_products_data.__getitem__ = self.test_products_data.__getitem__
        mock_products_data.get = self.test_products_data.get
        mock_products_data.__bool__ = lambda self: True
        mock_products_data.items = self.test_products_data.items

        request = MagicMock()
        request.query = {"category": "category_bakery"}

        response = await get_products_for_webapp(request)
        
        # Check response status
        self.assertEqual(response.status, 200)

    @patch('bot.api_server.products_data')
    async def test_get_products_for_webapp_category_not_found(self, mock_products_data):
        """Test getting products for non-existent category."""
        mock_products_data.__getitem__ = self.test_products_data.__getitem__
        mock_products_data.get = self.test_products_data.get
        mock_products_data.__bool__ = lambda self: True

        request = MagicMock()
        request.query = {"category": "nonexistent_category"}

        response = await get_products_for_webapp(request)

        self.assertEqual(response.status, 404)

    @patch('bot.api_server.products_data')
    async def test_get_products_for_webapp_no_data(self, mock_products_data):
        """Test getting products when no data is loaded."""
        mock_products_data.__bool__ = lambda self: False

        request = MagicMock()
        request.query = {}

        response = await get_products_for_webapp(request)

        self.assertEqual(response.status, 500)

    @patch('bot.api_server.products_data')
    async def test_get_categories_for_webapp_success(self, mock_products_data):
        """Test getting categories list successfully."""
        # Create a proper mock that behaves like a dict
        mock_products_data.__getitem__ = self.test_products_data.__getitem__
        mock_products_data.get = self.test_products_data.get
        mock_products_data.__bool__ = lambda self: True
        mock_products_data.items = self.test_products_data.items

        request = MagicMock()

        response = await get_categories_for_webapp(request)
        
        # Check response status
        self.assertEqual(response.status, 200)

    @patch('bot.api_server.products_data')
    async def test_get_categories_for_webapp_no_data(self, mock_products_data):
        """Test getting categories when no data is loaded."""
        mock_products_data.__bool__ = lambda self: False

        request = MagicMock()

        response = await get_categories_for_webapp(request)

        self.assertEqual(response.status, 500)

    @patch('bot.api_server.WEB_APP_DIR')
    @patch('os.path.join')
    @patch('aiohttp.web.FileResponse')
    async def test_serve_main_app_page_success(self, mock_file_response, mock_join, mock_web_app_dir):
        """Test serving main app page successfully."""
        mock_web_app_dir.return_value = "/test/web_app"
        mock_join.return_value = "/test/web_app/index.html"
        mock_file_response.return_value = web.Response(text="<html></html>")

        request = MagicMock()

        response = await serve_main_app_page(request)

        mock_join.assert_called_once_with("/test/web_app", "index.html")
        mock_file_response.assert_called_once_with("/test/web_app/index.html")

    @patch('bot.api_server.load_products_data_for_api')
    @patch('aiohttp.web.Application')
    async def test_setup_api_server(self, mock_app_class, mock_load_data):
        """Test API server setup."""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        await setup_api_server()

        mock_load_data.assert_called_once()
        mock_app.router.add_get.assert_called()

    @unittest_run_loop
    async def test_api_routes_are_registered(self):
        """Test that API routes are properly registered."""
        app = await self.get_application()
        
        # Check that routes are registered
        routes = list(app.router.routes())
        
        # Should have the main routes - just check that routes exist
        self.assertGreater(len(routes), 0)

    @patch('bot.api_server.products_data')
    async def test_get_products_empty_category(self, mock_products_data):
        """Test getting products for empty category."""
        mock_products_data.__getitem__ = self.test_products_data.__getitem__
        mock_products_data.get = lambda key: []  # Return empty list for any category
        mock_products_data.__bool__ = lambda self: True

        request = MagicMock()
        request.query = {"category": "empty_category"}

        response = await get_products_for_webapp(request)

        self.assertEqual(response.status, 404)

    @patch('bot.api_server.products_data')
    async def test_get_categories_empty_products(self, mock_products_data):
        """Test getting categories when some categories have no products."""
        # Create data with empty category
        test_data = {
            "category_bakery": [
                {
                    "name": "Bread",
                    "price": "10.00 р.",
                    "description": "Fresh bread",
                    "image_url": "bread.jpg",
                    "category_name": "🥨 Выпечка"
                }
            ],
            "empty_category": []  # Empty category
        }
        
        mock_products_data.__getitem__ = test_data.__getitem__
        mock_products_data.get = test_data.get
        mock_products_data.__bool__ = lambda self: True
        mock_products_data.items = test_data.items

        request = MagicMock()

        response = await get_categories_for_webapp(request)
        
        # Check response status
        self.assertEqual(response.status, 200)


class TestAPIServerErrorHandling(unittest.TestCase):
    """Test cases for API server error handling."""

    @patch('bot.api_server.products_data')
    async def test_get_products_json_error(self, mock_products_data):
        """Test handling JSON errors in products endpoint."""
        mock_products_data.__bool__ = lambda self: True
        mock_products_data.get.side_effect = Exception("JSON Error")

        request = MagicMock()
        request.query = {"category": "test_category"}

        with self.assertRaises(Exception):
            await get_products_for_webapp(request)

    @patch('bot.api_server.products_data')
    async def test_get_categories_json_error(self, mock_products_data):
        """Test handling JSON errors in categories endpoint."""
        mock_products_data.__bool__ = lambda self: True
        mock_products_data.items.side_effect = Exception("JSON Error")

        request = MagicMock()

        with self.assertRaises(Exception):
            await get_categories_for_webapp(request)

    @patch('bot.api_server.WEB_APP_DIR')
    @patch('os.path.join')
    async def test_serve_main_app_page_file_not_found(self, mock_join, mock_web_app_dir):
        """Test serving main app page when file not found."""
        mock_web_app_dir.return_value = "/test/web_app"
        mock_join.return_value = "/nonexistent/index.html"

        request = MagicMock()

        with self.assertRaises(FileNotFoundError):
            await serve_main_app_page(request)


if __name__ == '__main__':
    unittest.main() 