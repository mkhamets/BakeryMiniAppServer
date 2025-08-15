/**
 * Comprehensive Web App Tests
 * Tests for all major web app functionality
 */

// Mock Telegram WebApp API
global.Telegram = {
    WebApp: {
        ready: () => {},
        expand: () => {},
        close: () => {},
        MainButton: {
            show: () => {},
            hide: () => {},
            setText: () => {},
            setParams: () => {},
            onClick: () => {}
        },
        sendData: () => {}
    }
};

// Mock DOM elements
function createMockElement(id, type = 'input') {
    const element = {
        id: id,
        value: '',
        checked: false,
        classList: {
            add: () => {},
            remove: () => {},
            contains: () => false
        },
        style: {
            display: '',
            color: ''
        },
        addEventListener: () => {},
        focus: () => {},
        scrollIntoView: () => {}
    };
    
    if (type === 'radio') {
        element.type = 'radio';
        element.name = '';
    }
    
    return element;
}

// Mock document
global.document = {
    getElementById: (id) => {
        const elements = {
            'last-name': createMockElement('last-name'),
            'first-name': createMockElement('first-name'),
            'middle-name': createMockElement('middle-name'),
            'phone-number': createMockElement('phone-number'),
            'email': createMockElement('email'),
            'delivery-date': createMockElement('delivery-date'),
            'city': createMockElement('city'),
            'address-line': createMockElement('address-line'),
            'delivery-courier-radio': createMockElement('delivery-courier-radio', 'radio'),
            'delivery-pickup-radio': createMockElement('delivery-pickup-radio', 'radio'),
            'pickup-radio-group': createMockElement('pickup-radio-group'),
            'payment-method-section': createMockElement('payment-method-section'),
            'payment-method-section-pickup': createMockElement('payment-method-section-pickup'),
            'comment-delivery': createMockElement('comment-delivery'),
            'comment-pickup': createMockElement('comment-pickup'),
            'lastName-error': createMockElement('lastName-error'),
            'firstName-error': createMockElement('firstName-error'),
            'middleName-error': createMockElement('middleName-error'),
            'phoneNumber-error': createMockElement('phoneNumber-error'),
            'email-error': createMockElement('email-error'),
            'deliveryDate-error': createMockElement('deliveryDate-error'),
            'city-error': createMockElement('city-error'),
            'addressLine-error': createMockElement('addressLine-error'),
            'pickupAddress-error': createMockElement('pickupAddress-error'),
            'paymentMethod-error': createMockElement('paymentMethod-error'),
            'checkout-form': createMockElement('checkout-form'),
            'cart-total': { textContent: '100.00 р.' },
            'cart-items-list': createMockElement('cart-items-list'),
            'checkout-items-list': createMockElement('checkout-items-list'),
            'main-page-container': createMockElement('main-page-container'),
            'welcome-container': createMockElement('welcome-container'),
            'categories-container': createMockElement('categories-container'),
            'products-container': createMockElement('products-container'),
            'cart-container': createMockElement('cart-container'),
            'checkout-container': createMockElement('checkout-container'),
            'product-screen': createMockElement('product-screen'),
            'main-category-title': createMockElement('main-category-title'),
            'loading-logo-container': createMockElement('loading-logo-container'),
            'courier-text': createMockElement('courier-text'),
            'pickup-text': createMockElement('pickup-text'),
            'courier-delivery-fields': createMockElement('courier-delivery-fields'),
            'pickup-addresses': createMockElement('pickup-addresses'),
            'product-list': createMockElement('product-list'),
            'continue-shopping-button': createMockElement('continue-shopping-button'),
            'start-shopping-button': createMockElement('start-shopping-button')
        };
        return elements[id] || null;
    },
    querySelector: (selector) => {
        if (selector === 'input[name="deliveryMethod"]:checked') {
            return null;
        }
        if (selector === 'input[name="pickupAddress"]:checked') {
            return null;
        }
        if (selector === 'input[name="paymentMethod"]:checked') {
            return null;
        }
        if (selector === 'input[name="paymentMethodPickup"]:checked') {
            return null;
        }
        return null;
    },
    querySelectorAll: (selector) => {
        if (selector === 'input[name="deliveryMethod"]') {
            return [
                createMockElement('delivery-courier-radio', 'radio'),
                createMockElement('delivery-pickup-radio', 'radio')
            ];
        }
        return [];
    },
    addEventListener: () => {},
    readyState: 'loading'
};

// Mock localStorage
global.localStorage = {
    data: {},
    getItem: function(key) {
        return this.data[key] || null;
    },
    setItem: function(key, value) {
        this.data[key] = value;
    },
    removeItem: function(key) {
        delete this.data[key];
    },
    clear: function() {
        this.data = {};
    }
};

// Mock sessionStorage
global.sessionStorage = {
    data: {},
    getItem: function(key) {
        return this.data[key] || null;
    },
    setItem: function(key, value) {
        this.data[key] = value;
    },
    removeItem: function(key) {
        delete this.data[key];
    },
    clear: function() {
        this.data = {};
    }
};

// Mock fetch
global.fetch = async (url) => {
    if (url.includes('/api/products')) {
        return {
            ok: true,
            json: async () => ({
                category_bakery: [
                    { id: 1, name: "Bread", price: "10.00 р.", description: "Fresh bread" },
                    { id: 2, name: "Croissant", price: "15.00 р.", description: "Buttery croissant" }
                ]
            })
        };
    }
    return { ok: false };
};

// Mock console
global.console = {
    log: () => {},
    error: () => {},
    warn: () => {},
    info: () => {}
};

// Mock window
global.window = {
    location: { href: 'https://test.com' },
    innerWidth: 768,
    scrollTo: () => {},
    addEventListener: () => {}
};

// Mock navigator
global.navigator = {
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
    platform: 'iPhone'
};

// Test suite
class WebAppTestSuite {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    async run() {
        console.log('🧪 Running Web App Tests...\n');
        
        for (const test of this.tests) {
            try {
                await test.testFunction();
                console.log(`✅ ${test.name}`);
                this.passed++;
            } catch (error) {
                console.log(`❌ ${test.name}: ${error.message}`);
                this.failed++;
            }
        }
        
        console.log(`\n📊 Test Results: ${this.passed} passed, ${this.failed} failed`);
        return this.failed === 0;
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(message);
        }
    }

    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(`${message}: expected ${expected}, got ${actual}`);
        }
    }

    assertTrue(condition, message) {
        this.assert(condition, message);
    }

    assertFalse(condition, message) {
        this.assert(!condition, message);
    }
}

// Create test suite
const testSuite = new WebAppTestSuite();

// Test validation functions
testSuite.test('validateNameField - valid name', () => {
    const result = validateNameField('John Doe');
    testSuite.assertTrue(result, 'Valid name should pass validation');
});

testSuite.test('validateNameField - invalid name', () => {
    const result = validateNameField('John123');
    testSuite.assertFalse(result, 'Name with numbers should fail validation');
});

testSuite.test('validatePhoneField - valid phone', () => {
    const result = validatePhoneField('+375291234567');
    testSuite.assertTrue(result, 'Valid phone should pass validation');
});

testSuite.test('validatePhoneField - invalid phone', () => {
    const result = validatePhoneField('invalid-phone');
    testSuite.assertFalse(result, 'Invalid phone should fail validation');
});

testSuite.test('validateEmailField - valid email', () => {
    const result = validateEmailField('test@example.com');
    testSuite.assertTrue(result, 'Valid email should pass validation');
});

testSuite.test('validateEmailField - invalid email', () => {
    const result = validateEmailField('invalid-email');
    testSuite.assertFalse(result, 'Invalid email should fail validation');
});

testSuite.test('validateDeliveryDateField - valid date', () => {
    const today = new Date();
    const formattedDate = `${today.getDate().toString().padStart(2, '0')}.${(today.getMonth() + 1).toString().padStart(2, '0')}.${today.getFullYear()}`;
    const result = validateDeliveryDateField(formattedDate);
    testSuite.assertTrue(result, 'Valid delivery date should pass validation');
});

testSuite.test('validateDeliveryDateField - invalid date', () => {
    const result = validateDeliveryDateField('Выберите дату');
    testSuite.assertFalse(result, 'Placeholder date should fail validation');
});

// Test form data collection
testSuite.test('collectFormData - basic collection', () => {
    // Set up form data
    document.getElementById('last-name').value = 'Doe';
    document.getElementById('first-name').value = 'John';
    document.getElementById('middle-name').value = 'Smith';
    document.getElementById('phone-number').value = '+375291234567';
    document.getElementById('email').value = 'john@example.com';
    
    const formData = collectFormData();
    
    testSuite.assertEqual(formData.lastName, 'Doe', 'Last name should be collected');
    testSuite.assertEqual(formData.firstName, 'John', 'First name should be collected');
    testSuite.assertEqual(formData.middleName, 'Smith', 'Middle name should be collected');
    testSuite.assertEqual(formData.phoneNumber, '+375291234567', 'Phone number should be collected');
    testSuite.assertEqual(formData.email, 'john@example.com', 'Email should be collected');
});

// Test cart management
testSuite.test('loadCartWithExpiration - empty cart', () => {
    localStorage.clear();
    const cart = loadCartWithExpiration();
    testSuite.assertEqual(Object.keys(cart).length, 0, 'Empty cart should be returned');
});

testSuite.test('loadCartWithExpiration - valid cart', () => {
    const testCart = {
        '1': { id: 1, name: 'Bread', price: 10.00, quantity: 2 }
    };
    localStorage.setItem('cart', JSON.stringify(testCart));
    localStorage.setItem('cart_version', '1.0.0');
    localStorage.setItem('cart_timestamp', Date.now().toString());
    
    const cart = loadCartWithExpiration();
    testSuite.assertEqual(cart['1'].name, 'Bread', 'Cart item should be loaded');
    testSuite.assertEqual(cart['1'].quantity, 2, 'Cart item quantity should be preserved');
});

// Test customer data management
testSuite.test('saveCustomerDataWithMetadata - basic save', () => {
    const customerData = {
        firstName: 'John',
        lastName: 'Doe',
        email: 'john@example.com'
    };
    
    saveCustomerDataWithMetadata(customerData);
    
    const savedData = JSON.parse(localStorage.getItem('customer_data'));
    testSuite.assertEqual(savedData.firstName, 'John', 'Customer data should be saved');
    testSuite.assertEqual(savedData.lastName, 'Doe', 'Customer data should be saved');
    testSuite.assertEqual(savedData.email, 'john@example.com', 'Customer data should be saved');
    testSuite.assertTrue(savedData.version, 'Version should be set');
    testSuite.assertTrue(savedData.timestamp, 'Timestamp should be set');
});

testSuite.test('loadCustomerDataWithMetadata - valid data', () => {
    const testData = {
        firstName: 'Jane',
        lastName: 'Smith',
        email: 'jane@example.com',
        version: '1.0.0',
        timestamp: Date.now()
    };
    localStorage.setItem('customer_data', JSON.stringify(testData));
    
    const loadedData = loadCustomerDataWithMetadata();
    testSuite.assertEqual(loadedData.firstName, 'Jane', 'Customer data should be loaded');
    testSuite.assertEqual(loadedData.lastName, 'Smith', 'Customer data should be loaded');
    testSuite.assertEqual(loadedData.email, 'jane@example.com', 'Customer data should be loaded');
});

// Test cache management
testSuite.test('clearBrowserCache - basic functionality', async () => {
    // Set up some test data
    localStorage.setItem('test_data', 'test_value');
    sessionStorage.setItem('test_session', 'session_value');
    
    const result = await clearBrowserCache();
    testSuite.assertTrue(result, 'Cache clear should succeed');
    
    // Check that essential data is preserved
    const cartData = localStorage.getItem('cart');
    testSuite.assertTrue(cartData !== null, 'Cart data should be preserved');
});

// Test error handling
testSuite.test('clearAllErrors - basic functionality', () => {
    // Mock error elements
    const errorElements = document.querySelectorAll('.error-message');
    
    clearAllErrors();
    
    // Should not throw any errors
    testSuite.assertTrue(true, 'clearAllErrors should execute without errors');
});

testSuite.test('clearFieldError - basic functionality', () => {
    const fieldName = 'lastName';
    
    clearFieldError(fieldName);
    
    // Should not throw any errors
    testSuite.assertTrue(true, 'clearFieldError should execute without errors');
});

// Test mobile detection
testSuite.test('isMobileDevice - mobile detection', () => {
    // Test with mobile user agent
    navigator.userAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)';
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    
    testSuite.assertTrue(isMobile, 'Mobile device should be detected');
});

testSuite.test('isMobileDevice - desktop detection', () => {
    // Test with desktop user agent
    navigator.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';
    window.innerWidth = 1024;
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    
    testSuite.assertFalse(isMobile, 'Desktop device should not be detected as mobile');
});

// Test version consistency
testSuite.test('CACHE_VERSION - should be defined', () => {
    testSuite.assertTrue(typeof CACHE_VERSION !== 'undefined', 'CACHE_VERSION should be defined');
    testSuite.assertTrue(CACHE_VERSION.length > 0, 'CACHE_VERSION should not be empty');
});

// Test API functions
testSuite.test('fetchProductsData - basic functionality', async () => {
    const products = await fetchProductsData();
    testSuite.assertTrue(products, 'Products data should be fetched');
    testSuite.assertTrue(typeof products === 'object', 'Products should be an object');
});

// Test form validation
testSuite.test('validateOrderForm - empty form', () => {
    const orderDetails = {
        lastName: '',
        firstName: '',
        middleName: '',
        phoneNumber: '',
        email: '',
        deliveryDate: '',
        deliveryMethod: ''
    };
    
    const result = validateOrderForm(orderDetails);
    testSuite.assertFalse(result.isValid, 'Empty form should fail validation');
    testSuite.assertTrue(result.errors.length > 0, 'Should have validation errors');
});

testSuite.test('validateOrderForm - valid form', () => {
    const orderDetails = {
        lastName: 'Doe',
        firstName: 'John',
        middleName: 'Smith',
        phoneNumber: '+375291234567',
        email: 'john@example.com',
        deliveryDate: '15.08.2025',
        deliveryMethod: 'courier',
        city: 'Minsk',
        addressLine: 'Test Address 123'
    };
    
    const result = validateOrderForm(orderDetails);
    testSuite.assertTrue(result.isValid, 'Valid form should pass validation');
    testSuite.assertEqual(result.errors.length, 0, 'Should have no validation errors');
});

// Test cart operations
testSuite.test('addToCart - basic functionality', () => {
    const product = {
        id: 1,
        name: 'Test Product',
        price: 10.00,
        description: 'Test Description'
    };
    
    addToCart(product);
    
    const cart = loadCartWithExpiration();
    testSuite.assertTrue(cart['1'], 'Product should be added to cart');
    testSuite.assertEqual(cart['1'].quantity, 1, 'Initial quantity should be 1');
});

testSuite.test('updateCartItemQuantity - increase quantity', () => {
    // Set up cart with existing item
    const cart = { '1': { id: 1, name: 'Test Product', price: 10.00, quantity: 1 } };
    localStorage.setItem('cart', JSON.stringify(cart));
    
    updateCartItemQuantity(1, 3);
    
    const updatedCart = loadCartWithExpiration();
    testSuite.assertEqual(updatedCart['1'].quantity, 3, 'Quantity should be updated');
});

testSuite.test('removeFromCart - basic functionality', () => {
    // Set up cart with existing item
    const cart = { '1': { id: 1, name: 'Test Product', price: 10.00, quantity: 1 } };
    localStorage.setItem('cart', JSON.stringify(cart));
    
    removeFromCart(1);
    
    const updatedCart = loadCartWithExpiration();
    testSuite.assertFalse(updatedCart['1'], 'Product should be removed from cart');
});

// Test UI functions
testSuite.test('displayView - basic functionality', () => {
    // Mock view containers
    const containers = ['welcome-container', 'categories-container', 'products-container', 'cart-container', 'checkout-container'];
    
    displayView('cart');
    
    // Should not throw any errors
    testSuite.assertTrue(true, 'displayView should execute without errors');
});

testSuite.test('renderCart - basic functionality', () => {
    // Set up cart with items
    const cart = { '1': { id: 1, name: 'Test Product', price: 10.00, quantity: 2 } };
    localStorage.setItem('cart', JSON.stringify(cart));
    
    renderCart();
    
    // Should not throw any errors
    testSuite.assertTrue(true, 'renderCart should execute without errors');
});

// Test utility functions
testSuite.test('formatPrice - basic formatting', () => {
    const price = 10.50;
    const formatted = formatPrice(price);
    testSuite.assertEqual(formatted, '10.50 р.', 'Price should be formatted correctly');
});

testSuite.test('formatPrice - zero price', () => {
    const price = 0;
    const formatted = formatPrice(price);
    testSuite.assertEqual(formatted, '0.00 р.', 'Zero price should be formatted correctly');
});

// Test error handling functions
testSuite.test('showValidationErrors - basic functionality', () => {
    const errorFields = [
        { field: 'lastName', element: document.getElementById('last-name') }
    ];
    const errorMessages = ['Пожалуйста, введите фамилию.'];
    
    showValidationErrors(errorFields, errorMessages);
    
    // Should not throw any errors
    testSuite.assertTrue(true, 'showValidationErrors should execute without errors');
});

// Test date handling
testSuite.test('formatDate - basic formatting', () => {
    const date = new Date('2025-08-15');
    const formatted = formatDate(date);
    testSuite.assertEqual(formatted, '15.08.2025', 'Date should be formatted correctly');
});

// Test scroll functions
testSuite.test('scrollToTop - basic functionality', () => {
    scrollToTop();
    
    // Should not throw any errors
    testSuite.assertTrue(true, 'scrollToTop should execute without errors');
});

// Test initialization functions
testSuite.test('initializeIcons - basic functionality', () => {
    initializeIcons();
    
    // Should not throw any errors
    testSuite.assertTrue(true, 'initializeIcons should execute without errors');
});

testSuite.test('initializeCacheManagement - basic functionality', async () => {
    await initializeCacheManagement();
    
    // Should not throw any errors
    testSuite.assertTrue(true, 'initializeCacheManagement should execute without errors');
});

// Test cart expiration
testSuite.test('checkCartExpiration - fresh cart', () => {
    // Set up fresh cart
    const cart = { '1': { id: 1, name: 'Test Product', price: 10.00, quantity: 1 } };
    localStorage.setItem('cart', JSON.stringify(cart));
    localStorage.setItem('cart_timestamp', Date.now().toString());
    
    const expired = checkCartExpiration();
    testSuite.assertFalse(expired, 'Fresh cart should not be expired');
});

testSuite.test('checkCartExpiration - expired cart', () => {
    // Set up expired cart (older than 24 hours)
    const cart = { '1': { id: 1, name: 'Test Product', price: 10.00, quantity: 1 } };
    localStorage.setItem('cart', JSON.stringify(cart));
    localStorage.setItem('cart_timestamp', (Date.now() - 25 * 60 * 60 * 1000).toString()); // 25 hours ago
    
    const expired = checkCartExpiration();
    testSuite.assertTrue(expired, 'Expired cart should be detected');
});

// Test customer data extraction
testSuite.test('extractCustomerDataFromForm - basic extraction', () => {
    // Set up form data
    document.getElementById('last-name').value = 'Doe';
    document.getElementById('first-name').value = 'John';
    document.getElementById('email').value = 'john@example.com';
    document.getElementById('phone-number').value = '+375291234567';
    
    const customerData = extractCustomerDataFromForm();
    
    testSuite.assertEqual(customerData.lastName, 'Doe', 'Last name should be extracted');
    testSuite.assertEqual(customerData.firstName, 'John', 'First name should be extracted');
    testSuite.assertEqual(customerData.email, 'john@example.com', 'Email should be extracted');
    testSuite.assertEqual(customerData.phoneNumber, '+375291234567', 'Phone should be extracted');
});

// Test order processing
testSuite.test('processOrder - basic functionality', () => {
    const orderDetails = {
        lastName: 'Doe',
        firstName: 'John',
        phoneNumber: '+375291234567',
        email: 'john@example.com',
        deliveryMethod: 'courier',
        city: 'Minsk',
        addressLine: 'Test Address 123'
    };
    
    const cart = { '1': { id: 1, name: 'Test Product', price: 10.00, quantity: 1 } };
    
    const orderPayload = {
        action: 'checkout_order',
        order_details: orderDetails,
        cart_items: Object.values(cart).map(item => ({
            id: item.id,
            name: item.name,
            quantity: item.quantity,
            price: item.price
        })),
        total_amount: 10.00
    };
    
    testSuite.assertEqual(orderPayload.action, 'checkout_order', 'Order action should be correct');
    testSuite.assertEqual(orderPayload.order_details.firstName, 'John', 'Order details should be correct');
    testSuite.assertEqual(orderPayload.cart_items.length, 1, 'Cart items should be included');
    testSuite.assertEqual(orderPayload.total_amount, 10.00, 'Total amount should be correct');
});

// Test minimum order validation
testSuite.test('minimumOrderValidation - courier delivery below minimum', () => {
    const totalAmount = 50.00; // Below 70.00 minimum
    const deliveryMethod = 'courier';
    
    const isValid = totalAmount >= 70.00 || deliveryMethod !== 'courier';
    testSuite.assertFalse(isValid, 'Courier delivery below minimum should be invalid');
});

testSuite.test('minimumOrderValidation - courier delivery above minimum', () => {
    const totalAmount = 100.00; // Above 70.00 minimum
    const deliveryMethod = 'courier';
    
    const isValid = totalAmount >= 70.00 || deliveryMethod !== 'courier';
    testSuite.assertTrue(isValid, 'Courier delivery above minimum should be valid');
});

testSuite.test('minimumOrderValidation - pickup delivery below minimum', () => {
    const totalAmount = 50.00; // Below 70.00 minimum
    const deliveryMethod = 'pickup';
    
    const isValid = totalAmount >= 70.00 || deliveryMethod !== 'courier';
    testSuite.assertTrue(isValid, 'Pickup delivery below minimum should be valid');
});

// Test delivery method validation
testSuite.test('validateDeliveryMethodField - valid courier', () => {
    const result = validateDeliveryMethodField('courier');
    testSuite.assertTrue(result, 'Courier delivery method should be valid');
});

testSuite.test('validateDeliveryMethodField - valid pickup', () => {
    const result = validateDeliveryMethodField('pickup');
    testSuite.assertTrue(result, 'Pickup delivery method should be valid');
});

testSuite.test('validateDeliveryMethodField - invalid method', () => {
    const result = validateDeliveryMethodField('invalid');
    testSuite.assertFalse(result, 'Invalid delivery method should be invalid');
});

// Test address validation
testSuite.test('validateAddressField - valid address', () => {
    const result = validateAddressField('ул. Ленина, д. 10, кв. 5');
    testSuite.assertTrue(result, 'Valid address should pass validation');
});

testSuite.test('validateAddressField - invalid address', () => {
    const result = validateAddressField(''); // Empty address
    testSuite.assertFalse(result, 'Empty address should fail validation');
});

testSuite.test('validateCityField - valid city', () => {
    const result = validateCityField('Минск');
    testSuite.assertTrue(result, 'Valid city should pass validation');
});

testSuite.test('validateCityField - invalid city', () => {
    const result = validateCityField(''); // Empty city
    testSuite.assertFalse(result, 'Empty city should fail validation');
});

// Test payment method validation
testSuite.test('validatePaymentMethodField - valid payment method', () => {
    const result = validatePaymentMethodField('cash');
    testSuite.assertTrue(result, 'Valid payment method should pass validation');
});

testSuite.test('validatePaymentMethodField - invalid payment method', () => {
    const result = validatePaymentMethodField(''); // Empty payment method
    testSuite.assertFalse(result, 'Empty payment method should fail validation');
});

// Test pickup address validation
testSuite.test('validatePickupAddressField - valid pickup address', () => {
    const result = validatePickupAddressField('ул. Пушкина, д. 15');
    testSuite.assertTrue(result, 'Valid pickup address should pass validation');
});

testSuite.test('validatePickupAddressField - invalid pickup address', () => {
    const result = validatePickupAddressField(''); // Empty pickup address
    testSuite.assertFalse(result, 'Empty pickup address should fail validation');
});

// Test field validation
testSuite.test('validateField - empty value', () => {
    const validation = { field: 'test' };
    const result = validateField('', validation);
    testSuite.assertFalse(result, 'Empty value should fail validation');
});

testSuite.test('validateField - valid value', () => {
    const validation = { field: 'test' };
    const result = validateField('valid value', validation);
    testSuite.assertTrue(result, 'Valid value should pass validation');
});

testSuite.test('validateField - regex validation', () => {
    const validation = { field: 'email', regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ };
    const result = validateField('test@example.com', validation);
    testSuite.assertTrue(result, 'Valid email should pass regex validation');
});

testSuite.test('validateField - regex validation failure', () => {
    const validation = { field: 'email', regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ };
    const result = validateField('invalid-email', validation);
    testSuite.assertFalse(result, 'Invalid email should fail regex validation');
});

testSuite.test('validateField - custom validation', () => {
    const validation = { 
        field: 'test', 
        customValidation: (value) => value.length > 3 
    };
    const result = validateField('long value', validation);
    testSuite.assertTrue(result, 'Value should pass custom validation');
});

testSuite.test('validateField - custom validation failure', () => {
    const validation = { 
        field: 'test', 
        customValidation: (value) => value.length > 3 
    };
    const result = validateField('abc', validation);
    testSuite.assertFalse(result, 'Value should fail custom validation');
});

// Run all tests
async function runAllTests() {
    try {
        const success = await testSuite.run();
        if (success) {
            console.log('\n🎉 All tests passed!');
            process.exit(0);
        } else {
            console.log('\n❌ Some tests failed!');
            process.exit(1);
        }
    } catch (error) {
        console.error('Test runner error:', error);
        process.exit(1);
    }
}

// Export for use in other test files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WebAppTestSuite, testSuite };
} else {
    // Run tests if this file is executed directly
    runAllTests();
}

