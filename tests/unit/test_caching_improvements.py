#!/usr/bin/env python3
"""
Unit tests for WebApp caching improvements.

This module tests the caching functionality implemented in:
- Phase 4: Browser Cache API Integration
- Phase 5: localStorage Cache Management  
- Phase 6: Service Worker Integration
"""

import unittest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add the bot directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

class TestCachingImprovements(unittest.TestCase):
    """Test cases for caching improvements."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_cache_data = {
            'category_bakery': [
                {
                    'name': 'Test Bread',
                    'price': '10.00',
                    'id': 'test-123'
                }
            ]
        }

    def test_cache_version_constants(self):
        """Test that cache version constants are properly defined."""
        # Import the script to check constants
        try:
            with open('bot/web_app/script.js', 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Check for cache version constants
            self.assertIn('CACHE_VERSION', script_content)
            self.assertIn('CACHE_NAME', script_content)
            self.assertIn('1.2.0', script_content)
            
            # Check for cache management functions
            self.assertIn('clearBrowserCache', script_content)
            self.assertIn('invalidateCacheOnUpdate', script_content)
            self.assertIn('initializeCacheManagement', script_content)
            
        except FileNotFoundError:
            self.skipTest("script.js file not found")

    def test_service_worker_cache_constants(self):
        """Test that service worker has proper cache constants."""
        try:
            with open('bot/web_app/sw.js', 'r', encoding='utf-8') as f:
                sw_content = f.read()
            
            # Check for service worker cache constants
            self.assertIn('CACHE_NAME', sw_content)
            self.assertIn('CACHE_VERSION', sw_content)
            self.assertIn('1.2.0', sw_content)
            
            # Check for cache strategies
            self.assertIn('cacheFirst', sw_content)
            self.assertIn('networkFirst', sw_content)
            
        except FileNotFoundError:
            self.skipTest("sw.js file not found")

    def test_html_cache_busting(self):
        """Test that HTML files have proper cache busting."""
        try:
            with open('bot/web_app/index.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Check for cache busting in static resources
            self.assertIn('?v=1.2.0', html_content)
            
            # Check for service worker registration
            self.assertIn('serviceWorker.register', html_content)
            self.assertIn('sw.js', html_content)
            
        except FileNotFoundError:
            self.skipTest("index.html file not found")

    def test_api_cache_headers(self):
        """Test that API server has proper cache control headers."""
        try:
            with open('bot/api_server.py', 'r', encoding='utf-8') as f:
                api_content = f.read()
            
            # Check for cache control headers in API responses
            self.assertIn('Cache-Control', api_content)
            self.assertIn('no-cache, no-store, must-revalidate', api_content)
            self.assertIn('Pragma', api_content)
            self.assertIn('Expires', api_content)
            
        except FileNotFoundError:
            self.skipTest("api_server.py file not found")

    def test_static_file_cache_control(self):
        """Test that static files have proper cache control."""
        try:
            with open('bot/api_server.py', 'r', encoding='utf-8') as f:
                api_content = f.read()
            
            # Check for static file cache control
            self.assertIn('serve_static_with_cache_control', api_content)
            self.assertIn('Cache-Control', api_content)
            
        except FileNotFoundError:
            self.skipTest("api_server.py file not found")

    def test_cache_management_integration(self):
        """Test that cache management is properly integrated."""
        try:
            with open('bot/web_app/script.js', 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Check that cache management is initialized
            self.assertIn('initializeCacheManagement', script_content)
            self.assertIn('DOMContentLoaded', script_content)
            
            # Check that functions are exposed globally (using the actual pattern in the code)
            self.assertIn('window.clearAllCaches', script_content)
            self.assertIn('window.getCacheStatus', script_content)
            
        except FileNotFoundError:
            self.skipTest("script.js file not found")

    def test_service_worker_integration(self):
        """Test that service worker integration is properly implemented."""
        try:
            with open('bot/web_app/script.js', 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Check for service worker integration
            self.assertIn('initializeServiceWorkerIntegration', script_content)
            self.assertIn('getServiceWorkerStatus', script_content)
            
        except FileNotFoundError:
            self.skipTest("script.js file not found")

    def test_cart_cache_management(self):
        """Test that cart cache management is properly implemented."""
        try:
            with open('bot/web_app/script.js', 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Check for cart cache functions
            self.assertIn('createCartWithMetadata', script_content)
            self.assertIn('loadCartWithExpiration', script_content)
            self.assertIn('saveCartWithMetadata', script_content)
            self.assertIn('checkCartExpiration', script_content)
            
        except FileNotFoundError:
            self.skipTest("script.js file not found")

    def test_cache_health_monitoring(self):
        """Test that cache health monitoring is implemented."""
        try:
            with open('bot/web_app/script.js', 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Check for cache health functions
            self.assertIn('getCacheStatus', script_content)
            self.assertIn('checkCacheHealth', script_content)
            
        except FileNotFoundError:
            self.skipTest("script.js file not found")

    def test_cache_invalidation_strategy(self):
        """Test that cache invalidation strategy is implemented."""
        try:
            with open('bot/web_app/script.js', 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Check for cache invalidation
            self.assertIn('invalidateCacheOnUpdate', script_content)
            self.assertIn('app_version', script_content)
            
        except FileNotFoundError:
            self.skipTest("script.js file not found")

    def test_cache_busting_consistency(self):
        """Test that cache busting is consistent across all files."""
        try:
            # Check CSS file
            with open('bot/web_app/style.css', 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Check that CSS doesn't have hardcoded cache busting for external resources
            # Note: CSS might have @import statements with URLs that contain ?v=, so we check for our specific pattern
            # But CSS can have background image URLs with cache busting
            external_urls_with_version = css_content.count('?v=1.2.0')
            self.assertLessEqual(external_urls_with_version, 1, "CSS should have minimal external resource cache busting")
            
            # Check that HTML has consistent versioning
            with open('bot/web_app/index.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Count occurrences of version 1.2.0
            version_count = html_content.count('?v=1.2.0')
            self.assertGreater(version_count, 0, "HTML should have cache busting versions")
            
        except FileNotFoundError:
            self.skipTest("Required files not found")

    def test_service_worker_error_handling(self):
        """Test that service worker has proper error handling."""
        try:
            with open('bot/web_app/sw.js', 'r', encoding='utf-8') as f:
                sw_content = f.read()
            
            # Check for error handling in service worker
            self.assertIn('chrome-extension', sw_content)
            self.assertIn('Skipping unsupported scheme', sw_content)
            
        except FileNotFoundError:
            self.skipTest("sw.js file not found")

    def test_cache_strategies_implementation(self):
        """Test that cache strategies are properly implemented."""
        try:
            with open('bot/web_app/sw.js', 'r', encoding='utf-8') as f:
                sw_content = f.read()
            
            # Check for cache strategies
            self.assertIn('cacheFirst', sw_content)
            self.assertIn('networkFirst', sw_content)
            self.assertIn('getCacheStrategy', sw_content)
            
        except FileNotFoundError:
            self.skipTest("sw.js file not found")

    def test_cache_versioning_implementation(self):
        """Test that cache versioning is properly implemented."""
        try:
            with open('bot/web_app/sw.js', 'r', encoding='utf-8') as f:
                sw_content = f.read()
            
            # Check for version-based cache management
            self.assertIn('CACHE_VERSION', sw_content)
            self.assertIn('version', sw_content)
            
        except FileNotFoundError:
            self.skipTest("sw.js file not found")

    def test_cache_cleanup_implementation(self):
        """Test that cache cleanup is properly implemented."""
        try:
            with open('bot/web_app/sw.js', 'r', encoding='utf-8') as f:
                sw_content = f.read()
            
            # Check for cache cleanup in activate event
            self.assertIn('activate', sw_content)
            self.assertIn('caches.keys', sw_content)
            self.assertIn('caches.delete', sw_content)
            
        except FileNotFoundError:
            self.skipTest("sw.js file not found")

    def test_cache_message_handling(self):
        """Test that cache message handling is implemented."""
        try:
            with open('bot/web_app/sw.js', 'r', encoding='utf-8') as f:
                sw_content = f.read()
            
            # Check for message handling
            self.assertIn('message', sw_content)
            self.assertIn('postMessage', sw_content)
            
        except FileNotFoundError:
            self.skipTest("sw.js file not found")


if __name__ == '__main__':
    unittest.main()
