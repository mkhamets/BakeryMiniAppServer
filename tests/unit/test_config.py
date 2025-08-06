import unittest
import os
from unittest.mock import patch
import sys
import tempfile
import shutil

# Add the bot directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

from config import BOT_TOKEN, BASE_WEBAPP_URL, ADMIN_CHAT_ID, ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD, SMTP_SERVER


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


if __name__ == '__main__':
    unittest.main() 