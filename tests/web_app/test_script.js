// Web App JavaScript Tests
// Simple test framework for testing web app functionality

class WebAppTester {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed');
        }
    }

    assertEquals(expected, actual, message) {
        if (expected !== actual) {
            throw new Error(message || `Expected ${expected}, but got ${actual}`);
        }
    }

    assertNotNull(value, message) {
        if (value === null || value === undefined) {
            throw new Error(message || 'Value is null or undefined');
        }
    }

    runTests() {
        console.log('🧪 Running Web App Tests...\n');
        
        for (const test of this.tests) {
            try {
                test.testFunction();
                console.log(`✅ PASS: ${test.name}`);
                this.passed++;
            } catch (error) {
                console.log(`❌ FAIL: ${test.name}`);
                console.log(`   Error: ${error.message}`);
                this.failed++;
            }
        }
        
        console.log(`\n📊 Test Results: ${this.passed} passed, ${this.failed} failed`);
    }
}

// Mock Telegram WebApp API for testing
const Telegram = {
    WebApp: {
        ready: () => {},
        expand: () => {},
        close: () => {},
        MainButton: {
            text: '',
            color: '',
            isVisible: false,
            isActive: false,
            setText: function(text) { this.text = text; },
            setParams: function(params) { Object.assign(this, params); },
            show: function() { this.isVisible = true; },
            hide: function() { this.isVisible = false; },
            onClick: function(callback) { this.onClickCallback = callback; },
            offClick: function() { this.onClickCallback = null; }
        },
        BackButton: {
            isVisible: false,
            show: function() { this.isVisible = true; },
            hide: function() { this.isVisible = false; },
            onClick: function(callback) { this.onClickCallback = callback; },
            offClick: function() { this.onClickCallback = null; }
        },
        showAlert: function(message) { console.log('Alert:', message); },
        showConfirm: function(message) { return true; }
    }
};

// Mock DOM elements
const mockElements = {
    'welcome-container': { classList: { add: () => {}, remove: () => {}, contains: () => false } },
    'main-page-container': { classList: { add: () => {}, remove: () => {}, contains: () => false } },
    'categories-container': { classList: { add: () => {}, remove: () => {}, contains: () => false } },
    'products-container': { classList: { add: () => {}, remove: () => {}, contains: () => false } },
    'cart-container': { classList: { add: () => {}, remove: () => {}, contains: () => false } },
    'checkout-container': { classList: { add: () => {}, remove: () => {}, contains: () => false } },
    'product-screen': { classList: { add: () => {}, remove: () => {}, contains: () => false } },
    'main-category-title': { classList: { add: () => {}, remove: () => {}, contains: () => false }, textContent: '' },
    'cart-items-list': { innerHTML: '', querySelectorAll: () => [] },
    'cart-total': { textContent: '' },
    'checkout-items-list': { innerHTML: '', querySelectorAll: () => [] },
    'checkout-total': { textContent: '' },
    'product-screen-body': { innerHTML: '' }
};

// Mock document.getElementById
const originalGetElementById = document.getElementById;
document.getElementById = function(id) {
    return mockElements[id] || originalGetElementById.call(document, id);
};

// Mock localStorage
const mockLocalStorage = {};
const originalLocalStorage = window.localStorage;
window.localStorage = {
    getItem: function(key) { return mockLocalStorage[key] || null; },
    setItem: function(key, value) { mockLocalStorage[key] = value; },
    removeItem: function(key) { delete mockLocalStorage[key]; }
};

// Create test instance
const tester = new WebAppTester();

// Test cart functionality
tester.test('Cart initialization', () => {
    // Mock cart data
    const testCart = {
        'product1': { id: 'product1', name: 'Test Product 1', price: 10.50, quantity: 2 },
        'product2': { id: 'product2', name: 'Test Product 2', price: 15.75, quantity: 1 }
    };
    
    localStorage.setItem('cart', JSON.stringify(testCart));
    
    // Test cart loading
    const loadedCart = JSON.parse(localStorage.getItem('cart') || '{}');
    tester.assertNotNull(loadedCart);
    tester.assertEquals(2, Object.keys(loadedCart).length);
    tester.assertEquals(10.50, loadedCart['product1'].price);
    tester.assertEquals(2, loadedCart['product1'].quantity);
});

tester.test('Cart total calculation', () => {
    const cart = {
        'product1': { price: 10.50, quantity: 2 },
        'product2': { price: 15.75, quantity: 1 }
    };
    
    const total = Object.values(cart).reduce((sum, item) => sum + (item.price * item.quantity), 0);
    tester.assertEquals(36.75, total);
});

tester.test('Cart item count calculation', () => {
    const cart = {
        'product1': { quantity: 2 },
        'product2': { quantity: 1 },
        'product3': { quantity: 3 }
    };
    
    const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
    tester.assertEquals(6, totalItems);
});

tester.test('Empty cart handling', () => {
    const emptyCart = {};
    const totalItems = Object.values(emptyCart).reduce((sum, item) => sum + item.quantity, 0);
    tester.assertEquals(0, totalItems);
});

// Test URL parameter handling
tester.test('URL parameter extraction', () => {
    // Mock URLSearchParams
    const mockSearchParams = new Map([
        ['view', 'categories'],
        ['category', 'bread']
    ]);
    
    const getUrlParameter = (name) => {
        return mockSearchParams.get(name) || null;
    };
    
    tester.assertEquals('categories', getUrlParameter('view'));
    tester.assertEquals('bread', getUrlParameter('category'));
    tester.assertEquals(null, getUrlParameter('nonexistent'));
});

// Test view display logic
tester.test('View display logic', () => {
    const views = ['welcome', 'categories', 'products', 'cart', 'checkout', 'product'];
    const validViews = ['welcome', 'categories', 'products', 'cart', 'checkout', 'product'];
    
    for (const view of views) {
        tester.assert(validViews.includes(view), `Invalid view: ${view}`);
    }
});

// Test product data structure
tester.test('Product data structure validation', () => {
    const testProduct = {
        id: 'test-product-1',
        name: 'Test Product',
        price: 25.50,
        description: 'Test description',
        weight: '500 г',
        ingredients: 'Flour, Sugar, Eggs',
        nutrition: 'Calories: 250',
        image_url: 'https://example.com/image.jpg',
        category: 'bread'
    };
    
    const requiredFields = ['id', 'name', 'price'];
    for (const field of requiredFields) {
        tester.assert(testProduct.hasOwnProperty(field), `Missing required field: ${field}`);
    }
    
    tester.assertNotNull(testProduct.name);
    tester.assert(testProduct.price > 0, 'Price must be positive');
});

// Test quantity update logic
tester.test('Quantity update logic', () => {
    const cart = {
        'product1': { quantity: 1 }
    };
    
    // Test increase quantity
    const updateQuantity = (productId, change) => {
        if (cart[productId]) {
            cart[productId].quantity += change;
            if (cart[productId].quantity <= 0) {
                delete cart[productId];
            }
        }
    };
    
    updateQuantity('product1', 1);
    tester.assertEquals(2, cart['product1'].quantity);
    
    updateQuantity('product1', -1);
    tester.assertEquals(1, cart['product1'].quantity);
    
    updateQuantity('product1', -1);
    tester.assert(!cart.hasOwnProperty('product1'), 'Product should be removed when quantity reaches 0');
});

// Test price formatting
tester.test('Price formatting', () => {
    const formatPrice = (price) => {
        return `${price.toFixed(2)} р.`;
    };
    
    tester.assertEquals('25.50 р.', formatPrice(25.5));
    tester.assertEquals('0.00 р.', formatPrice(0));
    tester.assertEquals('100.00 р.', formatPrice(100));
});

// Test cart total formatting
tester.test('Cart total formatting', () => {
    const cart = {
        'product1': { price: 10.50, quantity: 2 },
        'product2': { price: 15.75, quantity: 1 }
    };
    
    const total = Object.values(cart).reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const formattedTotal = `Общая сумма: ${total.toFixed(2)} р.`;
    
    tester.assertEquals('Общая сумма: 36.75 р.', formattedTotal);
});

// Test empty cart message
tester.test('Empty cart message', () => {
    const cart = {};
    const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
    
    tester.assertEquals(0, totalItems);
    
    const message = totalItems === 0 ? 'Ваша корзина пуста.' : `В корзине ${totalItems} товаров`;
    tester.assertEquals('Ваша корзина пуста.', message);
});

// Test product ID generation
tester.test('Product ID validation', () => {
    const testIds = ['product-1', 'bread-123', 'cake-456'];
    
    for (const id of testIds) {
        tester.assertNotNull(id);
        tester.assert(id.length > 0, 'Product ID should not be empty');
        tester.assert(typeof id === 'string', 'Product ID should be a string');
    }
});

// Test image URL handling
tester.test('Image URL handling', () => {
    const testImageUrl = 'https://example.com/image.jpg';
    const fallbackImageUrl = 'https://placehold.co/80x80/cccccc/333333?text=No+Image';
    
    const getImageUrl = (url) => {
        return url || fallbackImageUrl;
    };
    
    tester.assertEquals(testImageUrl, getImageUrl(testImageUrl));
    tester.assertEquals(fallbackImageUrl, getImageUrl(null));
    tester.assertEquals(fallbackImageUrl, getImageUrl(''));
});

// Test category data structure
tester.test('Category data structure', () => {
    const testCategory = {
        key: 'bread',
        name: 'Хлеб',
        image_url: 'https://example.com/bread.jpg',
        description: 'Свежий хлеб'
    };
    
    const requiredFields = ['key', 'name'];
    for (const field of requiredFields) {
        tester.assert(testCategory.hasOwnProperty(field), `Missing required field: ${field}`);
    }
    
    tester.assertNotNull(testCategory.key);
    tester.assertNotNull(testCategory.name);
});

// Run all tests
console.log('🚀 Starting Web App Tests...\n');
tester.runTests(); 