import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add the bot directory to the path to import script functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bot'))

class TestCheckoutValidation(unittest.TestCase):
    """Test suite for checkout validation logic, order, and error styles"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Mock DOM elements
        self.mock_dom_elements = {
            'last-name': Mock(value='', id='last-name'),
            'first-name': Mock(value='', id='first-name'),
            'middle-name': Mock(value='', id='middle-name'),
            'phone-number': Mock(value='', id='phone-number'),
            'email': Mock(value='', id='email'),
            'delivery-date': Mock(value='', id='delivery-date'),
            'delivery-courier-radio': Mock(value='', id='delivery-courier-radio'),
            'city': Mock(value='', id='city'),
            'address-line': Mock(value='', id='address-line'),
            'payment-cash-radio': Mock(value='', id='payment-cash-radio'),
            'pickup_1': Mock(value='', id='pickup_1'),
            'payment-erip-radio-pickup': Mock(value='', id='payment-erip-radio-pickup'),
        }
        
        # Mock error message elements
        self.mock_error_elements = {
            'lastName-error': Mock(id='lastName-error'),
            'firstName-error': Mock(id='firstName-error'),
            'middleName-error': Mock(id='middleName-error'),
            'phoneNumber-error': Mock(id='phoneNumber-error'),
            'email-error': Mock(id='email-error'),
            'deliveryDate-error': Mock(id='deliveryDate-error'),
            'deliveryMethod-error': Mock(id='deliveryMethod-error'),
            'city-error': Mock(id='city-error'),
            'addressLine-error': Mock(id='addressLine-error'),
            'paymentMethod-error': Mock(id='paymentMethod-error'),
            'pickupAddress-error': Mock(id='pickupAddress-error'),
            'paymentMethodPickup-error': Mock(id='paymentMethodPickup-error'),
        }
        
        # Mock container elements for radio groups
        self.mock_containers = {
            'payment-method-section': Mock(id='payment-method-section'),
            'pickup-radio-group': Mock(id='pickup-radio-group'),
            'payment-method-section-pickup': Mock(id='payment-method-section-pickup'),
        }

    def test_validate_name_field_valid(self):
        """Test name field validation with valid input"""
        from web_app.script import validateNameField
        
        valid_names = [
            'Иван',
            'John',
            'Мария-Анна',
            "O'Connor",
            'Jean-Pierre',
            'Анна Петровна'
        ]
        
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(validateNameField(name), f"Name '{name}' should be valid")

    def test_validate_name_field_invalid(self):
        """Test name field validation with invalid input"""
        from web_app.script import validateNameField
        
        invalid_names = [
            '',
            '   ',
            '123',
            'John123',
            'Иван@',
            'Test#Name',
            'Name$'
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validateNameField(name), f"Name '{name}' should be invalid")

    def test_validate_phone_field_valid(self):
        """Test phone field validation with valid input"""
        from web_app.script import validatePhoneField
        
        valid_phones = [
            '+375291234567',
            '375291234567',
            '+7 (495) 123-45-67',
            '8-800-555-35-35',
            '+1 555 123 4567',
            '1234567890'
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                self.assertTrue(validatePhoneField(phone), f"Phone '{phone}' should be valid")

    def test_validate_phone_field_invalid(self):
        """Test phone field validation with invalid input"""
        from web_app.script import validatePhoneField
        
        invalid_phones = [
            '',
            '   ',
            'abc',
            '123',
            '123456',
            '+123456789012345678901',  # Too long
            'phone@email.com'
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                self.assertFalse(validatePhoneField(phone), f"Phone '{phone}' should be invalid")

    def test_validate_email_field_valid(self):
        """Test email field validation with valid input"""
        from web_app.script import validateEmailField
        
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org',
            '123@numbers.com',
            'user@subdomain.example.com'
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(validateEmailField(email), f"Email '{email}' should be valid")

    def test_validate_email_field_invalid(self):
        """Test email field validation with invalid input"""
        from web_app.script import validateEmailField
        
        invalid_emails = [
            '',
            '   ',
            'invalid-email',
            '@example.com',
            'user@',
            'user@.com',
            'user..name@example.com',
            'user name@example.com'
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(validateEmailField(email), f"Email '{email}' should be invalid")

    def test_validate_delivery_date_field_valid(self):
        """Test delivery date field validation with valid input"""
        from web_app.script import validateDeliveryDateField
        
        # Mock today and tomorrow dates
        with patch('web_app.script.Date') as mock_date:
            # Mock today as 2024-01-15
            mock_today = Mock()
            mock_today.getDate.return_value = 15
            mock_today.getMonth.return_value = 0  # January
            mock_today.getFullYear.return_value = 2024
            
            mock_date.now.return_value = mock_today
            
            valid_dates = [
                '15.01.2024',  # Today
                '16.01.2024'   # Tomorrow
            ]
            
            for date in valid_dates:
                with self.subTest(date=date):
                    self.assertTrue(validateDeliveryDateField(date), f"Date '{date}' should be valid")

    def test_validate_delivery_date_field_invalid(self):
        """Test delivery date field validation with invalid input"""
        from web_app.script import validateDeliveryDateField
        
        invalid_dates = [
            '',
            '   ',
            'Выберите дату',
            'invalid-date',
            '15/01/2024',
            '2024-01-15',
            '15.01.24',
            '15.13.2024',  # Invalid month
            '32.01.2024',  # Invalid day
            '14.01.2024',  # Yesterday
            '17.01.2024'   # Day after tomorrow
        ]
        
        for date in invalid_dates:
            with self.subTest(date=date):
                self.assertFalse(validateDeliveryDateField(date), f"Date '{date}' should be invalid")

    def test_validate_delivery_method_field(self):
        """Test delivery method field validation"""
        from web_app.script import validateDeliveryMethodField
        
        valid_methods = ['courier', 'pickup']
        invalid_methods = ['', '   ', 'delivery', 'pickup_address', 'self_pickup']
        
        for method in valid_methods:
            with self.subTest(method=method):
                self.assertTrue(validateDeliveryMethodField(method), f"Method '{method}' should be valid")
        
        for method in invalid_methods:
            with self.subTest(method=method):
                self.assertFalse(validateDeliveryMethodField(method), f"Method '{method}' should be invalid")

    def test_validate_city_field(self):
        """Test city field validation"""
        from web_app.script import validateCityField
        
        valid_cities = [
            'Минск',
            'Moscow',
            'New York',
            'Санкт-Петербург',
            'London-UK',
            'Paris'
        ]
        
        invalid_cities = [
            '',
            '   ',
            'City123',
            'City@',
            'City#',
            '123City'
        ]
        
        for city in valid_cities:
            with self.subTest(city=city):
                self.assertTrue(validateCityField(city), f"City '{city}' should be valid")
        
        for city in invalid_cities:
            with self.subTest(city=city):
                self.assertFalse(validateCityField(city), f"City '{city}' should be invalid")

    def test_validate_address_field(self):
        """Test address field validation"""
        from web_app.script import validateAddressField
        
        valid_addresses = [
            'ул. Ленина, 15',
            '123 Main St.',
            'пр. Независимости, 25, кв. 10',
            'Building #5, Floor 3',
            'ул. Советская, д. 10, оф. 15'
        ]
        
        invalid_addresses = [
            '',
            '   ',
            'Address@',
            'Address#',
            'Address$',
            'Address%'
        ]
        
        for address in valid_addresses:
            with self.subTest(address=address):
                self.assertTrue(validateAddressField(address), f"Address '{address}' should be valid")
        
        for address in invalid_addresses:
            with self.subTest(address=address):
                self.assertFalse(validateAddressField(address), f"Address '{address}' should be invalid")

    def test_validate_pickup_address_field(self):
        """Test pickup address field validation"""
        from web_app.script import validatePickupAddressField
        
        valid_addresses = ['1', '2', '3', 'pickup_address']
        invalid_addresses = ['', '   ', None]
        
        for address in valid_addresses:
            with self.subTest(address=address):
                self.assertTrue(validatePickupAddressField(address), f"Pickup address '{address}' should be valid")
        
        for address in invalid_addresses:
            with self.subTest(address=address):
                self.assertFalse(validatePickupAddressField(address), f"Pickup address '{address}' should be invalid")

    def test_validate_payment_method_field(self):
        """Test payment method field validation"""
        from web_app.script import validatePaymentMethodField
        
        valid_methods = ['cash', 'card', 'erip', 'payment_method']
        invalid_methods = ['', '   ', None]
        
        for method in valid_methods:
            with self.subTest(method=method):
                self.assertTrue(validatePaymentMethodField(method), f"Payment method '{method}' should be valid")
        
        for method in invalid_methods:
            with self.subTest(method=method):
                self.assertFalse(validatePaymentMethodField(method), f"Payment method '{method}' should be invalid")

    def test_validation_order_courier_delivery(self):
        """Test validation order for courier delivery method"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            order_details = {
                'lastName': '',
                'firstName': '',
                'middleName': '',
                'phoneNumber': '',
                'email': '',
                'deliveryDate': '',
                'deliveryMethod': 'courier',
                'city': '',
                'addressLine': '',
                'paymentMethod': ''
            }
            
            result = validateOrderForm(order_details)
            
            # Should fail validation
            self.assertFalse(result['isValid'])
            
            # Check validation order - should validate all required fields for courier
            expected_fields = [
                'lastName', 'firstName', 'middleName', 'phoneNumber', 'email',
                'deliveryDate', 'deliveryMethod', 'city', 'addressLine', 'paymentMethod'
            ]
            
            actual_fields = [field['field'] for field in result['errorFields']]
            self.assertEqual(actual_fields, expected_fields)

    def test_validation_order_pickup_delivery(self):
        """Test validation order for pickup delivery method"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            order_details = {
                'lastName': '',
                'firstName': '',
                'middleName': '',
                'phoneNumber': '',
                'email': '',
                'deliveryDate': '',
                'deliveryMethod': 'pickup',
                'pickupAddress': '',
                'paymentMethodPickup': ''
            }
            
            result = validateOrderForm(order_details)
            
            # Should fail validation
            self.assertFalse(result['isValid'])
            
            # Check validation order - should validate pickup-specific fields
            expected_fields = [
                'lastName', 'firstName', 'middleName', 'phoneNumber', 'email',
                'deliveryDate', 'deliveryMethod', 'pickupAddress', 'paymentMethodPickup'
            ]
            
            actual_fields = [field['field'] for field in result['errorFields']]
            self.assertEqual(actual_fields, expected_fields)

    def test_validation_condition_courier_fields(self):
        """Test that courier-specific fields are only validated when delivery method is courier"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            # Test with pickup delivery method
            order_details = {
                'lastName': 'Test',
                'firstName': 'User',
                'middleName': 'Middle',
                'phoneNumber': '+375291234567',
                'email': 'test@example.com',
                'deliveryDate': '15.01.2024',
                'deliveryMethod': 'pickup',
                'city': '',  # Should be skipped
                'addressLine': '',  # Should be skipped
                'paymentMethod': '',  # Should be skipped
                'pickupAddress': '1',
                'paymentMethodPickup': 'erip'
            }
            
            result = validateOrderForm(order_details)
            
            # Should pass validation
            self.assertTrue(result['isValid'])
            
            # Check that courier-specific fields were not validated
            validated_fields = [field['field'] for field in result['errorFields']]
            self.assertNotIn('city', validated_fields)
            self.assertNotIn('addressLine', validated_fields)
            self.assertNotIn('paymentMethod', validated_fields)

    def test_validation_condition_pickup_fields(self):
        """Test that pickup-specific fields are only validated when delivery method is pickup"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            # Test with courier delivery method
            order_details = {
                'lastName': 'Test',
                'firstName': 'User',
                'middleName': 'Middle',
                'phoneNumber': '+375291234567',
                'email': 'test@example.com',
                'deliveryDate': '15.01.2024',
                'deliveryMethod': 'courier',
                'city': 'Minsk',
                'addressLine': 'Test Address 123',
                'paymentMethod': 'cash',
                'pickupAddress': '',  # Should be skipped
                'paymentMethodPickup': ''  # Should be skipped
            }
            
            result = validateOrderForm(order_details)
            
            # Should pass validation
            self.assertTrue(result['isValid'])
            
            # Check that pickup-specific fields were not validated
            validated_fields = [field['field'] for field in result['errorFields']]
            self.assertNotIn('pickupAddress', validated_fields)
            self.assertNotIn('paymentMethodPickup', validated_fields)

    def test_radio_group_validation_handling(self):
        """Test that radio group validation handles elementType and errorElement correctly"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: (
                self.mock_dom_elements.get(id) or 
                self.mock_error_elements.get(id) or 
                self.mock_containers.get(id)
            )
            
            order_details = {
                'lastName': 'Test',
                'firstName': 'User',
                'middleName': 'Middle',
                'phoneNumber': '+375291234567',
                'email': 'test@example.com',
                'deliveryDate': '15.01.2024',
                'deliveryMethod': '',  # Empty - should fail
                'city': 'Minsk',
                'addressLine': 'Test Address 123',
                'paymentMethod': 'cash'
            }
            
            result = validateOrderForm(order_details)
            
            # Should fail validation due to empty delivery method
            self.assertFalse(result['isValid'])
            
            # Check that delivery method error field has correct properties
            delivery_method_error = next(f for f in result['errorFields'] if f['field'] == 'deliveryMethod')
            self.assertEqual(delivery_method_error['elementType'], 'radio')
            self.assertIsNotNone(delivery_method_error['element'])

    def test_error_message_formatting(self):
        """Test that error messages are formatted correctly"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            order_details = {
                'lastName': '',
                'firstName': '',
                'middleName': '',
                'phoneNumber': '',
                'email': '',
                'deliveryDate': '',
                'deliveryMethod': 'courier',
                'city': '',
                'addressLine': '',
                'paymentMethod': ''
            }
            
            result = validateOrderForm(order_details)
            
            # Check error message format
            expected_messages = [
                'Пожалуйста, введите фамилию.',
                'Пожалуйста, введите имя.',
                'Пожалуйста, введите отчество.',
                'Пожалуйста, введите номер телефона.',
                'Пожалуйста, введите Email.',
                'Пожалуйста, введите дату доставки/самовывоза.',
                'Пожалуйста, введите способ получения.',
                'Пожалуйста, введите город для доставки.',
                'Пожалуйста, введите адрес доставки.',
                'Пожалуйста, введите способ оплаты.'
            ]
            
            self.assertEqual(result['errors'], expected_messages)

    def test_validation_with_partial_data(self):
        """Test validation with some fields filled and others empty"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            order_details = {
                'lastName': 'Test',
                'firstName': '',  # Empty
                'middleName': 'Middle',
                'phoneNumber': '+375291234567',
                'email': '',  # Empty
                'deliveryDate': '15.01.2024',
                'deliveryMethod': 'courier',
                'city': 'Minsk',
                'addressLine': '',  # Empty
                'paymentMethod': 'cash'
            }
            
            result = validateOrderForm(order_details)
            
            # Should fail validation
            self.assertFalse(result['isValid'])
            
            # Check that only empty fields are in error list
            expected_error_fields = ['firstName', 'email', 'addressLine']
            actual_error_fields = [field['field'] for field in result['errorFields']]
            self.assertEqual(actual_error_fields, expected_error_fields)

    def test_validation_with_all_valid_data(self):
        """Test validation with all required fields properly filled"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            order_details = {
                'lastName': 'Test',
                'firstName': 'User',
                'middleName': 'Middle',
                'phoneNumber': '+375291234567',
                'email': 'test@example.com',
                'deliveryDate': '15.01.2024',
                'deliveryMethod': 'courier',
                'city': 'Minsk',
                'addressLine': 'Test Address 123',
                'paymentMethod': 'cash'
            }
            
            result = validateOrderForm(order_details)
            
            # Should pass validation
            self.assertTrue(result['isValid'])
            self.assertEqual(len(result['errors']), 0)
            self.assertEqual(len(result['errorFields']), 0)

    def test_validation_with_pickup_all_valid_data(self):
        """Test validation with pickup delivery method and all required fields filled"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            order_details = {
                'lastName': 'Test',
                'firstName': 'User',
                'middleName': 'Middle',
                'phoneNumber': '+375291234567',
                'email': 'test@example.com',
                'deliveryDate': '15.01.2024',
                'deliveryMethod': 'pickup',
                'pickupAddress': '1',
                'paymentMethodPickup': 'erip'
            }
            
            result = validateOrderForm(order_details)
            
            # Should pass validation
            self.assertTrue(result['isValid'])
            self.assertEqual(len(result['errors']), 0)
            self.assertEqual(len(result['errorFields']), 0)

    def test_validation_field_priority_order(self):
        """Test that validation follows the correct priority order"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            order_details = {
                'lastName': '',
                'firstName': '',
                'middleName': '',
                'phoneNumber': '',
                'email': '',
                'deliveryDate': '',
                'deliveryMethod': 'courier',
                'city': '',
                'addressLine': '',
                'paymentMethod': ''
            }
            
            result = validateOrderForm(order_details)
            
            # Check that error fields are in the correct order
            expected_order = [
                'lastName', 'firstName', 'middleName', 'phoneNumber', 'email',
                'deliveryDate', 'deliveryMethod', 'city', 'addressLine', 'paymentMethod'
            ]
            
            actual_order = [field['field'] for field in result['errorFields']]
            self.assertEqual(actual_order, expected_order)

    def test_validation_with_whitespace_only(self):
        """Test validation with fields containing only whitespace"""
        from web_app.script import validateOrderForm
        
        # Mock DOM elements
        with patch('web_app.script.document') as mock_doc:
            mock_doc.getElementById.side_effect = lambda id: self.mock_dom_elements.get(id)
            
            order_details = {
                'lastName': '   ',
                'firstName': '  ',
                'middleName': ' ',
                'phoneNumber': '   ',
                'email': '  ',
                'deliveryDate': '   ',
                'deliveryMethod': 'courier',
                'city': '  ',
                'addressLine': ' ',
                'paymentMethod': '   '
            }
            
            result = validateOrderForm(order_details)
            
            # Should fail validation - whitespace-only values are considered empty
            self.assertFalse(result['isValid'])
            
            # All fields should be in error list
            expected_error_fields = [
                'lastName', 'firstName', 'middleName', 'phoneNumber', 'email',
                'deliveryDate', 'deliveryMethod', 'city', 'addressLine', 'paymentMethod'
            ]
            
            actual_error_fields = [field['field'] for field in result['errorFields']]
            self.assertEqual(actual_error_fields, expected_error_fields)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCheckoutValidation)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    print(f"{'='*60}")
    
    # Exit with appropriate code
    sys.exit(len(result.failures) + len(result.errors))
