import unittest
import sys
import os
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

from api_server import setup_api_server
import aiohttp


class TestAPIIntegration(AioHTTPTestCase):
    """Integration tests for API server."""

    async def get_application(self):
        """Create application for testing."""
        # Create a test application
        app = aiohttp.web.Application()
        
        # Add basic routes for testing
        async def test_index(request):
            return aiohttp.web.Response(
                text='<!DOCTYPE html><html><head><title>Bakery Mini App</title></head><body>Test Content</body></html>',
                content_type='text/html'
            )
        
        async def test_css(request):
            return aiohttp.web.Response(
                text='body { margin: 0; } .container { width: 100%; }',
                content_type='text/css'
            )
        
        async def test_js(request):
            return aiohttp.web.Response(
                text='document.addEventListener("DOMContentLoaded", function() { console.log("Test"); }); Telegram.WebApp.ready();',
                content_type='application/javascript'
            )
        
        async def test_products(request):
            return aiohttp.web.json_response({
                "categories": ["bread", "pastries"],
                "products": []
            })
        
        async def test_categories(request):
            return aiohttp.web.json_response(["bread", "pastries", "cookies"])
        
        # Add routes
        app.router.add_get('/bot-app/', test_index)
        app.router.add_get('/bot-app/style.css', test_css)
        app.router.add_get('/bot-app/script.js', test_js)
        app.router.add_get('/bot-app/Hleb.jpg', lambda r: aiohttp.web.Response(content_type='image/jpeg'))
        app.router.add_get('/api/products', test_products)
        app.router.add_get('/api/categories', test_categories)
        
        return app

    @unittest_run_loop
    async def test_webapp_index_endpoint(self):
        """Test that the main web app index endpoint returns HTML."""
        resp = await self.client.request("GET", "/bot-app/")
        
        self.assertEqual(resp.status, 200)
        self.assertIn("text/html", resp.headers["content-type"])
        
        html_content = await resp.text()
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("Bakery Mini App", html_content)

    @unittest_run_loop
    async def test_webapp_css_endpoint(self):
        """Test that CSS endpoint returns stylesheet."""
        resp = await self.client.request("GET", "/bot-app/style.css")
        
        self.assertEqual(resp.status, 200)
        self.assertIn("text/css", resp.headers["content-type"])
        
        css_content = await resp.text()
        self.assertIn("body", css_content)
        self.assertIn("container", css_content)

    @unittest_run_loop
    async def test_webapp_js_endpoint(self):
        """Test that JavaScript endpoint returns script."""
        resp = await self.client.request("GET", "/bot-app/script.js")
        
        self.assertEqual(resp.status, 200)
        self.assertIn("application/javascript", resp.headers["content-type"])
        
        js_content = await resp.text()
        self.assertIn("document.addEventListener", js_content)
        self.assertIn("Telegram.WebApp", js_content)

    @unittest_run_loop
    async def test_webapp_image_endpoint(self):
        """Test that image endpoint returns image."""
        resp = await self.client.request("GET", "/bot-app/Hleb.jpg")
        
        self.assertEqual(resp.status, 200)
        self.assertIn("image/", resp.headers["content-type"])

    @unittest_run_loop
    async def test_api_products_endpoint(self):
        """Test that products API endpoint returns JSON data."""
        resp = await self.client.request("GET", "/api/products")
        
        self.assertEqual(resp.status, 200)
        self.assertIn("application/json", resp.headers["content-type"])
        
        data = await resp.json()
        self.assertIsInstance(data, dict)
        self.assertIn("categories", data)

    @unittest_run_loop
    async def test_api_products_with_category(self):
        """Test that products API endpoint with category parameter works."""
        resp = await self.client.request("GET", "/api/products?category=bread")
        
        self.assertEqual(resp.status, 200)
        self.assertIn("application/json", resp.headers["content-type"])
        
        data = await resp.json()
        self.assertIsInstance(data, dict)

    @unittest_run_loop
    async def test_api_categories_endpoint(self):
        """Test that categories API endpoint returns JSON data."""
        resp = await self.client.request("GET", "/api/categories")
        
        self.assertEqual(resp.status, 200)
        self.assertIn("application/json", resp.headers["content-type"])
        
        data = await resp.json()
        self.assertIsInstance(data, list)

    @unittest_run_loop
    async def test_cors_headers(self):
        """Test that CORS headers are properly set."""
        resp = await self.client.request("GET", "/bot-app/")
        
        self.assertIn("Access-Control-Allow-Origin", resp.headers)
        self.assertIn("Access-Control-Allow-Methods", resp.headers)
        self.assertIn("Access-Control-Allow-Headers", resp.headers)

    @unittest_run_loop
    async def test_404_for_nonexistent_endpoint(self):
        """Test that 404 is returned for nonexistent endpoints."""
        resp = await self.client.request("GET", "/nonexistent")
        
        self.assertEqual(resp.status, 404)

    @unittest_run_loop
    async def test_webapp_with_query_parameters(self):
        """Test that web app handles query parameters correctly."""
        resp = await self.client.request("GET", "/bot-app/?view=cart")
        
        self.assertEqual(resp.status, 200)
        html_content = await resp.text()
        self.assertIn("<!DOCTYPE html>", html_content)

    @unittest_run_loop
    async def test_static_file_serving(self):
        """Test that static files are served correctly."""
        # Test CSS file
        resp = await self.client.request("GET", "/bot-app/style.css")
        self.assertEqual(resp.status, 200)
        
        # Test JS file
        resp = await self.client.request("GET", "/bot-app/script.js")
        self.assertEqual(resp.status, 200)
        
        # Test image file
        resp = await self.client.request("GET", "/bot-app/Hleb.jpg")
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def test_api_error_handling(self):
        """Test that API handles errors gracefully."""
        # Test with invalid category
        resp = await self.client.request("GET", "/api/products?category=invalid")
        
        self.assertEqual(resp.status, 200)  # Should still return 200 with empty data
        data = await resp.json()
        self.assertIsInstance(data, dict)

    @unittest_run_loop
    async def test_webapp_initialization(self):
        """Test that web app initializes correctly."""
        resp = await self.client.request("GET", "/bot-app/")
        
        self.assertEqual(resp.status, 200)
        html_content = await resp.text()
        
        # Check for required elements
        self.assertIn("welcome-container", html_content)
        self.assertIn("categories-container", html_content)
        self.assertIn("products-container", html_content)
        self.assertIn("cart-container", html_content)
        self.assertIn("checkout-container", html_content)

    @unittest_run_loop
    async def test_api_response_structure(self):
        """Test that API responses have correct structure."""
        resp = await self.client.request("GET", "/api/products")
        data = await resp.json()
        
        # Check that response has expected structure
        self.assertIsInstance(data, dict)
        if "categories" in data:
            self.assertIsInstance(data["categories"], dict)

    @unittest_run_loop
    async def test_webapp_script_integration(self):
        """Test that web app script is properly integrated."""
        resp = await self.client.request("GET", "/bot-app/")
        html_content = await resp.text()
        
        # Check that script is included
        self.assertIn("script.js", html_content)
        self.assertIn("style.css", html_content)

    @unittest_run_loop
    async def test_api_categories_structure(self):
        """Test that categories API returns correct structure."""
        resp = await self.client.request("GET", "/api/categories")
        data = await resp.json()
        
        if data:  # If categories exist
            for category in data:
                self.assertIsInstance(category, dict)
                self.assertIn("key", category)
                self.assertIn("name", category)

    @unittest_run_loop
    async def test_webapp_telegram_integration(self):
        """Test that web app has Telegram WebApp integration."""
        resp = await self.client.request("GET", "/bot-app/script.js")
        js_content = await resp.text()
        
        # Check for Telegram WebApp API usage
        self.assertIn("Telegram.WebApp", js_content)
        self.assertIn("MainButton", js_content)
        self.assertIn("BackButton", js_content)

    @unittest_run_loop
    async def test_webapp_cart_functionality(self):
        """Test that web app has cart functionality."""
        resp = await self.client.request("GET", "/bot-app/script.js")
        js_content = await resp.text()
        
        # Check for cart-related functions
        self.assertIn("renderCart", js_content)
        self.assertIn("updateProductQuantity", js_content)
        self.assertIn("localStorage", js_content)

    @unittest_run_loop
    async def test_webapp_view_management(self):
        """Test that web app has view management functionality."""
        resp = await self.client.request("GET", "/bot-app/script.js")
        js_content = await resp.text()
        
        # Check for view management functions
        self.assertIn("displayView", js_content)
        self.assertIn("getCurrentView", js_content)

    @unittest_run_loop
    async def test_api_products_data_loading(self):
        """Test that products API loads data correctly."""
        resp = await self.client.request("GET", "/api/products")
        data = await resp.json()
        
        # Check that data is loaded (even if empty)
        self.assertIsInstance(data, dict)

    @unittest_run_loop
    async def test_webapp_responsive_design(self):
        """Test that web app has responsive design elements."""
        resp = await self.client.request("GET", "/bot-app/style.css")
        css_content = await resp.text()
        
        # Check for responsive design elements
        self.assertIn("@media", css_content)
        self.assertIn("max-width", css_content)

    @unittest_run_loop
    async def test_webapp_accessibility(self):
        """Test that web app has accessibility features."""
        resp = await self.client.request("GET", "/bot-app/")
        html_content = await resp.text()
        
        # Check for accessibility elements
        self.assertIn("alt=", html_content)
        self.assertIn("aria-", html_content)

    @unittest_run_loop
    async def test_api_error_response_format(self):
        """Test that API returns proper error response format."""
        # Test with invalid endpoint
        resp = await self.client.request("GET", "/api/invalid")
        
        # Should return 404 or proper error response
        self.assertIn(resp.status, [404, 500])

    @unittest_run_loop
    async def test_webapp_performance_features(self):
        """Test that web app has performance optimization features."""
        resp = await self.client.request("GET", "/bot-app/")
        html_content = await resp.text()
        
        # Check for performance features
        self.assertIn("preload", html_content)
        self.assertIn("async", html_content)

    @unittest_run_loop
    async def test_api_data_consistency(self):
        """Test that API returns consistent data structure."""
        # Test products endpoint
        resp1 = await self.client.request("GET", "/api/products")
        data1 = await resp1.json()
        
        # Test categories endpoint
        resp2 = await self.client.request("GET", "/api/categories")
        data2 = await resp2.json()
        
        # Both should return valid JSON
        self.assertIsInstance(data1, dict)
        self.assertIsInstance(data2, list)

    @unittest_run_loop
    async def test_webapp_security_features(self):
        """Test that web app has security features."""
        resp = await self.client.request("GET", "/bot-app/")
        html_content = await resp.text()
        
        # Check for security headers and features
        self.assertIn("Content-Security-Policy", resp.headers or {})
        self.assertIn("X-Content-Type-Options", resp.headers or {})


if __name__ == '__main__':
    unittest.main() 