"""
Fixed unit tests for configuration functionality.
Uses proper environment variable mocking to avoid test failures.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import importlib

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))


class TestConfigFixed(unittest.TestCase):
    """Test configuration functionality with proper mocking."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing config module
        if 'config' in sys.modules:
            del sys.modules['config']

    def tearDown(self):
        """Clean up test fixtures."""
        # Clear any existing config module
        if 'config' in sys.modules:
            del sys.modules['config']

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456789:test-bot-token-here',
        'ADMIN_CHAT_ID': '987654321',
        'ADMIN_EMAIL': 'admin@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123'
    })
    def test_config_with_valid_environment_variables(self):
        """Test configuration with valid environment variables."""
        import config
        
        # Check that configuration loaded successfully
        self.assertEqual(config.config.BOT_TOKEN, '123456789:test-bot-token-here')
        self.assertEqual(config.config.ADMIN_CHAT_ID, 987654321)
        self.assertEqual(config.config.ADMIN_EMAIL, 'admin@example.com')
        self.assertEqual(config.config.ADMIN_EMAIL_PASSWORD, 'test-password-123')

    @patch.dict(os.environ, {
        'BOT_TOKEN': 'invalid-token-format',
        'ADMIN_CHAT_ID': '987654321',
        'ADMIN_EMAIL': 'admin@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123'
    })
    def test_config_with_invalid_bot_token_format(self):
        """Test configuration with invalid bot token format."""
        with self.assertRaises(OSError) as context:
            import config
        
        self.assertIn("Invalid BOT_TOKEN format", str(context.exception))

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456789:test-bot-token-here',
        'ADMIN_CHAT_ID': 'invalid-id',
        'ADMIN_EMAIL': 'admin@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123'
    })
    def test_config_with_invalid_admin_chat_id(self):
        """Test configuration with invalid admin chat ID."""
        with self.assertRaises(OSError) as context:
            import config
        
        self.assertIn("ADMIN_CHAT_ID must be a valid positive integer", str(context.exception))

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456789:test-bot-token-here',
        'ADMIN_CHAT_ID': '987654321',
        'ADMIN_EMAIL': 'invalid-email',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123'
    })
    def test_config_with_invalid_email_format(self):
        """Test configuration with invalid email format."""
        # Email format is not validated in config, so this should work
        import config
        
        self.assertEqual(config.config.ADMIN_EMAIL, 'invalid-email')

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456789:test-bot-token-here',
        'ADMIN_CHAT_ID': '987654321',
        'ADMIN_EMAIL': 'admin@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123',
        'ENABLE_RATE_LIMITING': 'true',
        'RATE_LIMIT_MAX_REQUESTS': '10',
        'RATE_LIMIT_WINDOW': '60',
        'ALLOW_WEBHOOKS': 'false',
        'LOG_SECURITY_EVENTS': 'true',
        'ENABLE_SECURITY_MONITORING': 'true'
    })
    def test_config_security_settings(self):
        """Test security configuration settings."""
        import config
        
        # Check security settings
        self.assertTrue(config.config.ENABLE_RATE_LIMITING)
        self.assertEqual(config.config.RATE_LIMIT_MAX_REQUESTS, 10)
        self.assertEqual(config.config.RATE_LIMIT_WINDOW, 60)
        self.assertFalse(config.config.ALLOW_WEBHOOKS)
        self.assertTrue(config.config.LOG_SECURITY_EVENTS)
        self.assertTrue(config.config.ENABLE_SECURITY_MONITORING)

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456789:test-bot-token-here',
        'ADMIN_CHAT_ID': '987654321',
        'ADMIN_EMAIL': 'admin@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123'
    })
    def test_config_default_values(self):
        """Test configuration default values."""
        import config
        
        # Check that required fields are present
        self.assertIsNotNone(config.config.BOT_TOKEN)
        self.assertIsNotNone(config.config.ADMIN_CHAT_ID)
        self.assertIsNotNone(config.config.ADMIN_EMAIL)
        self.assertIsNotNone(config.config.ADMIN_EMAIL_PASSWORD)
        
        # Check that bot token has correct format
        self.assertIn(':', config.config.BOT_TOKEN)
        
        # Check that admin chat ID is a positive integer
        self.assertIsInstance(config.config.ADMIN_CHAT_ID, int)
        self.assertGreater(config.config.ADMIN_CHAT_ID, 0)

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456789:test-bot-token-here',
        'ADMIN_CHAT_ID': '987654321',
        'ADMIN_EMAIL': 'admin@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123',
        'WEBHOOK_SECRET': 'test-webhook-secret'
    })
    def test_config_optional_webhook_secret(self):
        """Test configuration with optional webhook secret."""
        import config
        
        # Check that webhook secret is set
        self.assertEqual(config.config.WEBHOOK_SECRET, 'test-webhook-secret')

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456789:test-bot-token-here',
        'ADMIN_CHAT_ID': '987654321',
        'ADMIN_EMAIL': 'admin@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123'
    })
    def test_config_missing_optional_variables(self):
        """Test configuration with missing optional variables."""
        import config
        
        # Check that optional variables have default values
        self.assertIsNone(config.config.WEBHOOK_SECRET)

    def test_config_missing_required_variables(self):
        """Test configuration with missing required variables."""
        # Clear all environment variables
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(OSError) as context:
                import config
            
            self.assertIn("Missing required environment variables", str(context.exception))

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456789:test-bot-token-here',
        'ADMIN_CHAT_ID': '987654321',
        'ADMIN_EMAIL': 'admin@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password-123',
        'ALLOW_WEBHOOKS': 'true',
        'TRUSTED_DOMAINS': 'bakery-mini-app-server-440955f475ad.herokuapp.com,drazhin.by,localhost'
    })
    def test_config_validation_methods(self):
        """Test configuration validation methods."""
        import config
        
        # Test webhook URL validation
        valid_urls = [
            "https://bakery-mini-app-server-440955f475ad.herokuapp.com/webhook",
            "https://drazhin.by/webhook"
        ]
        
        for url in valid_urls:
            self.assertTrue(config.config.validate_webhook_url(url))
        
        # Test invalid webhook URLs
        invalid_urls = [
            "http://malicious-site.com/webhook",
            "https://suspicious-domain.work.gd/webhook",
            "https://casino-site.com/webhook"
        ]
        
        for url in invalid_urls:
            self.assertFalse(config.config.validate_webhook_url(url))


if __name__ == '__main__':
    unittest.main()
