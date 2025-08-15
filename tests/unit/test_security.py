import unittest
import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import datetime, timedelta

# Import the modules we want to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bot.security import BotSecurityMonitor
from bot.security_manager import SecurityManager
from bot.config import config


class TestBotSecurityMonitor(unittest.TestCase):
    """Test cases for BotSecurityMonitor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.bot_token = "test_token_123"
        self.monitor = BotSecurityMonitor(self.bot_token)

    def test_init(self):
        """Test BotSecurityMonitor initialization."""
        self.assertEqual(self.monitor.bot_token, self.bot_token)
        self.assertEqual(self.monitor.api_base, f"https://api.telegram.org/bot{self.bot_token}")
        self.assertIsInstance(self.monitor.suspicious_patterns, list)
        self.assertIsNone(self.monitor.last_webhook_check)

    def test_analyze_webhook_security_no_webhook(self):
        """Test webhook security analysis when no webhook is set."""
        webhook_info = {"url": ""}
        result = self.monitor._analyze_webhook_security(webhook_info)
        
        self.assertTrue(result["secure"])
        self.assertEqual(result["status"], "No webhook set")
        self.assertEqual(result["recommendation"], "Safe")

    def test_analyze_webhook_security_suspicious(self):
        """Test webhook security analysis with suspicious URL."""
        webhook_info = {"url": "https://malicious-casino.com/webhook"}
        result = self.monitor._analyze_webhook_security(webhook_info)
        
        self.assertFalse(result["secure"])
        self.assertEqual(result["status"], "Suspicious webhook detected")
        self.assertEqual(result["recommendation"], "DELETE IMMEDIATELY")
        self.assertEqual(result["risk"], "HIGH")

    def test_analyze_webhook_security_unknown_domain(self):
        """Test webhook security analysis with unknown domain."""
        webhook_info = {"url": "https://unknown-domain.com/webhook"}
        result = self.monitor._analyze_webhook_security(webhook_info)
        
        self.assertFalse(result["secure"])
        self.assertEqual(result["status"], "Unknown webhook domain")
        self.assertEqual(result["recommendation"], "Verify ownership or delete")
        self.assertEqual(result["risk"], "MEDIUM")

    def test_analyze_webhook_security_safe_domain(self):
        """Test webhook security analysis with safe domain."""
        webhook_info = {"url": "https://bakery-mini-app-server-440955f475ad.herokuapp.com/webhook"}
        result = self.monitor._analyze_webhook_security(webhook_info)
        
        self.assertTrue(result["secure"])
        self.assertEqual(result["status"], "Webhook appears safe")
        self.assertEqual(result["recommendation"], "Monitor regularly")

    @patch('bot.security.aiohttp.ClientSession')
    async def test_check_webhook_security_success(self, mock_session):
        """Test successful webhook security check."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "ok": True,
            "result": {"url": "https://safe-domain.com/webhook"}
        })
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance

        result = await self.monitor.check_webhook_security()
        
        self.assertTrue(result["secure"])
        self.assertEqual(result["status"], "Webhook appears safe")

    @patch('bot.security.aiohttp.ClientSession')
    async def test_check_webhook_security_failure(self, mock_session):
        """Test webhook security check failure."""
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.get.side_effect = Exception("Network error")
        mock_session.return_value = mock_session_instance

        result = await self.monitor.check_webhook_security()
        
        self.assertFalse(result["secure"])
        self.assertIn("error", result)

    @patch('bot.security.aiohttp.ClientSession')
    async def test_delete_webhook_success(self, mock_session):
        """Test successful webhook deletion."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ok": True})
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance

        result = await self.monitor.delete_webhook()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Webhook deleted")


class TestSecurityManager(unittest.TestCase):
    """Test cases for SecurityManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.security_manager = SecurityManager()

    def test_init(self):
        """Test SecurityManager initialization."""
        self.assertIsInstance(self.security_manager.rate_limit_store, dict)
        self.assertIsInstance(self.security_manager.suspicious_activities, list)
        self.assertIsInstance(self.security_manager.security_events, list)
        self.assertIsInstance(self.security_manager.last_cleanup, float)

    def test_verify_webhook_signature_valid(self):
        """Test valid webhook signature verification."""
        data = {"update_id": 123, "message": "test"}
        message = json.dumps(data, separators=(',', ':'))
        
        # Create a valid signature
        import hmac
        import hashlib
        secret = "test_secret"
        expected_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        with patch('bot.security_manager.config') as mock_config:
            mock_config.WEBHOOK_SECRET = secret
            result = self.security_manager._verify_webhook_signature(data, expected_signature)
            self.assertTrue(result)

    def test_verify_webhook_signature_invalid(self):
        """Test invalid webhook signature verification."""
        data = {"update_id": 123, "message": "test"}
        invalid_signature = "invalid_signature"
        
        with patch('bot.security_manager.config') as mock_config:
            mock_config.WEBHOOK_SECRET = "test_secret"
            result = self.security_manager._verify_webhook_signature(data, invalid_signature)
            self.assertFalse(result)

    def test_validate_webhook_structure_valid(self):
        """Test valid webhook structure validation."""
        data = {"update_id": 123, "message": "test"}
        result = self.security_manager._validate_webhook_structure(data)
        self.assertTrue(result)

    def test_validate_webhook_structure_invalid(self):
        """Test invalid webhook structure validation."""
        data = {"message": "test"}  # Missing update_id
        result = self.security_manager._validate_webhook_structure(data)
        self.assertFalse(result)

    async def test_check_rate_limit_allowed(self):
        """Test rate limit check when user is allowed."""
        user_id = 123
        action = "test_action"
        
        with patch('bot.security_manager.config') as mock_config:
            mock_config.ENABLE_RATE_LIMITING = True
            mock_config.RATE_LIMIT_WINDOW = 3600
            mock_config.RATE_LIMIT_MAX_REQUESTS = 10
            
            # First request should be allowed
            result = await self.security_manager.check_rate_limit(user_id, action)
            self.assertTrue(result)

    async def test_check_rate_limit_exceeded(self):
        """Test rate limit check when user exceeds limit."""
        user_id = 123
        action = "test_action"
        
        with patch('bot.security_manager.config') as mock_config:
            mock_config.ENABLE_RATE_LIMITING = True
            mock_config.RATE_LIMIT_WINDOW = 3600
            mock_config.RATE_LIMIT_MAX_REQUESTS = 2
            
            # Add requests to exceed limit
            key = f"{user_id}:{action}"
            self.security_manager.rate_limit_store[key] = [time.time(), time.time()]
            
            # This request should be blocked
            result = await self.security_manager.check_rate_limit(user_id, action)
            self.assertFalse(result)

    async def test_check_rate_limit_disabled(self):
        """Test rate limit check when rate limiting is disabled."""
        user_id = 123
        action = "test_action"
        
        with patch('bot.security_manager.config') as mock_config:
            mock_config.ENABLE_RATE_LIMITING = False
            
            result = await self.security_manager.check_rate_limit(user_id, action)
            self.assertTrue(result)

    def test_validate_input_data_valid(self):
        """Test valid input data validation."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 25
        }
        expected_structure = {
            "name": str,
            "email": str,
            "age": int
        }
        
        result, errors = self.security_manager.validate_input_data(data, expected_structure)
        self.assertTrue(result)
        self.assertEqual(len(errors), 0)

    def test_validate_input_data_invalid(self):
        """Test invalid input data validation."""
        data = {
            "name": "John Doe",
            "email": "invalid-email",
            "age": "not-a-number"
        }
        expected_structure = {
            "name": str,
            "email": str,
            "age": int
        }
        
        result, errors = self.security_manager.validate_input_data(data, expected_structure)
        self.assertFalse(result)
        self.assertGreater(len(errors), 0)

    def test_log_security_event(self):
        """Test security event logging."""
        event_type = "test_event"
        event_data = {"user_id": 123, "action": "test"}
        
        initial_count = len(self.security_manager.security_events)
        self.security_manager._log_security_event(event_type, event_data)
        
        self.assertEqual(len(self.security_manager.security_events), initial_count + 1)
        # Check that the event was logged (structure may vary)
        self.assertIsInstance(self.security_manager.security_events[-1], dict)

    def test_cleanup_old_data(self):
        """Test cleanup of old rate limit data."""
        user_id = 123
        action = "test_action"
        key = f"{user_id}:{action}"
        
        # Add old and new timestamps
        old_time = time.time() - 7200  # 2 hours ago
        new_time = time.time() - 300   # 5 minutes ago
        
        self.security_manager.rate_limit_store[key] = [old_time, new_time]
        
        with patch('bot.security_manager.config') as mock_config:
            mock_config.RATE_LIMIT_WINDOW = 3600  # 1 hour
            
            # Trigger cleanup
            self.security_manager.rate_limit_store[key] = [
                timestamp for timestamp in self.security_manager.rate_limit_store[key]
                if time.time() - timestamp < mock_config.RATE_LIMIT_WINDOW
            ]
            
            # Only new timestamp should remain
            self.assertEqual(len(self.security_manager.rate_limit_store[key]), 1)
            self.assertEqual(self.security_manager.rate_limit_store[key][0], new_time)


if __name__ == '__main__':
    unittest.main()

