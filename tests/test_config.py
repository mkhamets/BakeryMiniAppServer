"""
Test Configuration
Sets up the test environment for order placement tests
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def setup_test_environment():
    """Set up test environment variables and paths."""
    
    # Set test environment
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['BOT_TOKEN'] = 'test_token_123456789'
    os.environ['BASE_WEBAPP_URL'] = 'http://localhost:8000/test/'
    os.environ['ADMIN_CHAT_ID'] = '123456789'
    os.environ['ADMIN_EMAIL'] = 'test@example.com'
    os.environ['ADMIN_EMAIL_PASSWORD'] = 'test_password'
    os.environ['SMTP_SERVER'] = 'smtp.test.com'
    os.environ['ENABLE_EMAIL_NOTIFICATIONS'] = 'false'
    
    # Create temporary data directory for tests
    test_data_dir = tempfile.mkdtemp(prefix='bakery_test_')
    os.environ['DATA_DIR'] = test_data_dir
    
    # Create test data files
    create_test_data_files(test_data_dir)
    
    return test_data_dir

def create_test_data_files(data_dir):
    """Create test data files."""
    
    # Create products data
    products_data = {
        "categories": {
            "category_bakery": {
                "name": "Хлебобулочные изделия",
                "products": [
                    {
                        "id": "4e736e2b-5ce0-434e-af44-7df5bae477ea",
                        "name": "Завиванец с маком",
                        "price": "18",
                        "description": "Свежий завиванец с маком",
                        "category": "category_bakery"
                    }
                ]
            }
        }
    }
    
    # Create order counter
    order_counter = {
        "counter": 0,
        "last_reset_month": 8
    }
    
    # Write test files
    products_file = os.path.join(data_dir, 'products_scraped.json')
    counter_file = os.path.join(data_dir, 'order_counter.json')
    
    import json
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(products_data, f, ensure_ascii=False, indent=2)
    
    with open(counter_file, 'w', encoding='utf-8') as f:
        json.dump(order_counter, f, ensure_ascii=False, indent=2)

def cleanup_test_environment(test_data_dir):
    """Clean up test environment."""
    if test_data_dir and os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    
    # Clear test environment variables
    test_env_vars = [
        'ENVIRONMENT', 'BOT_TOKEN', 'BASE_WEBAPP_URL', 'ADMIN_CHAT_ID',
        'ADMIN_EMAIL', 'ADMIN_EMAIL_PASSWORD', 'SMTP_SERVER', 
        'ENABLE_EMAIL_NOTIFICATIONS', 'DATA_DIR'
    ]
    
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var]

def mock_bot_functions():
    """Mock bot functions for testing."""
    
    # Mock the bot instance
    class MockBot:
        def __init__(self):
            self.send_message = MockAsyncFunction()
    
    class MockAsyncFunction:
        async def __call__(self, *args, **kwargs):
            return True
    
    return MockBot()

class MockAsyncFunction:
    """Mock async function for testing."""
    
    def __init__(self, return_value=None, side_effect=None):
        self.return_value = return_value
        self.side_effect = side_effect
        self.call_count = 0
        self.call_args = []
        self.call_kwargs = []
    
    async def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.call_args.append(args)
        self.call_kwargs.append(kwargs)
        
        if self.side_effect:
            if callable(self.side_effect):
                return self.side_effect(*args, **kwargs)
            else:
                raise self.side_effect
        
        return self.return_value
    
    def assert_called(self):
        """Assert that the function was called."""
        assert self.call_count > 0, "Function was not called"
    
    def assert_called_once(self):
        """Assert that the function was called exactly once."""
        assert self.call_count == 1, f"Function was called {self.call_count} times, expected 1"
    
    def assert_called_with(self, *args, **kwargs):
        """Assert that the function was called with specific arguments."""
        self.assert_called()
        for call_args, call_kwargs in zip(self.call_args, self.call_kwargs):
            if call_args == args and call_kwargs == kwargs:
                return
        raise AssertionError(f"Function was not called with {args}, {kwargs}")

def create_test_message(user_id=123456789, chat_id=None):
    """Create a test message object."""
    if chat_id is None:
        chat_id = user_id
    
    message = type('Message', (), {
        'chat': type('Chat', (), {'id': chat_id})(),
        'from_user': type('User', (), {'id': user_id})(),
        'answer': MockAsyncFunction(),
        'reply': MockAsyncFunction()
    })()
    
    return message

def create_test_order_data(delivery_method="courier", **kwargs):
    """Create test order data."""
    base_data = {
        "order_details": {
            "deliveryMethod": delivery_method,
            "firstName": kwargs.get("firstName", "Test"),
            "lastName": kwargs.get("lastName", "User"),
            "middleName": kwargs.get("middleName", "Middle"),
            "phone": kwargs.get("phone", "+375291234567"),
            "email": kwargs.get("email", "test@example.com"),
            "deliveryDate": kwargs.get("deliveryDate", "2025-08-11"),
            "comment": kwargs.get("comment", "Test comment")
        },
        "cart_items": kwargs.get("cart_items", [
            {
                "id": "test_product_1",
                "name": "Test Product 1",
                "price": "25",
                "quantity": 2
            }
        ]),
        "total_amount": kwargs.get("total_amount", 50.0)
    }
    
    # Add delivery-specific fields
    if delivery_method == "courier":
        base_data["order_details"].update({
            "city": kwargs.get("city", "Minsk"),
            "addressLine": kwargs.get("addressLine", "Test Address 123")
        })
    elif delivery_method == "pickup":
        base_data["order_details"].update({
            "pickupAddress": kwargs.get("pickupAddress", "Test Pickup Address"),
            "commentPickup": kwargs.get("commentPickup", "Test pickup comment")
        })
    
    return base_data
