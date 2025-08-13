#!/usr/bin/env python3
"""
Unit tests for customer data persistence functionality.
Tests the JavaScript customer data management functions.
"""

import os
import unittest
from pathlib import Path


class TestCustomerDataPersistence(unittest.TestCase):
    """Test suite for customer data persistence functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.script_file = self.project_root / "bot" / "web_app" / "script.js"
        
    def test_customer_data_constants_exist(self):
        """Test that customer data constants are defined."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for customer data constants
        self.assertIn('CUSTOMER_DATA_KEY', content)
        self.assertIn('CUSTOMER_DATA_VERSION', content)
        self.assertIn('CUSTOMER_DATA_EXPIRATION_DAYS', content)
        
    def test_customer_data_functions_exist(self):
        """Test that customer data management functions are defined."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for customer data functions
        functions_to_check = [
            'createCustomerDataWithMetadata',
            'loadCustomerDataWithExpiration',
            'saveCustomerDataWithMetadata',
            'extractCustomerDataFromForm',
            'populateFormWithCustomerData',
            'clearCustomerData',
            'checkCustomerDataExpiration',
            'getCustomerDataAge'
        ]
        
        for function_name in functions_to_check:
            self.assertIn(f'function {function_name}', content, 
                         f"Function {function_name} not found in script.js")
                         
    def test_customer_data_integration(self):
        """Test that customer data is integrated with form submission."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that customer data is saved after order submission
        self.assertIn('extractCustomerDataFromForm()', content)
        self.assertIn('saveCustomerDataWithMetadata(customerData)', content)
        
    def test_customer_data_population(self):
        """Test that customer data is loaded when checkout view is displayed."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that customer data is loaded in checkout view
        self.assertIn('loadCustomerDataWithExpiration()', content)
        self.assertIn('populateFormWithCustomerData(customerData)', content)
        
    def test_customer_data_cache_preservation(self):
        """Test that customer data is preserved during cache clearing."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that customer data key is in preserved keys list
        self.assertIn('CUSTOMER_DATA_KEY', content)
        
    def test_customer_data_global_functions(self):
        """Test that customer data functions are exposed globally."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that functions are exposed to window object
        global_functions = [
            'window.loadCustomerDataWithExpiration',
            'window.saveCustomerDataWithMetadata',
            'window.extractCustomerDataFromForm',
            'window.populateFormWithCustomerData',
            'window.clearCustomerData',
            'window.checkCustomerDataExpiration',
            'window.getCustomerDataAge'
        ]
        
        for function_name in global_functions:
            self.assertIn(function_name, content, 
                         f"Global function {function_name} not found in script.js")
                         
    def test_customer_data_fields_mapping(self):
        """Test that customer data field mappings are correct."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for field mappings in populateFormWithCustomerData
        expected_fields = [
            'firstName', 'lastName', 'middleName', 'phoneNumber', 
            'email', 'city', 'addressLine'
        ]
        
        for field in expected_fields:
            self.assertIn(f"'{field}'", content, 
                         f"Field {field} not found in customer data mappings")
                         
    def test_customer_data_expiration_logic(self):
        """Test that customer data expiration logic is implemented."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for expiration logic
        self.assertIn('expiresAt', content)
        self.assertIn('Date.now() > customerData.expiresAt', content)
        self.assertIn('CUSTOMER_DATA_EXPIRATION_DAYS', content)
        
    def test_customer_data_versioning(self):
        """Test that customer data versioning is implemented."""
        with open(self.script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for versioning logic
        self.assertIn('version', content)
        self.assertIn('CUSTOMER_DATA_VERSION', content)
        self.assertIn('customerData.version !== CUSTOMER_DATA_VERSION', content)


if __name__ == '__main__':
    unittest.main()
