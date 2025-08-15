import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from aiogram.types import Message, CallbackQuery, User, Chat

# Import the modules we want to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bot.security_middleware import SecurityMiddleware


class TestSecurityMiddleware(unittest.TestCase):
    """Test cases for SecurityMiddleware class."""

    def setUp(self):
        """Set up test fixtures."""
        self.middleware = SecurityMiddleware()

    def test_init(self):
        """Test SecurityMiddleware initialization."""
        self.assertIsInstance(self.middleware, SecurityMiddleware)

    @patch('bot.security_middleware.security_manager')
    async def test_middleware_allows_valid_message(self, mock_security_manager):
        """Test that middleware allows valid messages."""
        mock_security_manager.check_rate_limit.return_value = True
        
        # Create a mock message
        mock_user = MagicMock()
        mock_user.id = 123
        message = MagicMock(spec=Message)
        message.from_user = mock_user
        message.web_app_data = None
        message.text = "test"
        
        # Create a mock handler
        handler = AsyncMock()
        handler.return_value = "OK"
        
        # Test the middleware
        result = await self.middleware(handler, message, {})
        
        self.assertEqual(result, "OK")
        handler.assert_called_once()

    @patch('bot.security_middleware.security_manager')
    async def test_middleware_blocks_rate_limited_user(self, mock_security_manager):
        """Test that middleware blocks rate-limited users."""
        mock_security_manager.check_rate_limit.return_value = False
        
        # Create a mock message
        mock_user = MagicMock()
        mock_user.id = 123
        message = MagicMock(spec=Message)
        message.from_user = mock_user
        message.web_app_data = None
        message.text = "test"
        
        # Create a mock handler
        handler = AsyncMock()
        
        # Test the middleware
        result = await self.middleware(handler, message, {})
        
        # Should return None (blocked)
        self.assertIsNone(result)
        handler.assert_not_called()

    def test_extract_user_id_from_message(self):
        """Test user ID extraction from message."""
        mock_user = MagicMock()
        mock_user.id = 123
        message = MagicMock(spec=Message)
        message.from_user = mock_user
        
        user_id = self.middleware._extract_user_id(message)
        self.assertEqual(user_id, 123)

    def test_extract_user_id_from_callback(self):
        """Test user ID extraction from callback query."""
        mock_user = MagicMock()
        mock_user.id = 456
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = mock_user
        
        user_id = self.middleware._extract_user_id(callback)
        self.assertEqual(user_id, 456)

    def test_get_action_name_text_message(self):
        """Test action name generation for text messages."""
        message = MagicMock(spec=Message)
        message.web_app_data = None
        message.text = "hello"
        message.photo = None
        message.document = None
        
        action = self.middleware._get_action_name(message)
        self.assertEqual(action, "text_hello")

    def test_get_action_name_web_app_data(self):
        """Test action name generation for web app data."""
        message = MagicMock(spec=Message)
        message.web_app_data = MagicMock()
        message.text = None
        message.photo = None
        message.document = None
        
        action = self.middleware._get_action_name(message)
        self.assertEqual(action, "web_app_data")


if __name__ == '__main__':
    unittest.main()

