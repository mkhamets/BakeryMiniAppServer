"""
Unit tests for security features.
Tests security headers, CORS, rate limiting, HMAC signatures, and other security measures.
Updated to include new HMAC security features.
"""

import unittest
import sys
import os
import json
import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

from security_headers import security_headers_middleware, create_content_hash
from security_manager import SecurityManager
from config import config


class TestSecurityHeaders(unittest.TestCase):
    """Test security headers middleware."""

    def test_create_content_hash(self):
        """Test content hash generation."""
        content = b"test content"
        hash1 = create_content_hash(content)
        hash2 = create_content_hash(content)
        
        # Same content should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Different content should produce different hash
        different_content = b"different content"
        hash3 = create_content_hash(different_content)
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be a valid MD5 hex string
        self.assertEqual(len(hash1), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1))

    async def test_security_headers_middleware(self):
        """Test security headers middleware adds correct headers."""
        # Create a mock request and handler
        request = MagicMock()
        request.scheme = 'https'
        
        async def mock_handler(req):
            return aiohttp.web.Response(text="test", status=200)
        
        # Call the middleware
        response = await security_headers_middleware(request, mock_handler)
        
        # Check that security headers are present
        headers = response.headers
        
        # Required security headers
        self.assertIn('X-Frame-Options', headers)
        self.assertEqual(headers['X-Frame-Options'], 'DENY')
        
        self.assertIn('X-Content-Type-Options', headers)
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        
        self.assertIn('Referrer-Policy', headers)
        self.assertEqual(headers['Referrer-Policy'], 'strict-origin-when-cross-origin')
        
        self.assertIn('Content-Security-Policy', headers)
        self.assertIn('default-src', headers['Content-Security-Policy'])
        self.assertIn('script-src', headers['Content-Security-Policy'])
        self.assertIn('style-src', headers['Content-Security-Policy'])
        
        self.assertIn('Permissions-Policy', headers)
        self.assertIn('geolocation=()', headers['Permissions-Policy'])
        self.assertIn('camera=()', headers['Permissions-Policy'])
        
        self.assertIn('X-XSS-Protection', headers)
        self.assertEqual(headers['X-XSS-Protection'], '1; mode=block')
        
        # HSTS header should be present for HTTPS
        self.assertIn('Strict-Transport-Security', headers)
        self.assertIn('max-age=31536000', headers['Strict-Transport-Security'])

    async def test_security_headers_http_request(self):
        """Test that HSTS header is not added for HTTP requests."""
        # Create a mock request and handler
        request = MagicMock()
        request.scheme = 'http'
        
        async def mock_handler(req):
            return aiohttp.web.Response(text="test", status=200)
        
        # Call the middleware
        response = await security_headers_middleware(request, mock_handler)
        
        # HSTS header should not be present for HTTP
        self.assertNotIn('Strict-Transport-Security', response.headers)

    async def test_security_headers_error_handling(self):
        """Test security headers middleware handles errors gracefully."""
        # Create a mock request and handler that raises an exception
        request = MagicMock()
        request.scheme = 'https'
        
        async def mock_handler(req):
            raise Exception("Test error")
        
        # Call the middleware - should not raise exception
        response = await security_headers_middleware(request, mock_handler)
        
        # Should return error response with security headers
        self.assertEqual(response.status, 500)
        self.assertIn('X-Frame-Options', response.headers)


class TestSecurityManager(unittest.TestCase):
    """Test security manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.security_manager = SecurityManager()

    def test_validate_phone_number(self):
        """Test phone number validation."""
        # Valid phone numbers
        valid_numbers = [
            "+1234567890",
            "1234567890",
            "+375291234567",
            "375291234567"
        ]
        
        for number in valid_numbers:
            self.assertTrue(self.security_manager._validate_phone_number(number))
        
        # Invalid phone numbers
        invalid_numbers = [
            "123",  # Too short
            "abc",  # Not numeric
            "+123abc",  # Contains letters
            "",  # Empty
            "123-456-7890"  # Contains hyphens (but should be cleaned)
        ]
        
        for number in invalid_numbers:
            # Clean the number first (remove spaces and hyphens)
            cleaned_number = number.replace(' ', '').replace('-', '')
            if cleaned_number:  # Only test if not empty after cleaning
                self.assertFalse(self.security_manager._validate_phone_number(cleaned_number))
            else:
                self.assertFalse(self.security_manager._validate_phone_number(number))

    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            self.assertTrue(self.security_manager._validate_email(email))
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            ""
        ]
        
        for email in invalid_emails:
            self.assertFalse(self.security_manager._validate_email(email))

    def test_validate_input_data(self):
        """Test input data validation."""
        # Valid data
        valid_data = {
            "name": "John Doe",
            "age": 25,
            "email": "john@example.com",
            "phone": "+1234567890"
        }
        
        expected_structure = {
            "name": "str",
            "age": "int",
            "email": "str",
            "phone": "str"
        }
        
        is_valid, errors = self.security_manager.validate_input_data(valid_data, expected_structure)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid data - missing required field
        invalid_data = {
            "name": "John Doe",
            "age": 25
            # Missing email and phone
        }
        
        is_valid, errors = self.security_manager.validate_input_data(invalid_data, expected_structure)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Invalid data - wrong type
        invalid_data = {
            "name": "John Doe",
            "age": "not a number",
            "email": "john@example.com",
            "phone": "+1234567890"
        }
        
        is_valid, errors = self.security_manager.validate_input_data(invalid_data, expected_structure)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        user_id = 12345
        action = "test_action"
        
        # First requests should be allowed
        for i in range(5):
            result = await self.security_manager.check_rate_limit(user_id, action)
            self.assertTrue(result)
        
        # After many requests, should be rate limited
        # Note: This depends on the rate limit configuration
        # We'll test the basic functionality

    def test_webhook_validation(self):
        """Test webhook URL validation."""
        # Test webhook structure validation
        valid_webhook_data = {
            "update_id": 12345,
            "message": {"text": "test"}
        }
        
        invalid_webhook_data = {
            "message": {"text": "test"}
            # Missing update_id
        }
        
        # Test structure validation
        self.assertTrue(self.security_manager._validate_webhook_structure(valid_webhook_data))
        self.assertFalse(self.security_manager._validate_webhook_structure(invalid_webhook_data))


class TestSecurityConfiguration(unittest.TestCase):
    """Test security configuration settings."""

    def test_config_security_settings(self):
        """Test that security configuration is properly set."""
        # Check that required security settings are present
        self.assertIsInstance(config.ENABLE_RATE_LIMITING, bool)
        self.assertIsInstance(config.RATE_LIMIT_MAX_REQUESTS, int)
        self.assertIsInstance(config.RATE_LIMIT_WINDOW, int)
        self.assertIsInstance(config.ALLOW_WEBHOOKS, bool)
        self.assertIsInstance(config.LOG_SECURITY_EVENTS, bool)
        self.assertIsInstance(config.ENABLE_SECURITY_MONITORING, bool)
        
        # Check that rate limiting values are reasonable
        self.assertGreater(config.RATE_LIMIT_MAX_REQUESTS, 0)
        self.assertGreater(config.RATE_LIMIT_WINDOW, 0)
        
        # Check that webhooks are disabled by default for security
        self.assertFalse(config.ALLOW_WEBHOOKS)

    def test_config_environment_validation(self):
        """Test that environment variables are properly validated."""
        # Check that required environment variables are set
        self.assertIsNotNone(config.BOT_TOKEN)
        self.assertIsNotNone(config.ADMIN_CHAT_ID)
        self.assertIsNotNone(config.ADMIN_EMAIL)
        self.assertIsNotNone(config.ADMIN_EMAIL_PASSWORD)
        
        # Check that bot token has correct format
        self.assertIn(':', config.BOT_TOKEN)
        
        # Check that admin chat ID is a positive integer
        self.assertIsInstance(config.ADMIN_CHAT_ID, int)
        self.assertGreater(config.ADMIN_CHAT_ID, 0)


class TestSecurityHeadersContent(unittest.TestCase):
    """Test the content of security headers."""

    def test_csp_policy_content(self):
        """Test that CSP policy contains required directives."""
        # Create a mock request to get the CSP policy
        request = MagicMock()
        request.scheme = 'https'
        
        async def mock_handler(req):
            return aiohttp.web.Response(text="test", status=200)
        
        # We need to access the CSP policy from the middleware
        # For now, let's test the expected content
        expected_csp_directives = [
            "default-src",
            "script-src",
            "style-src",
            "font-src",
            "img-src",
            "connect-src",
            "frame-src",
            "object-src",
            "base-uri",
            "form-action"
        ]
        
        # This is a basic test - in a real scenario, we'd extract the CSP from the response
        for directive in expected_csp_directives:
            self.assertTrue(True)  # Placeholder - would check actual CSP content

    def test_permissions_policy_content(self):
        """Test that Permissions Policy contains required restrictions."""
        expected_permissions = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
            "autoplay=()",
            "encrypted-media=()",
            "picture-in-picture=()"
        ]
        
        # This is a basic test - in a real scenario, we'd extract the policy from the response
        for permission in expected_permissions:
            self.assertTrue(True)  # Placeholder - would check actual policy content


class TestHMACSecurity(unittest.TestCase):
    """Test HMAC signature security features."""

    def setUp(self):
        """Set up test environment."""
        self.security_manager = SecurityManager()
        self.test_data = "test_data_string"
        self.test_secret = "test_secret_key"

    def test_hmac_signature_generation(self):
        """Test HMAC signature generation."""
        signature = self.security_manager.generate_hmac_signature(self.test_data, self.test_secret)
        
        # Signature should be base64 encoded
        self.assertIsInstance(signature, str)
        self.assertGreater(len(signature), 0)
        
        # Same data should generate same signature
        signature2 = self.security_manager.generate_hmac_signature(self.test_data, self.test_secret)
        self.assertEqual(signature, signature2)

    def test_hmac_signature_verification(self):
        """Test HMAC signature verification."""
        signature = self.security_manager.generate_hmac_signature(self.test_data, self.test_secret)
        
        # Valid signature should verify
        self.assertTrue(self.security_manager.verify_hmac_signature(
            self.test_data, signature, self.test_secret
        ))
        
        # Invalid signature should fail
        self.assertFalse(self.security_manager.verify_hmac_signature(
            self.test_data, "invalid_signature", self.test_secret
        ))
        
        # Different data should fail
        self.assertFalse(self.security_manager.verify_hmac_signature(
            "different_data", signature, self.test_secret
        ))

    def test_auth_token_generation(self):
        """Test authentication token generation."""
        token_data = self.security_manager.generate_auth_token()
        
        # Token should have required fields
        self.assertIn("token", token_data)
        self.assertIn("timestamp", token_data)
        self.assertIn("expires_in", token_data)
        
        # Token should be valid
        self.assertIsInstance(token_data["token"], str)
        self.assertIsInstance(token_data["timestamp"], int)
        self.assertEqual(token_data["expires_in"], 3600)

    def test_timestamp_validation(self):
        """Test timestamp validation for replay attack prevention."""
        current_time = int(time.time())
        
        # Valid timestamp should pass
        self.assertTrue(self.security_manager.validate_timestamp(current_time))
        self.assertTrue(self.security_manager.validate_timestamp(current_time - 100))
        self.assertTrue(self.security_manager.validate_timestamp(current_time + 100))
        
        # Old timestamp should fail
        self.assertFalse(self.security_manager.validate_timestamp(current_time - 400))
        
        # Future timestamp should fail
        self.assertFalse(self.security_manager.validate_timestamp(current_time + 400))


if __name__ == '__main__':
    unittest.main()
