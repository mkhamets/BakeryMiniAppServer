import unittest
import os
from unittest.mock import patch
import sys
import tempfile
import shutil

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

from config import config, BOT_TOKEN, BASE_WEBAPP_URL, ADMIN_CHAT_ID, ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD, SMTP_SERVER


class TestConfig(unittest.TestCase):
    """Test cases for configuration module."""

    def setUp(self):
        """Set up test environment."""
        # Store original environment variables
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_bot_token_default_value(self):
        """Test that BOT_TOKEN has a default value when not set in environment."""
        # Remove BOT_TOKEN from environment
        if 'BOT_TOKEN' in os.environ:
            del os.environ['BOT_TOKEN']
        
        # Reload config module to get fresh values
        import importlib
        import config
        importlib.reload(config)
        
        # Check that BOT_TOKEN has a default value
        self.assertIsNotNone(config.BOT_TOKEN)
        self.assertIsInstance(config.BOT_TOKEN, str)
        self.assertGreater(len(config.BOT_TOKEN), 0)

    def test_bot_token_from_environment(self):
        """Test that BOT_TOKEN is loaded from environment variable."""
        test_token = "test_token_12345"
        os.environ['BOT_TOKEN'] = test_token
        
        # Reload config module
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.BOT_TOKEN, test_token)

    def test_base_webapp_url_default_value(self):
        """Test that BASE_WEBAPP_URL has a default value."""
        if 'BASE_WEBAPP_URL' in os.environ:
            del os.environ['BASE_WEBAPP_URL']
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertIsNotNone(config.BASE_WEBAPP_URL)
        self.assertIsInstance(config.BASE_WEBAPP_URL, str)
        self.assertIn('herokuapp.com', config.BASE_WEBAPP_URL)

    def test_base_webapp_url_from_environment(self):
        """Test that BASE_WEBAPP_URL is loaded from environment variable."""
        test_url = "https://test-app.herokuapp.com/bot-app/"
        os.environ['BASE_WEBAPP_URL'] = test_url
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.BASE_WEBAPP_URL, test_url)

    def test_admin_chat_id_default_value(self):
        """Test that ADMIN_CHAT_ID has a default value."""
        if 'ADMIN_CHAT_ID' in os.environ:
            del os.environ['ADMIN_CHAT_ID']
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertIsNotNone(config.ADMIN_CHAT_ID)
        self.assertIsInstance(config.ADMIN_CHAT_ID, int)

    def test_admin_chat_id_from_environment(self):
        """Test that ADMIN_CHAT_ID is loaded from environment variable."""
        test_id = "123456789"
        os.environ['ADMIN_CHAT_ID'] = test_id
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.ADMIN_CHAT_ID, int(test_id))

    def test_admin_email_default_value(self):
        """Test that ADMIN_EMAIL has a default value."""
        if 'ADMIN_EMAIL' in os.environ:
            del os.environ['ADMIN_EMAIL']
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertIsNotNone(config.ADMIN_EMAIL)
        self.assertIsInstance(config.ADMIN_EMAIL, str)
        self.assertIn('@', config.ADMIN_EMAIL)

    def test_admin_email_from_environment(self):
        """Test that ADMIN_EMAIL is loaded from environment variable."""
        test_email = "test@example.com"
        os.environ['ADMIN_EMAIL'] = test_email
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.ADMIN_EMAIL, test_email)

    def test_admin_email_password_from_environment(self):
        """Test that ADMIN_EMAIL_PASSWORD is loaded from environment variable."""
        test_password = "test_password_123"
        os.environ['ADMIN_EMAIL_PASSWORD'] = test_password
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.ADMIN_EMAIL_PASSWORD, test_password)

    def test_smtp_server_default_value(self):
        """Test that SMTP_SERVER has a default value."""
        if 'SMTP_SERVER' in os.environ:
            del os.environ['SMTP_SERVER']
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertIsNotNone(config.SMTP_SERVER)
        self.assertIsInstance(config.SMTP_SERVER, str)
        self.assertIn('smtp.gmail.com', config.SMTP_SERVER)

    def test_smtp_server_from_environment(self):
        """Test that SMTP_SERVER is loaded from environment variable."""
        test_server = "smtp.example.com"
        os.environ['SMTP_SERVER'] = test_server
        
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.SMTP_SERVER, test_server)

    def test_admin_chat_id_invalid_value(self):
        """Test that invalid ADMIN_CHAT_ID raises ValueError."""
        os.environ['ADMIN_CHAT_ID'] = "invalid_id"
        
        with self.assertRaises(ValueError):
            import importlib
            import config
            importlib.reload(config)


class TestSecureConfig(unittest.TestCase):
    """Test cases for SecureConfig class."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after tests."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456:test-token',
        'ADMIN_CHAT_ID': '123456789',
        'ADMIN_EMAIL': 'test@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password'
    })
    def test_secure_config_initialization(self):
        """Test SecureConfig initialization with valid environment."""
        # Clear any existing config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        import importlib
        import config
        importlib.reload(config)
        
        # Test that config instance is created
        self.assertIsNotNone(config.config)
        self.assertIsInstance(config.config, config.SecureConfig)
        
        # Test basic properties
        self.assertEqual(config.config.BOT_TOKEN, '123456:test-token')
        self.assertEqual(config.config.ADMIN_CHAT_ID, 123456789)
        self.assertEqual(config.config.ADMIN_EMAIL, 'test@example.com')

    def test_secure_config_missing_required_vars(self):
        """Test SecureConfig fails with missing required environment variables."""
        # Clear environment
        os.environ.clear()
        
        # Clear any existing config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        with self.assertRaises(EnvironmentError):
            import importlib
            import config
            importlib.reload(config)

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456:test-token',
        'ADMIN_CHAT_ID': '123456789',
        'ADMIN_EMAIL': 'test@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password',
        'ENABLE_RATE_LIMITING': 'true',
        'RATE_LIMIT_MAX_REQUESTS': '200',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_secure_config_security_settings(self):
        """Test security-related configuration settings."""
        # Clear any existing config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        import importlib
        import config
        importlib.reload(config)
        
        # Test security settings
        self.assertTrue(config.config.ENABLE_RATE_LIMITING)
        self.assertEqual(config.config.RATE_LIMIT_MAX_REQUESTS, 200)
        self.assertEqual(config.config.LOG_LEVEL, 'DEBUG')

    @patch.dict(os.environ, {
        'BOT_TOKEN': '123456:test-token',
        'ADMIN_CHAT_ID': '123456789',
        'ADMIN_EMAIL': 'test@example.com',
        'ADMIN_EMAIL_PASSWORD': 'test-password'
    })
    def test_secure_config_webhook_security_config(self):
        """Test webhook security configuration method."""
        # Clear any existing config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        import importlib
        import config
        importlib.reload(config)
        
        webhook_config = config.config.get_webhook_security_config()
        
        self.assertIsInstance(webhook_config, dict)
        self.assertIn('allowed', webhook_config)
        self.assertIn('trusted_domains', webhook_config)
        self.assertIn('secret_configured', webhook_config)


if __name__ == '__main__':
    unittest.main() 