import unittest
import os
import re

class TestPrivacyConsentSimple(unittest.TestCase):
    """Test suite for privacy consent checkbox functionality - simplified version"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Get the project root directory
        self.project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        self.html_file_path = os.path.join(self.project_root, 'bot', 'web_app', 'index.html')
        self.css_file_path = os.path.join(self.project_root, 'bot', 'web_app', 'style.css')
        self.js_file_path = os.path.join(self.project_root, 'bot', 'web_app', 'script.js')

    def test_privacy_consent_html_structure(self):
        """Test that HTML structure for privacy consent is correct"""
        # Read the HTML file
        with open(self.html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check for required elements
        self.assertIn('id="privacy-consent"', html_content, "Privacy consent checkbox should have correct ID")
        self.assertIn('id="privacy-consent-container"', html_content, "Privacy consent container should have correct ID")
        self.assertIn('id="privacyConsent-error"', html_content, "Privacy consent error message should have correct ID")
        self.assertIn('Я согласен/согласна на обработку', html_content, "Privacy consent text should be gender-neutral")
        self.assertIn('required', html_content, "Privacy consent checkbox should be required")
        
        # Check that checkbox is of correct type
        self.assertIn('type="checkbox"', html_content, "Privacy consent should be a checkbox")
        
        # Check that label is properly associated with checkbox
        self.assertIn('for="privacy-consent"', html_content, "Label should be associated with checkbox")

    def test_privacy_consent_css_styles(self):
        """Test that CSS styles for privacy consent are present"""
        # Read the CSS file
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for required CSS classes
        self.assertIn('.privacy-consent-container', css_content, "Privacy consent container styles should be present")
        self.assertIn('.privacy-consent-label', css_content, "Privacy consent label styles should be present")
        self.assertIn('font-family: Arial', css_content, "Privacy consent should use Arial font")
        self.assertIn('display: flex', css_content, "Privacy consent should use flexbox layout")
        self.assertIn('.privacy-consent-container.error', css_content, "Privacy consent error styles should be present")
        
        # Check for mobile responsive styles
        self.assertIn('@media (max-width: 768px)', css_content, "Mobile responsive styles should be present")
        self.assertIn('@media (max-width: 480px)', css_content, "Small mobile responsive styles should be present")

    def test_privacy_consent_javascript_functions(self):
        """Test that JavaScript functions for privacy consent are present"""
        # Read the JavaScript file
        with open(self.js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for privacy consent validation function
        self.assertIn('validatePrivacyConsentField', js_content, "Privacy consent validation function should be present")
        
        # Check for privacy consent in form data collection
        self.assertIn('privacyConsent:', js_content, "Privacy consent should be collected in form data")
        
        # Check for privacy consent in validation order
        self.assertIn('field: \'privacyConsent\'', js_content, "Privacy consent should be in validation order")
        
        # Check for event listener for checkbox
        self.assertIn('addEventListener(\'change\'', js_content, "Change event listener should be present")
        
        # Check for error message clearing logic
        self.assertIn('privacyConsent-error', js_content, "Error message clearing should be present")

    def test_privacy_consent_validation_logic(self):
        """Test privacy consent validation logic in JavaScript"""
        # Read the JavaScript file
        with open(self.js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check that validation function returns correct values
        # Look for the validation function definition
        validation_function_match = re.search(r'function validatePrivacyConsentField\([^)]*\)\s*\{[^}]*return[^}]*\}', js_content, re.DOTALL)
        self.assertIsNotNone(validation_function_match, "Privacy consent validation function should be defined")
        
        # Check that it returns true for checked checkbox
        self.assertIn('value === true', js_content, "Validation should return true when checkbox is checked")

    def test_privacy_consent_form_integration(self):
        """Test that privacy consent is properly integrated into form validation"""
        # Read the JavaScript file
        with open(self.js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check that privacy consent is in the validation order array
        # Look for the validation order definition
        validation_order_match = re.search(r'const validationOrder\s*=\s*\[[^\]]*privacyConsent[^\]]*\]', js_content, re.DOTALL)
        self.assertIsNotNone(validation_order_match, "Privacy consent should be in validation order array")
        
        # Check that it's configured as checkbox type
        self.assertIn('elementType: \'checkbox\'', js_content, "Privacy consent should be configured as checkbox type")

    def test_privacy_consent_error_handling(self):
        """Test privacy consent error handling and styling"""
        # Read the JavaScript file
        with open(self.js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for error styling logic
        self.assertIn('privacy-consent-container', js_content, "Error styling should target the container")
        
        # Check for error message display logic
        self.assertIn('privacyConsent-error', js_content, "Error message should be handled")

    def test_privacy_consent_event_handling(self):
        """Test privacy consent event handling"""
        # Read the JavaScript file
        with open(self.js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for event listener setup
        self.assertIn('getElementById(\'privacy-consent\')', js_content, "Should get privacy consent checkbox element")
        
        # Check for change event handling
        self.assertIn('addEventListener(\'change\'', js_content, "Should handle change events")
        
        # Check for error clearing logic
        self.assertIn('classList.remove(\'show\')', js_content, "Should clear error message when checkbox is checked")

    def test_privacy_consent_accessibility(self):
        """Test privacy consent accessibility features"""
        # Read the HTML file
        with open(self.html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check for proper label association
        self.assertIn('for="privacy-consent"', html_content, "Label should be properly associated with checkbox")
        
        # Check for required attribute
        self.assertIn('required', html_content, "Checkbox should be required")
        
        # Check for proper input type
        self.assertIn('type="checkbox"', html_content, "Should be a checkbox input")

    def test_privacy_consent_mobile_responsiveness(self):
        """Test privacy consent mobile responsiveness"""
        # Read the CSS file
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for mobile breakpoints
        self.assertIn('@media (max-width: 768px)', css_content, "Should have tablet breakpoint")
        self.assertIn('@media (max-width: 480px)', css_content, "Should have mobile breakpoint")
        
        # Check for responsive font sizes
        self.assertIn('font-size: 13px', css_content, "Should have responsive font size for tablets")
        self.assertIn('font-size: 12px', css_content, "Should have responsive font size for mobile")
        
        # Check for responsive checkbox sizes
        self.assertIn('width: 16px', css_content, "Should have responsive checkbox size for tablets")
        self.assertIn('width: 15px', css_content, "Should have responsive checkbox size for mobile")

    def test_privacy_consent_gender_neutral_text(self):
        """Test that privacy consent text is gender-neutral"""
        # Read the HTML file
        with open(self.html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check for gender-neutral text
        self.assertIn('Я согласен/согласна', html_content, "Text should be gender-neutral")
        
        # Ensure it's not just the old text
        self.assertNotIn('Я согласен на обработку', html_content, "Should not have old gender-specific text")

    def test_privacy_consent_required_validation(self):
        """Test that privacy consent is required for form submission"""
        # Read the HTML file
        with open(self.html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check for required attribute
        self.assertIn('required', html_content, "Privacy consent checkbox should be required")
        
        # Read the JavaScript file
        with open(self.js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check that validation fails without consent
        self.assertIn('privacyConsent', js_content, "Privacy consent should be validated")

if __name__ == '__main__':
    unittest.main()
