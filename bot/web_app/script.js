// Инициализация Telegram Web App
Telegram.WebApp.ready();
Telegram.WebApp.expand(); // Разворачиваем Web App на весь экран

// ===== PHASE 4: BROWSER CACHE API INTEGRATION =====
// Cache versioning and management system
    const CACHE_VERSION = '1.3.95';
const CACHE_NAME = `bakery-app-v${CACHE_VERSION}`;

// Customer data constants (moved here for scope access)
const CUSTOMER_DATA_KEY = 'customer_data';
const CUSTOMER_DATA_VERSION = '1.0.0';
const CUSTOMER_DATA_EXPIRATION_DAYS = 365; // Keep customer data for 1 year
const CUSTOMER_DATA_EXPIRATION_MS = CUSTOMER_DATA_EXPIRATION_DAYS * 24 * 60 * 60 * 1000;

// Mobile detection for cache strategy
const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const isIOSDevice = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
const isAndroidDevice = /Android/i.test(navigator.userAgent);
const isTelegramWebView = window.Telegram && window.Telegram.WebApp;

// Smart cache management functions that preserve cart data
async function clearBrowserCache() {
    try {
        if ('caches' in window) {
            // Clear all caches
            const cacheNames = await caches.keys();
            await Promise.all(
                cacheNames.map(cacheName => caches.delete(cacheName))
            );
            console.log('🧹 Browser cache cleared successfully');
        }
        
        // SMART CLEAR: Preserve cart data and essential app data
        const cartData = localStorage.getItem('cart');
        const cartVersion = localStorage.getItem('cart_version');
        const appVersion = localStorage.getItem('app_version');
        
        // Clear sessionStorage completely
        sessionStorage.clear();
        
        // Selectively clear localStorage (preserve cart and customer data)
        const keysToPreserve = ['cart', 'cart_version', 'app_version', CUSTOMER_DATA_KEY];
        const keysToClear = [];
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && !keysToPreserve.includes(key)) {
                keysToClear.push(key);
            }
        }
        
        // Clear only non-essential keys
        keysToClear.forEach(key => localStorage.removeItem(key));
        
        // Restore essential data if accidentally cleared
        if (cartData && !localStorage.getItem('cart')) {
            localStorage.setItem('cart', cartData);
            console.log('🛒 Cart data preserved during cache clear');
        }
        if (cartVersion && !localStorage.getItem('cart_version')) {
            localStorage.setItem('cart_version', cartVersion);
        }
        if (appVersion && !localStorage.getItem('app_version')) {
            localStorage.setItem('app_version', appVersion);
        }
        
        // Preserve customer data during cache clear
        const customerData = localStorage.getItem(CUSTOMER_DATA_KEY);
        if (customerData) {
            console.log('👤 Customer data preserved during cache clear');
        }
        
        console.log('🧹 Smart cache clear completed - cart preserved');
        return true;
    } catch (error) {
        console.error('❌ Error clearing browser cache:', error);
        return false;
    }
}

async function invalidateCacheOnUpdate() {
    try {
        const storedVersion = localStorage.getItem('app_version');
        
        // For mobile devices, use more aggressive cache invalidation
        if (isMobileDevice && isTelegramWebView) {
            console.log('📱 Mobile Telegram WebApp detected - using aggressive cache strategy');
            
            if (storedVersion !== CACHE_VERSION) {
                console.log(`🔄 Mobile: App version changed from ${storedVersion} to ${CACHE_VERSION}`);
                
                // Smart clear that preserves cart
                await clearBrowserCache();
                
                // Force reload CSS/JS with timestamps
                await forceMobileResourceReload();
                
                // Store new version
                localStorage.setItem('app_version', CACHE_VERSION);
                
                // Force reload with cache bypass
                setTimeout(() => {
                    const url = window.location.href;
                    const separator = url.includes('?') ? '&' : '?';
                    window.location.href = url + separator + '_cache_bust=' + Date.now();
                }, 500);
                
                return true;
            }
        } else {
            // Desktop logic - less aggressive
            if (storedVersion !== CACHE_VERSION) {
                console.log(`🔄 Desktop: App version changed from ${storedVersion} to ${CACHE_VERSION}`);
                
                // Smart clear that preserves cart
                await clearBrowserCache();
                
                // Store new version
                localStorage.setItem('app_version', CACHE_VERSION);
                
                // Simple reload for desktop
                window.location.reload();
                return true;
            }
        }
        
        return false;
    } catch (error) {
        console.error('❌ Error during cache invalidation:', error);
        return false;
    }
}

// Mobile-specific resource reloading function
async function forceMobileResourceReload() {
    try {
        const timestamp = Date.now();
        console.log('📱 Forcing mobile resource reload with timestamp:', timestamp);
        
        // Force reload CSS files
        const links = document.querySelectorAll('link[rel="stylesheet"]');
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && !href.includes('telegram.org')) {
                const separator = href.includes('?') ? '&' : '?';
                const newHref = href + separator + '_mobile_t=' + timestamp;
                link.setAttribute('href', newHref);
                console.log('🔄 CSS reloaded:', newHref);
            }
        });
        
        // Force reload script files (except Telegram SDK)
        const scripts = document.querySelectorAll('script[src]');
        scripts.forEach(script => {
            const src = script.getAttribute('src');
            if (src && !src.includes('telegram.org')) {
                const separator = src.includes('?') ? '&' : '?';
                const newSrc = src + separator + '_mobile_t=' + timestamp;
                script.setAttribute('src', newSrc);
                console.log('🔄 JS reloaded:', newSrc);
            }
        });
        
        // Force reload images
        const images = document.querySelectorAll('img[src]');
        images.forEach(img => {
            const src = img.getAttribute('src');
            if (src) {
                const separator = src.includes('?') ? '&' : '?';
                const newSrc = src + separator + '_mobile_t=' + timestamp;
                img.setAttribute('src', newSrc);
            }
        });
        
        return true;
    } catch (error) {
        console.error('❌ Error in mobile resource reload:', error);
        return false;
    }
}

// Telegram WebView specific cache clearing
function forceTelegramCacheClear() {
    try {
        if (isTelegramWebView && isMobileDevice) {
            if (DEBUG) console.log('📱 Telegram WebView detected - implementing aggressive cache clear');
            
            // Preserve cart data before any operations
            const cartData = localStorage.getItem('cart');
            const cartVersion = localStorage.getItem('cart_version');
            
            // Clear browser caches
            if ('caches' in window) {
                caches.keys().then(function(names) {
                    for (let name of names) {
                        caches.delete(name);
                    }
                });
            }
            
            // Clear session storage
            sessionStorage.clear();
            
            // Restore cart data immediately
            if (cartData) {
                localStorage.setItem('cart', cartData);
                if (DEBUG) console.log('🛒 Cart data preserved in Telegram WebView');
            }
            if (cartVersion) {
                localStorage.setItem('cart_version', cartVersion);
            }
            
            // Force resource reload
            forceMobileResourceReload();
            
            return true;
        }
        return false;
    } catch (error) {
        if (DEBUG) console.error('❌ Error in Telegram cache clear:', error);
        return false;
    }
}

// Initialize cache management on app start
async function initializeCacheManagement() {
    try {
        console.log('🚀 Initializing smart cache management...');
        console.log('📱 Mobile device:', isMobileDevice);
        console.log('🍎 iOS device:', isIOSDevice);
        console.log('💬 Telegram WebView:', isTelegramWebView);
        
        // Mobile-specific initialization
        if (isMobileDevice && isTelegramWebView) {
            console.log('📱 Mobile Telegram WebView - using aggressive cache strategy');
            forceTelegramCacheClear();
        }
        
        // Check if cache invalidation is needed (but not during form validation)
        if (!document.querySelector('#checkout-form')) {
            await invalidateCacheOnUpdate();
        } else {
            console.log('🛒 Checkout form detected - skipping cache invalidation to preserve cart');
        }
        
        // Set up periodic cache health check (less frequent for mobile to save battery)
        const checkInterval = isMobileDevice ? 600000 : 300000; // 10min mobile, 5min desktop
        setInterval(async () => {
            const cacheHealth = await checkCacheHealth();
            if (!cacheHealth) {
                console.warn('⚠️ Cache health check failed, clearing cache (preserving cart)');
                await clearBrowserCache();
            }
        }, checkInterval);
        
        // Set up periodic cart expiration check
        setInterval(() => {
            const cartExpired = checkCartExpiration();
            if (cartExpired) {
                console.log('⏰ Periodic check: Cart expired, clearing...');
                cart = {};
                renderCart();
                updateMainButtonCartInfo();
            }
        }, 600000); // Check every 10 minutes
        
        // Service Worker integration removed to fix iOS twitching issues
        
        console.log('✅ Cache management initialized (Service Worker removed)');
    } catch (error) {
        console.error('❌ Error initializing cache management:', error);
    }
}

async function checkCacheHealth() {
    try {
        if ('caches' in window) {
            const cache = await caches.open(CACHE_NAME);
            return cache !== null;
        }
        return true; // If caches not supported, consider healthy
    } catch (error) {
        console.error('❌ Cache health check error:', error);
        return false;
    }
}

// ===== END PHASE 4 =====

// ===== PHASE 5: LOCALSTORAGE CACHE MANAGEMENT =====
// Cart data structure and versioning
const CART_DATA_VERSION = '1.0.0';
const CART_EXPIRATION_DAYS = 2; // Cart expires after 2 days
const CART_EXPIRATION_MS = CART_EXPIRATION_DAYS * 24 * 60 * 60 * 1000;

// Enhanced cart data structure with metadata
function createCartWithMetadata(cartData) {
    return {
        version: CART_DATA_VERSION,
        timestamp: Date.now(),
        expiresAt: Date.now() + CART_EXPIRATION_MS,
        data: cartData || {}
    };
}

// Load cart with expiration check and migration
function loadCartWithExpiration() {
    try {
        const cartItem = localStorage.getItem('cart');
        if (!cartItem) {
            console.log('📦 No cart found in localStorage');
            return {};
        }

        let cartData;
        try {
            cartData = JSON.parse(cartItem);
        } catch (parseError) {
            console.error('❌ Error parsing cart data:', parseError);
            localStorage.removeItem('cart');
            return {};
        }

        // Check if this is the new format with metadata
        if (cartData && typeof cartData === 'object' && cartData.version && cartData.timestamp) {
            console.log('📦 Cart data version:', cartData.version);
            
            // Check expiration
            if (Date.now() > cartData.expiresAt) {
                console.log('⏰ Cart expired, clearing...');
                localStorage.removeItem('cart');
                return {};
            }
            
            // Check if version needs migration
            if (cartData.version !== CART_DATA_VERSION) {
                console.log(`🔄 Cart version ${cartData.version} needs migration to ${CART_DATA_VERSION}`);
                // For now, just clear and start fresh (can be enhanced later)
                localStorage.removeItem('cart');
                return {};
            }
            
            console.log('✅ Cart loaded successfully with metadata');
            return cartData.data;
        } else {
            // Legacy cart format - migrate to new format
            console.log('🔄 Migrating legacy cart to new format');
            const migratedCart = createCartWithMetadata(cartData);
            localStorage.setItem('cart', JSON.stringify(migratedCart));
            console.log('✅ Cart migrated successfully');
            return cartData;
        }
    } catch (error) {
        console.error('❌ Error loading cart:', error);
        return {};
    }
}

// Save cart with metadata
function saveCartWithMetadata(cartData) {
    try {
        const cartWithMetadata = createCartWithMetadata(cartData);
        localStorage.setItem('cart', JSON.stringify(cartWithMetadata));
        console.log('💾 Cart saved with metadata');
        return true;
    } catch (error) {
        console.error('❌ Error saving cart:', error);
        return false;
    }
}

// Check cart expiration and clean up if needed
function checkCartExpiration() {
    try {
        const cartItem = localStorage.getItem('cart');
        if (!cartItem) return false;
        
        const cartData = JSON.parse(cartItem);
        if (cartData && cartData.expiresAt && Date.now() > cartData.expiresAt) {
            console.log('⏰ Cart expired, cleaning up...');
            localStorage.removeItem('cart');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ Error checking cart expiration:', error);
        return false;
    }
}

// Get cart age in days
function getCartAge() {
    try {
        const cartItem = localStorage.getItem('cart');
        if (!cartItem) return null;
        
        const cartData = JSON.parse(cartItem);
        if (cartData && cartData.timestamp) {
            const ageMs = Date.now() - cartData.timestamp;
            const ageDays = ageMs / (24 * 60 * 60 * 1000);
            return Math.round(ageDays * 100) / 100; // Round to 2 decimal places
        }
        return null;
    } catch (error) {
        console.error('❌ Error getting cart age:', error);
        return null;
    }
}

// ===== END PHASE 5 =====

// ===== PHASE 6: SERVICE WORKER INTEGRATION =====
// Service Worker removed to fix iOS twitching issues
// ===== END PHASE 6 =====

// ===== PHASE 7: CUSTOMER DATA PERSISTENCE =====
// Customer data structure and versioning for prepopulated form fields
// Constants moved to Phase 4 for scope access

// Enhanced customer data structure with metadata
function createCustomerDataWithMetadata(customerData) {
    return {
        version: CUSTOMER_DATA_VERSION,
        timestamp: Date.now(),
        expiresAt: Date.now() + CUSTOMER_DATA_EXPIRATION_MS,
        data: customerData || {}
    };
}

// Load customer data with expiration check and migration
function loadCustomerDataWithExpiration() {
    try {
        const customerDataItem = localStorage.getItem(CUSTOMER_DATA_KEY);
        if (!customerDataItem) {
            console.log('👤 No customer data found in localStorage');
            return {};
        }

        let customerData;
        try {
            customerData = JSON.parse(customerDataItem);
        } catch (parseError) {
            console.error('❌ Error parsing customer data:', parseError);
            localStorage.removeItem(CUSTOMER_DATA_KEY);
            return {};
        }

        // Check if this is the new format with metadata
        if (customerData && typeof customerData === 'object' && customerData.version && customerData.timestamp) {
            console.log('👤 Customer data version:', customerData.version);
            
            // Check expiration
            if (Date.now() > customerData.expiresAt) {
                console.log('⏰ Customer data expired, clearing...');
                localStorage.removeItem(CUSTOMER_DATA_KEY);
                return {};
            }
            
            // Check if version needs migration
            if (customerData.version !== CUSTOMER_DATA_VERSION) {
                console.log(`🔄 Customer data version ${customerData.version} needs migration to ${CUSTOMER_DATA_VERSION}`);
                // For now, just clear and start fresh (can be enhanced later)
                localStorage.removeItem(CUSTOMER_DATA_KEY);
                return {};
            }
            
            console.log('✅ Customer data loaded successfully with metadata');
            return customerData.data;
        } else {
            // Legacy customer data format - migrate to new format
            console.log('🔄 Migrating legacy customer data to new format');
            const migratedCustomerData = createCustomerDataWithMetadata(customerData);
            localStorage.setItem(CUSTOMER_DATA_KEY, JSON.stringify(migratedCustomerData));
            console.log('✅ Customer data migrated successfully');
            return customerData;
        }
    } catch (error) {
        console.error('❌ Error loading customer data:', error);
        return {};
    }
}

// Save customer data with metadata
function saveCustomerDataWithMetadata(customerData) {
    try {
        const customerDataWithMetadata = createCustomerDataWithMetadata(customerData);
        localStorage.setItem(CUSTOMER_DATA_KEY, JSON.stringify(customerDataWithMetadata));
        console.log('💾 Customer data saved with metadata');
        return true;
    } catch (error) {
        console.error('❌ Error saving customer data:', error);
        return false;
    }
}

// Extract customer data from form
function extractCustomerDataFromForm() {
    try {
        const form = document.getElementById('checkout-form');
        if (!form) return {};

        const formData = new FormData(form);
        const customerData = {};

        // Extract only the fields we want to persist
        const fieldsToPersist = ['firstName', 'lastName', 'middleName', 'phoneNumber', 'email', 'city', 'addressLine'];
        
        for (let [key, value] of formData.entries()) {
            if (fieldsToPersist.includes(key) && value.trim()) {
                customerData[key] = value.trim();
            }
        }

        return customerData;
    } catch (error) {
        console.error('❌ Error extracting customer data from form:', error);
        return {};
    }
}

// Populate form with customer data
function populateFormWithCustomerData(customerData) {
    try {
        if (!customerData || Object.keys(customerData).length === 0) {
            console.log('👤 No customer data to populate');
            return;
        }

        console.log('👤 Populating form with customer data:', customerData);

        // Populate each field if data exists
        const fieldMappings = {
            'firstName': 'first-name',
            'lastName': 'last-name', 
            'middleName': 'middle-name',
            'phoneNumber': 'phone-number',
            'email': 'email',
            'city': 'city',
            'addressLine': 'address-line'
        };

        for (const [dataKey, elementId] of Object.entries(fieldMappings)) {
            if (customerData[dataKey]) {
                const element = document.getElementById(elementId);
                if (element) {
                    element.value = customerData[dataKey];
                    console.log(`👤 Populated ${elementId} with: ${customerData[dataKey]}`);
                    // Clear any stale validation error for prefilled fields
                    const errorIdMap = {
                        firstName: 'first-name-error',
                        lastName: 'last-name-error',
                        middleName: 'middle-name-error',
                        phoneNumber: 'phone-number-error',
                        email: 'email-error',
                        city: 'city-error',
                        addressLine: 'address-line-error'
                    };
                    const errEl = document.getElementById(errorIdMap[dataKey]);
                    if (errEl) {
                        errEl.classList.remove('show');
                        errEl.style.display = 'none';
                        errEl.style.color = '';
                    }
                    element.classList.remove('form-field-error');
                }
            }
        }

        console.log('✅ Form populated with customer data');
    } catch (error) {
        console.error('❌ Error populating form with customer data:', error);
    }
}

// Clear customer data
function clearCustomerData() {
    try {
        localStorage.removeItem(CUSTOMER_DATA_KEY);
        console.log('🗑️ Customer data cleared successfully');
        return true;
    } catch (error) {
        console.error('❌ Error clearing customer data:', error);
        return false;
    }
}

// Check customer data expiration and clean up if needed
function checkCustomerDataExpiration() {
    try {
        const customerDataItem = localStorage.getItem(CUSTOMER_DATA_KEY);
        if (!customerDataItem) return false;
        
        const customerData = JSON.parse(customerDataItem);
        if (customerData && customerData.expiresAt && Date.now() > customerData.expiresAt) {
            console.log('⏰ Customer data expired, cleaning up...');
            localStorage.removeItem(CUSTOMER_DATA_KEY);
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ Error checking customer data expiration:', error);
        return false;
    }
}

// Get customer data age in days
function getCustomerDataAge() {
    try {
        const customerDataItem = localStorage.getItem(CUSTOMER_DATA_KEY);
        if (!customerDataItem) return null;
        
        const customerData = JSON.parse(customerDataItem);
        if (customerData && customerData.timestamp) {
            const ageMs = Date.now() - customerData.timestamp;
            const ageDays = ageMs / (24 * 60 * 60 * 1000);
            return Math.round(ageDays * 100) / 100; // Round to 2 decimal places
        }
        return null;
    } catch (error) {
        console.error('❌ Error getting customer data age:', error);
        return null;
    }
}

// ===== END PHASE 7 =====

// Helper function to create SVG icons
function createIcon(iconName, className = '') {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const use = document.createElementNS('http://www.w3.org/1999/xlink', 'use');
    
    svg.setAttribute('class', `icon ${className}`);
    use.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#${iconName}`);
    
    svg.appendChild(use);
    return svg;
}

// Helper function to create icon with specific size
function createIconWithSize(iconName, size = 'normal', className = '') {
    const icon = createIcon(iconName, className);
    
    switch(size) {
        case 'small':
            icon.classList.add('icon--small');
            break;
        case 'large':
            icon.classList.add('icon--large');
            break;
        case 'xl':
            icon.classList.add('icon--xl');
            break;
    }
    
    return icon;
}

// Helper function to create icon with color
function createIconWithColor(iconName, color = 'primary', size = 'normal', className = '') {
    const icon = createIconWithSize(iconName, size, className);
    icon.classList.add(`icon--${color}`);
    return icon;
}

// Common icon creation functions
function createCartIcon(size = 'normal', color = 'primary') {
    return createIconWithColor('cart', color, size);
}

function createCloseIcon(size = 'normal', color = 'dark') {
    return createIconWithColor('close', color, size);
}

function createDeliveryIcon(size = 'normal', color = 'primary') {
    return createIconWithColor('delivery', color, size);
}

function createLocationIcon(size = 'normal', color = 'primary') {
    return createIconWithColor('location', color, size);
}

function createMoneyIcon(size = 'normal', color = 'primary') {
    return createIconWithColor('money', color, size);
}

function createTakeawayIcon(size = 'normal', color = 'primary') {
    return createIconWithColor('takeaway', color, size);
}

// Helper function to replace text with icon
function replaceTextWithIcon(element, iconName, size = 'normal', color = 'primary') {
    const icon = createIconWithColor(iconName, color, size);
    element.innerHTML = '';
    element.appendChild(icon);
}

// Function to initialize icons in the UI
function initializeIcons() {
    // Icons removed as requested - keeping function for potential future use
    
    // Add icons to delivery method labels
    addDeliveryMethodIcons();

    // Add money icon to cart total
    addMoneyIconToCartTotal();
    
    // Add location icons to address fields
    // addLocationIcons(); // Disabled to remove icons from city and address fields
}

// Function to add icons to delivery method labels
function addDeliveryMethodIcons() {
    const courierLabel = document.querySelector('label[for="delivery-courier-radio"]');
    const pickupLabel = document.querySelector('label[for="delivery-pickup-radio"]');
    
    if (courierLabel) {
        const icon = createIconWithColor('delivery', 'primary', 'small');
        courierLabel.insertBefore(icon, courierLabel.firstChild);
        courierLabel.classList.add('btn-with-icon');
    }
    
    if (pickupLabel) {
        const icon = createIconWithColor('takeaway', 'primary', 'small');
        pickupLabel.insertBefore(icon, pickupLabel.firstChild);
        pickupLabel.classList.add('btn-with-icon');
    }
}

// Function to add money icon to cart total
function addMoneyIconToCartTotal() {
    const cartTotal = document.getElementById('cart-total');
    if (cartTotal && !cartTotal.querySelector('.icon')) {
        const icon = createIconWithColor('money', 'primary', 'small');
        cartTotal.insertBefore(icon, cartTotal.firstChild);
        cartTotal.classList.add('btn-with-icon');
    }
}

// Function to add location icons to address fields
function addLocationIcons() {
    const cityLabel = document.querySelector('label[for="city"]');
    const addressLabel = document.querySelector('label[for="address-line"]');
    
    if (cityLabel && !cityLabel.querySelector('.icon')) {
        const icon = createIconWithColor('location', 'primary', 'small');
        cityLabel.insertBefore(icon, cityLabel.firstChild);
        cityLabel.classList.add('btn-with-icon');
    }
    
    if (addressLabel && !addressLabel.querySelector('.icon')) {
        const icon = createIconWithColor('location', 'primary', 'small');
        addressLabel.insertBefore(icon, addressLabel.firstChild);
        addressLabel.classList.add('btn-with-icon');
    }
}

// Form validation helper functions
function clearAllErrors() {
    // Remove error styling from all form fields
    document.querySelectorAll('.form-field-error').forEach(field => {
        field.classList.remove('form-field-error');
    });
    
    // Hide all error messages
    document.querySelectorAll('.error-message').forEach(message => {
        message.classList.remove('show');
        // Reset display style to hide the error message
        message.style.display = 'none';
        message.style.color = '';
    });
}

function clearFieldError(fieldName) {
    // Clear error styling from specific field
    const fieldElement = document.getElementById(fieldName) || 
                        document.querySelector(`[name="${fieldName}"]`) ||
                        document.querySelector(`#${fieldName}`);
    
    if (fieldElement) {
        fieldElement.classList.remove('form-field-error');
    }
    
    // Clear container errors for radio groups
    if (fieldName === 'pickupAddress') {
        const pickupContainer = document.getElementById('pickup-radio-group');
        if (pickupContainer) {
            pickupContainer.classList.remove('form-field-error');
        }
    } else if (fieldName === 'paymentMethod') {
        const paymentContainer = document.getElementById('payment-method-section');
        if (paymentContainer) {
            paymentContainer.classList.remove('form-field-error');
        }
    } else if (fieldName === 'paymentMethodPickup') {
        const paymentPickupContainer = document.getElementById('payment-method-section-pickup');
        if (paymentPickupContainer) {
            paymentPickupContainer.classList.remove('form-field-error');
        }
    }
    
    // Hide corresponding error message - handle camelCase and kebab-case IDs
    const toKebab = (s) => s.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
    let errorMessageElement = document.getElementById(fieldName + '-error');
    if (!errorMessageElement) {
        // Try camelCase normalized from hyphenated input
        const camelCaseFieldName = fieldName.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
        errorMessageElement = document.getElementById(camelCaseFieldName + '-error');
    }
    if (!errorMessageElement) {
        // Try kebab-case from camelCase input (e.g., deliveryDate -> delivery-date-error)
        const kebabName = toKebab(fieldName);
        errorMessageElement = document.getElementById(kebabName + '-error');
    }
    if (errorMessageElement) {
        errorMessageElement.classList.remove('show');
        // Reset display style to hide the error message
        errorMessageElement.style.display = 'none';
        errorMessageElement.style.color = '';
    }
}

function showValidationErrors(errorFields, errorMessages) {
    console.log('🎯 === SHOW VALIDATION ERRORS CALLED ===');
    console.log('📝 Error fields to process:', errorFields.length);
    console.log('📝 Error messages to show:', errorMessages.length);
    
    // Clear previous errors first
    clearAllErrors();
    
    // Debug: Check if error message elements exist
    console.log('🔍 === ERROR VALIDATION DEBUG ===');
    console.log('Error fields:', errorFields);
    console.log('Error messages:', errorMessages);
    
    // Test if error message elements exist
    const testErrorElements = ['lastName-error', 'firstName-error', 'paymentMethod-error', 'pickupAddress-error'];
    testErrorElements.forEach(id => {
        const element = document.getElementById(id);
        console.log(`Error element ${id}:`, element);
    });
    console.log('=== END DEBUG ===');
    
    // Show error messages and highlight error fields
    errorFields.forEach((errorField, index) => {
        if (errorField.element || errorField.errorContainer) {
            // Add error styling to the field
            // For radio groups, style the container instead of individual radio
            if (errorField.elementType === 'radio' && errorField.errorContainer) {
                // Add visual indicator to radio group container
                errorField.errorContainer.classList.add('form-field-error');
                console.log(`Added error styling to radio container for: ${errorField.field}`);
            } else if (errorField.element && !['paymentMethod', 'paymentMethodPickup', 'pickupAddress', 'deliveryMethod'].includes(errorField.field)) {
                // For regular inputs, add error class
                errorField.element.classList.add('form-field-error');
            }
            
            // Show corresponding error message
            const errorMessageId = errorField.field + '-error';
            const errorMessageElement = document.getElementById(errorMessageId);
            console.log(`Looking for error message with ID: ${errorMessageId}`, errorMessageElement);
            if (errorMessageElement) {
                errorMessageElement.classList.add('show');
                errorMessageElement.style.display = 'block';  // Force display
                errorMessageElement.style.color = '#ff4444';  // Force red color
                console.log(`Error message shown for: ${errorField.field}`);
            } else {
                console.error(`Error message element not found for: ${errorField.field}`);
                // Try alternative selectors
                const alternativeElement = document.querySelector(`[id*="${errorField.field}"][id*="error"]`);
                if (alternativeElement) {
                    console.log(`Found alternative error element:`, alternativeElement);
                    alternativeElement.classList.add('show');
                    alternativeElement.style.display = 'block';
                    alternativeElement.style.color = '#ff4444';
                }
            }
            
            // Focus behavior for the first error field
            if (index === 0 && errorField.element) {
                console.log('🎯 === HANDLE FIRST ERROR FIELD ===');
                console.log('🎯 Field name:', errorField.field);
                console.log('🎯 Field element:', errorField.element);
                console.log('🎯 Field element ID:', errorField.element ? errorField.element.id : 'none');
                console.log('🎯 Field element type:', errorField.element ? errorField.element.type : 'none');

                // For deliveryDate: do NOT focus to avoid opening calendar; just scroll into view
                if (errorField.field !== 'deliveryDate' && errorField.element.focus) {
                    try {
                        errorField.element.focus();
                        console.log('🎯 Focus() called on:', errorField.field);
                    } catch (e) {
                        console.log('🎯 Could not focus on:', errorField.field, e);
                    }
                } else {
                    console.log('🎯 Skipping focus on:', errorField.field);
                }

                // Ensure the field is visible - scroll to container for radio groups
                const scrollTarget = errorField.errorContainer || errorField.element;
                if (scrollTarget && scrollTarget.scrollIntoView) {
                    console.log('🎯 Scrolling to:', errorField.field);
                    scrollTarget.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }
                console.log('🎯 === FIRST ERROR HANDLED ===');
            }
        }
    });
    
    // Log all error messages
    console.error('Validation errors:', errorMessages.join('\n'));
}

// ===== UNIFIED FORM VALIDATION SYSTEM =====
// Add this before the DOMContentLoaded event listener

function validateField(value, validation) {
    // Empty check
    if (!value || value.trim() === '') {
        console.log(`❌ ${validation.field} validation FAILED - empty value`);
        return false;
    }

    // Regex validation
    if (validation.regex && !validation.regex.test(value)) {
        console.log(`❌ ${validation.field} validation FAILED - regex mismatch`);
        return false;
    }

    // Custom validation
    if (validation.customValidation) {
        const customResult = validation.customValidation(value);
        if (!customResult) {
            console.log(`❌ ${validation.field} validation FAILED - custom validation`);
        }
        return customResult;
    }

    return true;
}

// Custom validation functions for all field types
function validateNameField(value) {
    if (!value || value.trim() === '') return false;
    // Allow all Cyrillic and Latin letters, spaces, hyphens, and apostrophes
    const nameRegex = /^[\p{Script=Latin}\p{Script=Cyrillic}\s\-']+$/u;
    return nameRegex.test(value.trim());
}

function validatePhoneField(value) {
    if (!value || value.trim() === '') return false;
    const phoneRegex = /^\+?[\d\s\-\(\)]{7,20}$/;
    return phoneRegex.test(value.trim());
}

function validateEmailField(value) {
    if (!value || value.trim() === '') return false;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value.trim());
}

function validateDeliveryDateField(value) {
    if (!value || value.trim() === '') return false;
    if (value.trim() === 'Выберите дату') return false;

    // Expect DD.MM.YYYY, parse safely instead of relying on Date(string)
    const dateRegex = /^(\d{2})\.(\d{2})\.(\d{4})$/;
    const match = value.trim().match(dateRegex);
    if (!match) return false;

    const day = parseInt(match[1], 10);
    const month = parseInt(match[2], 10) - 1;
    const year = parseInt(match[3], 10);

    const selectedDate = new Date(year, month, day);
    const today = new Date();
    const tomorrow = new Date(today);
    // Ensure 'tomorrow' is actually next day
    tomorrow.setDate(today.getDate() + 1);
    
    // Reset time for comparison
    today.setHours(0, 0, 0, 0);
    tomorrow.setHours(0, 0, 0, 0);
    selectedDate.setHours(0, 0, 0, 0);

    // Only today or tomorrow are valid (matches calendar availability)
    const valid = (
        selectedDate.getTime() === today.getTime() ||
        selectedDate.getTime() === tomorrow.getTime()
    );
    // Update dataset.valid to reflect validation state
    try {
        const input = document.getElementById('delivery-date');
        if (input) input.dataset.valid = valid ? 'true' : 'false';
    } catch (e) {}
    return valid;
}

function validateDeliveryMethodField(value) {
    return value === 'courier' || value === 'pickup';
}

function validateCityField(value) {
    if (!value || value.trim() === '') return false;
    // Allow all Cyrillic and Latin letters, spaces, hyphens for city names
    const cityRegex = /^[\p{Script=Latin}\p{Script=Cyrillic}\s\-]+$/u;
    return cityRegex.test(value.trim());
}

function validateAddressField(value) {
    if (!value || value.trim() === '') return false;
    // Allow: Cyrillic/Latin letters, numbers, spaces, hyphens, commas, dots, slash, #, №, parentheses
    const addressRegex = /^[\p{Script=Latin}\p{Script=Cyrillic}\p{N}\s\-\.,\/#№()]+$/u;
    return addressRegex.test(value.trim());
}

function validatePickupAddressField(value) {
    // Fix: Ensure proper validation for pickup address
    if (!value || value.trim() === '') {
        console.log('❌ pickupAddress validation FAILED - empty value');
        return false;
    }
    return true;
}

function validatePaymentMethodField(value) {
    return value && value.trim() !== '';
}

function validateOrderForm(orderDetails) {
    
    const validationOrder = [
        { 
            field: 'lastName', 
            label: 'фамилию', 
            element: 'last-name',
            customValidation: validateNameField
        },
        { 
            field: 'firstName', 
            label: 'имя', 
            element: 'first-name',
            customValidation: validateNameField
        },
        { 
            field: 'middleName', 
            label: 'отчество', 
            element: 'middle-name',
            customValidation: validateNameField
        },
        { 
            field: 'phoneNumber', 
            label: 'номер телефона', 
            element: 'phone-number',
            customValidation: validatePhoneField
        },
        { 
            field: 'email', 
            label: 'Email', 
            element: 'email',
            customValidation: validateEmailField
        },
        { 
            field: 'deliveryDate', 
            label: 'дату доставки/самовывоза', 
            element: 'delivery-date',
            customValidation: validateDeliveryDateField
        },
        { 
            field: 'deliveryMethod', 
            label: 'способ получения', 
            element: 'delivery-courier-radio',  // This will be handled specially for radio groups
            elementType: 'radio',  // Add type to handle radio buttons specially
            customValidation: validateDeliveryMethodField
        },
        // Conditional fields based on delivery method
        { 
            field: 'city', 
            label: 'город для доставки', 
            element: 'city', 
            condition: () => orderDetails.deliveryMethod === 'courier',
            customValidation: validateCityField
        },
        { 
            field: 'addressLine', 
            label: 'адрес доставки', 
            element: 'address-line', 
            condition: () => orderDetails.deliveryMethod === 'courier',
            customValidation: validateAddressField
        },
        { 
            field: 'paymentMethod', 
            label: 'способ оплаты', 
            element: 'payment-cash-radio',  // Use first radio button ID for focus
            elementType: 'radio',  // Mark as radio group
            errorElement: 'payment-method-section',  // Container for error styling
            condition: () => orderDetails.deliveryMethod === 'courier',
            customValidation: validatePaymentMethodField
        },
        { 
            field: 'pickupAddress', 
            label: 'адрес самовывоза', 
            element: 'pickup_1',  // Use first radio button ID for focus
            elementType: 'radio',  // Mark as radio group
            errorElement: 'pickup-radio-group',  // Container for error styling
            condition: () => orderDetails.deliveryMethod === 'pickup',
            customValidation: validatePickupAddressField
        },
        { 
            field: 'paymentMethodPickup', 
            label: 'способ оплаты', 
            element: 'payment-erip-radio-pickup',  // Use first radio button ID for focus
            elementType: 'radio',  // Mark as radio group
            errorElement: 'payment-method-section-pickup',  // Container for error styling
            condition: () => orderDetails.deliveryMethod === 'pickup',
            customValidation: validatePaymentMethodField
        }
    ];

    const errors = [];
    const errorFields = [];

    console.log('🔍 === VALIDATION STARTING ===');
    console.log('OrderDetails received:', orderDetails);

    for (const validation of validationOrder) {
        const value = orderDetails[validation.field];
        console.log(`🔍 Validating field '${validation.field}' with value: '${value}'`);
        
        // Check if field should be validated based on condition
        if (validation.condition && !validation.condition()) {
            console.log(`⏭️ Skipping ${validation.field} - condition not met`);
            continue;
        }

        // Perform validation using unified custom validation
        const isValid = validateField(value, validation);
        
        if (!isValid) {
            // For radio groups, handle element reference specially
            let elementRef = document.getElementById(validation.element);
            let errorContainer = null;
            
            if (validation.elementType === 'radio' && validation.errorElement) {
                // For radio groups, get the container for error styling
                errorContainer = document.getElementById(validation.errorElement);
                // But use the first radio for focus
                if (!elementRef) {
                    // Fallback: find first radio in group if specified element not found
                    const radioName = validation.field === 'deliveryMethod' ? 'deliveryMethod' :
                                     validation.field === 'paymentMethod' ? 'paymentMethod' :
                                     validation.field === 'pickupAddress' ? 'pickupAddress' :
                                     validation.field === 'paymentMethodPickup' ? 'paymentMethodPickup' : null;
                    if (radioName) {
                        elementRef = document.querySelector(`input[name="${radioName}"]`);
                    }
                }
            }
            
            console.log(`❌ Validation failed for ${validation.field}`);
            console.log(`   - Looking for element with ID: '${validation.element}'`);
            console.log(`   - Element found: ${elementRef ? 'YES' : 'NO'}`);
            if (elementRef) {
                console.log(`   - Element type: ${elementRef.tagName}`);
                console.log(`   - Element value: ${elementRef.value || 'N/A'}`);
            }
            if (errorContainer) {
                console.log(`   - Error container found: ${errorContainer ? 'YES' : 'NO'}`);
            }
            
            errors.push(`Пожалуйста, введите ${validation.label}.`);
            errorFields.push({ 
                field: validation.field, 
                element: elementRef,
                errorContainer: errorContainer,  // Add container for error styling
                elementType: validation.elementType  // Pass type for special handling
            });
        }
    }

    if (errors.length > 0) {
        console.log('❌ === VALIDATION FAILED ===');
        console.log('📝 Error fields:', errorFields.map(f => f.field));
        console.log('📝 Error messages:', errors);
    }

    return { isValid: errors.length === 0, errors, errorFields };
}

function collectFormData() {
    // Unified approach: Always collect from actual DOM elements
    // This ensures we get the current values regardless of caching or timing
    const orderDetails = {
        lastName: document.getElementById('last-name')?.value || '',
        firstName: document.getElementById('first-name')?.value || '',
        middleName: document.getElementById('middle-name')?.value || '',
        phoneNumber: document.getElementById('phone-number')?.value || '',
        email: document.getElementById('email')?.value || '',
        deliveryDate: document.getElementById('delivery-date')?.value || '',
        deliveryMethod: document.querySelector('input[name="deliveryMethod"]:checked')?.value || '',
        city: document.getElementById('city')?.value || '',
        addressLine: document.getElementById('address-line')?.value || '',
        pickupAddress: document.querySelector('input[name="pickupAddress"]:checked')?.value || '',
        paymentMethod: document.querySelector('input[name="paymentMethod"]:checked')?.value || '',
        paymentMethodPickup: document.querySelector('input[name="paymentMethodPickup"]:checked')?.value || '',
        commentDelivery: document.getElementById('comment-delivery')?.value || '',
        commentPickup: document.getElementById('comment-pickup')?.value || ''
    };
    
    return orderDetails;
}

// ===== END UNIFIED FORM VALIDATION SYSTEM =====

// Оборачиваем весь основной код в обработчик DOMContentLoaded
document.addEventListener('DOMContentLoaded', async () => {

    // Debug flag to control noisy logs and debug globals
    const DEBUG = true;
    if (!DEBUG && typeof console !== 'undefined' && console.log) {
        console.log = function(){};
    }

    // One-time Service Worker unregister (cleanup legacy sw.js caches)
    async function unregisterServiceWorkersOnce() {
        try {
            const flagKey = 'sw_unregistered_once';
            if (!('serviceWorker' in navigator)) return;
            if (localStorage.getItem(flagKey) === '1') return;
            const regs = await navigator.serviceWorker.getRegistrations();
            regs.forEach(reg => reg.unregister());
            localStorage.setItem(flagKey, '1');
            console.log('🧹 Service workers unregistered (one-time)');
        } catch (e) {
            console.warn('SW unregister failed:', e);
        }
    }

    // iOS-only emergency asset cache bust (adds &_=<timestamp> to CSS/JS)
    function iosHardBustAssetsOnce() {
        try {
            const bustFlag = 'ios_hard_bust_done_v1';
            // iOS detection (same logic as below but available earlier)
            const isIOSRuntime = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
                (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
            if (!isIOSRuntime) return;
            if (sessionStorage.getItem(bustFlag) === '1') return;

            const stamp = Date.now();
            // Bust stylesheets
            document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                const href = link.getAttribute('href');
                if (!href) return;
                const newHref = href + (href.includes('?') ? '&' : '?') + '_=' + stamp;
                link.setAttribute('href', newHref);
            });
            // Bust any additional script tags (JS already running won't re-execute)
            document.querySelectorAll('script[src]').forEach(script => {
                const src = script.getAttribute('src');
                if (!src) return;
                // Skip the currently executing main script to avoid double execution
                if (src.includes('/bot-app/script.js')) return;
                const newSrc = src + (src.includes('?') ? '&' : '?') + '_=' + stamp;
                script.setAttribute('src', newSrc);
            });
            sessionStorage.setItem(bustFlag, '1');
            console.log('🧨 iOS hard bust applied');
        } catch (e) {
            console.warn('iOS hard bust failed:', e);
        }
    }

    // Run early to maximize effect
    unregisterServiceWorkersOnce();
    iosHardBustAssetsOnce();

    const mainPageContainer = document.getElementById('main-page-container');
    const welcomeContainer = document.getElementById('welcome-container');
    const categoriesContainer = document.getElementById('categories-container');
    const productsContainer = document.getElementById('products-container');
    const cartContainer = document.getElementById('cart-container');
    const checkoutContainer = document.getElementById('checkout-container');
    const productScreen = document.getElementById('product-screen');
    const mainCategoryTitle = document.getElementById('main-category-title');
    const loadingLogoContainer = document.getElementById('loading-logo-container');

    const courierInfoText = document.getElementById('courier-text');
    const pickupInfoText = document.getElementById('pickup-text');
    const courierDeliveryFields = document.getElementById('courier-delivery-fields');
    const pickupAddresses = document.getElementById('pickup-addresses');

    const cartItemsList = document.getElementById('cart-items-list');
    const cartTotalElement = document.getElementById('cart-total');
    const productListElement = document.getElementById('product-list');
    const checkoutForm = document.getElementById('checkout-form');
    const deliveryMethodRadios = document.querySelectorAll('input[name="deliveryMethod"]');
    const checkoutTotalElement = document.getElementById('cart-total');
    const checkoutItemsList = document.getElementById('checkout-items-list');

    const continueShoppingButton = document.getElementById('continue-shopping-button');
    const startShoppingButton = document.getElementById('start-shopping-button');

    let cart = loadCartWithExpiration();
    let productsData = {};
    let isSubmitting = false; // Флаг для предотвращения двойной отправки
    let currentProductCategory = null; // Для отслеживания категории продукта

    const CATEGORY_DISPLAY_MAP = {
        "category_bakery": { name: "Выпечка", icon: "images/bakery.svg?v=1.3.96&t=1756283401", image: "images/bakery.svg?v=1.3.96&t=1756283401" },
        "category_croissants": { name: "Круассаны", icon: "images/crouasan.svg?v=1.3.96&t=1756283401", image: "images/crouasan.svg?v=1.3.96&t=1756283401" },
        "category_artisan_bread": { name: "Ремесленный хлеб", icon: "images/bread1.svg?v=1.3.96&t=1756283401", image: "images/bread1.svg?v=1.3.96&t=1756283401" },
        "category_desserts": { name: "Десерты", icon: "images/cookie.svg?v=1.3.96&t=1756283401", image: "images/cookie.svg?v=1.3.96&t=1756283401" }
    };

    await fetchProductsData();
    
    // 🔄 SETUP AUTOMATIC CART REFRESH EVERY MINUTE
    let autoRefreshInterval;
    
    // Function to check if app is active and refresh cart if needed
    function setupAutoRefresh() {
        // Clear existing interval if any
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
        
        // Set up periodic refresh every minute (60000ms)
        autoRefreshInterval = setInterval(async () => {
            // Only refresh if app is active
            if (!document.hidden) {
                try {
                    console.log('🔄 Auto-refreshing products data...');
                    await fetchProductsData();
                    
                    // 🔄 REFRESH PRODUCT GRID IF ON CATEGORY SCREEN
                    const productsContainer = document.getElementById('products-container');
                    if (productsContainer && !productsContainer.classList.contains('hidden')) {
                        // User is on a category screen, refresh the product grid
                        const currentCategory = localStorage.getItem('lastProductCategory');
                        if (currentCategory) {
                            console.log('🔄 Refreshing product grid for category:', currentCategory);
                            await loadProducts(currentCategory);
                        }
                    }
                } catch (error) {
                    console.warn('Auto-refresh failed:', error);
                }
            }
        }, 60000); // 1 minute
        
        console.log('✅ Auto-refresh setup: Cart will refresh every minute when active');
    }
    
    // Initialize auto-refresh
    setupAutoRefresh();
    
    // Handle page visibility changes to pause/resume auto-refresh
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            console.log('📱 App hidden, pausing auto-refresh');
        } else {
            console.log('📱 App visible, resuming auto-refresh');
            setupAutoRefresh(); // Restart interval when app becomes visible
        }
    });
    
    // Initialize cache management system
    await initializeCacheManagement();
    
    // Check cart expiration on app start
    const cartExpired = checkCartExpiration();
    if (cartExpired) {
        cart = {};
        console.log('⏰ Expired cart cleared on app start');
    }
    
    // Only initialize cart rendering after products data is loaded
    renderCart();
    

    
    // Initialize icons (no-op placeholder)
    // initializeIcons(); // removed: icon system disabled

    // Helper function to ensure screen scrolls to top
    function scrollToTop() {
        // Multiple methods to ensure scroll to top works in all contexts
        try {
            // Method 1: Standard scrollTo
            window.scrollTo(0, 0);
            
            // Method 2: Scroll to top of body
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
            
            // Method 3: Scroll to top of main container
            const mainContainer = document.getElementById('main-page-container');
            if (mainContainer) {
                mainContainer.scrollTop = 0;
            }
            
            // Method 4: Scroll to top of specific containers
            const categoriesContainer = document.getElementById('categories-container');
            if (categoriesContainer) {
                categoriesContainer.scrollTop = 0;
            }
            
            const productsContainer = document.getElementById('products-container');
            if (productsContainer) {
                productsContainer.scrollTop = 0;
            }
            
            const cartContainer = document.getElementById('cart-container');
            if (cartContainer) {
                cartContainer.scrollTop = 0;
            }
            
            const checkoutContainer = document.getElementById('checkout-container');
            if (checkoutContainer) {
                checkoutContainer.scrollTop = 0;
            }
            
            // Method 5: Force scroll after a small delay
            setTimeout(() => {
                window.scrollTo(0, 0);
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
            }, 100);
            
            // Method 6: Additional scroll reset for cart view
            setTimeout(() => {
                window.scrollTo(0, 0);
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
                if (mainContainer) mainContainer.scrollTop = 0;
                if (cartContainer) cartContainer.scrollTop = 0;
            }, 200);
            
            console.log('🔧 Scroll to top executed');
        } catch (error) {
            console.error('❌ Error during scroll to top:', error);
        }
    }

    function displayView(viewName, categoryKey = null) {
        // Prevent multiple simultaneous view changes
        if (window.isChangingView) {
            console.log('View change already in progress, skipping...');
            return;
        }
        window.isChangingView = true;

        // Hide all views first
        if (welcomeContainer) welcomeContainer.classList.add('hidden');
        if (categoriesContainer) categoriesContainer.classList.add('hidden');
        if (productsContainer) productsContainer.classList.add('hidden');
        if (cartContainer) cartContainer.classList.add('hidden');
        if (checkoutContainer) checkoutContainer.classList.add('hidden');
        if (productScreen) productScreen.classList.add('hidden');
        if (mainCategoryTitle) {
            mainCategoryTitle.classList.add('hidden');
            // Keep loading text hidden by default
            if (mainCategoryTitle.textContent === 'Загрузка...') {
                mainCategoryTitle.classList.add('hidden');
            }
        }
        if (loadingLogoContainer) loadingLogoContainer.classList.add('hidden');

        if (viewName === 'welcome' || viewName === 'categories') {
            Telegram.WebApp.BackButton.hide();
        } else {
            Telegram.WebApp.BackButton.show();
        }

        // Mobile-optimized view switching
        const showView = () => {
            switch (viewName) {
                case 'loading':
                    const loadingOverlay = document.getElementById('loading-overlay');
                    if (loadingOverlay) loadingOverlay.classList.remove('hidden');
                    if (mainCategoryTitle) mainCategoryTitle.classList.add('hidden');
                    // Hide all Telegram Web App buttons during loading
                    if (Telegram.WebApp.MainButton) {
                        Telegram.WebApp.MainButton.hide();
                    }
                    if (Telegram.WebApp.BackButton) {
                        Telegram.WebApp.BackButton.hide();
                    }
                    break;
                case 'welcome':
                    if (welcomeContainer) {
                        welcomeContainer.classList.remove('hidden');
                        if (isAndroidDevice) welcomeContainer.style.display = 'block';
                    }
                    if (mainPageContainer) {
                        mainPageContainer.classList.add('hidden');
                        if (isAndroidDevice) mainPageContainer.style.display = 'none';
                    }
                    Telegram.WebApp.MainButton.hide();
                    // Scroll to top of the page when welcome view is displayed
                    scrollToTop();
                    break;
                case 'categories':
                    if (mainPageContainer) {
                        mainPageContainer.classList.remove('hidden');
                        if (isAndroidDevice) mainPageContainer.style.display = 'block';
                    }
                    if (categoriesContainer) categoriesContainer.classList.remove('hidden');
                    if (mainCategoryTitle) {
                        mainCategoryTitle.textContent = 'Наше меню';
                        mainCategoryTitle.classList.remove('hidden');
                    }
                    // Load categories immediately for mobile to prevent twitching
                    loadCategories();
                    // Show basket button for categories view
                    if (Telegram.WebApp.MainButton) {
                        updateMainButtonCartInfo();
                    }
                    // Scroll to top of the page when categories view is displayed
                    scrollToTop();
                    break;
                case 'products':
                    if (mainPageContainer) {
                        mainPageContainer.classList.remove('hidden');
                        if (isAndroidDevice) mainPageContainer.style.display = 'block';
                    }
                    if (productsContainer) productsContainer.classList.remove('hidden');
                    if (mainCategoryTitle) mainCategoryTitle.classList.remove('hidden');
                    loadProducts(categoryKey);
                    // Show basket button for products view
                    if (Telegram.WebApp.MainButton) {
                        updateMainButtonCartInfo();
                    }
                    // Scroll to top of the page when products view is displayed
                    scrollToTop();
                    break;
                case 'product':
                    if (productScreen) productScreen.classList.remove('hidden');
                    Telegram.WebApp.MainButton.hide();
                    // Scroll to top of the page when product view is displayed
                    scrollToTop();
                    break;
                case 'cart':
                    if (mainPageContainer) {
                        mainPageContainer.classList.remove('hidden');
                        if (isAndroidDevice) mainPageContainer.style.display = 'block';
                    }
                    if (cartContainer) cartContainer.classList.remove('hidden');
                    if (mainCategoryTitle) {
                        mainCategoryTitle.textContent = 'Ваша корзина';
                        mainCategoryTitle.classList.remove('hidden');
                    }
                    renderCart();
                    Telegram.WebApp.MainButton.hide();
                    // Clear all form errors when switching to cart
                    clearAllErrors();
                    // Scroll to top of the page when cart view is displayed
                    // Add delay to ensure view is fully rendered before scrolling
                    setTimeout(() => {
                        scrollToTop();
                    }, 150);
                    break;
                case 'checkout':
                    if (mainPageContainer) {
                        mainPageContainer.classList.remove('hidden');
                        if (isAndroidDevice) mainPageContainer.style.display = 'block';
                    }
                    if (checkoutContainer) checkoutContainer.classList.remove('hidden');
                    if (mainCategoryTitle) {
                        mainCategoryTitle.textContent = 'Оформление заказа';
                        mainCategoryTitle.classList.remove('hidden');
                    }
                    renderCheckoutSummary();
                    setupDateInput();
                    updateSubmitButtonState();
                    
                    // Load and populate customer data if available
                    const customerData = loadCustomerDataWithExpiration();
                    if (Object.keys(customerData).length > 0) {
                        populateFormWithCustomerData(customerData);
                    }
                    
                    // Clear all form errors when switching to checkout
                    clearAllErrors();
                    
                    Telegram.WebApp.MainButton.hide();
                    // Scroll to top of the page when checkout view is displayed
                    scrollToTop();
                    break;
            }
            
            // Reset the flag after a short delay
            setTimeout(() => {
                window.isChangingView = false;
            }, isMobile ? 100 : 50);
        };

        // Use requestAnimationFrame for smoother transitions on mobile
        if (isMobile) {
            requestAnimationFrame(showView);
        } else {
            showView();
        }
    }

    Telegram.WebApp.BackButton.onClick(() => {
        const currentView = getCurrentView();
        if (currentView === 'products') {
            displayView('categories');
        } else if (currentView === 'product') {
            // Возвращаемся к списку продуктов в той же категории
            if (currentProductCategory) {
                displayView('products', currentProductCategory);
            } else {
                displayView('categories');
            }
        } else if (currentView === 'cart') {
            const lastProductCategory = localStorage.getItem('lastProductCategory');
            if (lastProductCategory) {
                displayView('products', lastProductCategory);
                localStorage.removeItem('lastProductCategory');
            } else {
                displayView('categories');
            }
        } else if (currentView === 'checkout') {
            displayView('cart');
        } else if (currentView === 'categories') {
            // Если мы на странице категорий, закрываем приложение
            Telegram.WebApp.close();
        } else {
            Telegram.WebApp.close();
        }
    });

    function getCurrentView() {
        if (welcomeContainer && !welcomeContainer.classList.contains('hidden')) return 'welcome';
        if (categoriesContainer && !categoriesContainer.classList.contains('hidden')) return 'categories';
        if (productsContainer && !productsContainer.classList.contains('hidden')) return 'products';
        if (productScreen && !productScreen.classList.contains('hidden')) return 'product';
        if (cartContainer && !cartContainer.classList.contains('hidden')) return 'cart';
        if (checkoutContainer && !checkoutContainer.classList.contains('hidden')) return 'checkout';
        return null;
    }

    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        const results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    async function fetchProductsData() {
        try {
            const response = await fetch('/bot-app/api/products');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            productsData = data;
            
            // 🔄 AUTO-REFRESH CART WHEN PRODUCTS CHANGE
            if (Object.keys(cart).length > 0) {
                renderCart();
            }
        } catch (error) {
            console.error('Ошибка при загрузке данных о продуктах:', error);
            console.error('Failed to load products data. Please try again later.');
        }
    }

    async function loadCategories() {
        try {
            const response = await fetch('/bot-app/api/categories');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const categoriesData = await response.json();

            if (categoriesContainer) categoriesContainer.innerHTML = '';

            const categoriesGrid = document.createElement('div');
            categoriesGrid.className = 'categories-grid';

            categoriesData.forEach(category => {
                const categoryInfo = CATEGORY_DISPLAY_MAP[category.key] || { name: category.key, icon: '' };
                const categoryDisplayName = categoryInfo.name;
                const categoryIcon = categoryInfo.icon;

                const categoryImageUrl = (productsData[category.key] && productsData[category.key].length > 0)
                    ? productsData[category.key][0].image_url
                    : 'https://placehold.co/300x200/cccccc/333333?text=No+Image';

                const categoryCard = document.createElement('div');
                categoryCard.className = 'category-card-item';
                categoryCard.dataset.categoryKey = category.key;

                categoryCard.innerHTML = `
                    <img src="${categoryImageUrl}"
                         alt="${categoryDisplayName}"
                         class="category-image"
                         onerror="this.onerror=null;this.src='https://placehold.co/300x200/cccccc/333333?text=No+Image';">
                    <div class="category-text-wrapper">
                        <h3 class="category-title-text">${categoryDisplayName}</h3>
                        <div class="category-link-text">
                            <span>перейти в каталог</span>
                            <svg class="category-arrow-svg" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M10.707 2.293a1 1 0 010 1.414L6.414 8l4.293 4.293a1 1 0 01-1.414 1.414l-5-5a1 1 0 010-1.414l5-5a1 1 0 011.414 0z" transform="rotate(180 8 8)"></path>
                            </svg>
                        </div>
                    </div>
                `;
                            categoryCard.addEventListener('click', () => {
                    displayView('products', category.key);
                    localStorage.setItem('lastProductCategory', category.key);
                });
                if (categoriesGrid) categoriesGrid.appendChild(categoryCard);
            });
            if (categoriesContainer) categoriesContainer.appendChild(categoriesGrid);
            
            // Hide loading logo after categories are loaded
            if (loadingLogoContainer) loadingLogoContainer.classList.add('hidden');
        } catch (error) {
            console.error('Ошибка при загрузке категорий:', error);
            console.error('Failed to load categories. Please try again later.');
        }
    }

    async function loadProducts(categoryKey) {
        if (!productsData[categoryKey]) {
            await fetchProductsData();
            if (!productsData[categoryKey]) {
                console.warn('No products found for this category.');
                displayView('categories');
                return;
            }
        }

        const products = productsData[categoryKey];
        
        // Update category title with icon for category screens (not main menu)
        if (mainCategoryTitle) {
            const categoryInfo = CATEGORY_DISPLAY_MAP[categoryKey];
            if (categoryInfo && categoryInfo.image) {
                // Create icon + title container
                mainCategoryTitle.innerHTML = `
                    <div class="category-title-with-icon">
                        <img src="${categoryInfo.image}" alt="${categoryInfo.name}" class="category-icon" onerror="this.style.display='none';">
                        <span>${categoryInfo.name}</span>
                    </div>
                `;
            } else {
                mainCategoryTitle.textContent = 'Продукты';
            }
        }
        if (productListElement) productListElement.innerHTML = '';

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.dataset.productId = product.id;

            const quantityInCart = cart[product.id] ? cart[product.id].quantity : 0;

            productCard.innerHTML = `
                <div class="product-image-container">
                    <img src="${product.image_url || 'https://placehold.co/300x225/e0e0e0/555?text=Нет+фото'}" 
                         alt="${product.name}" 
                         class="product-image clickable-image" 
                         data-product-id="${product.id}"
                         loading="lazy" decoding="async"
                         onerror="this.onerror=null;this.src='https://placehold.co/300x225/e0e0e0/555?text=Нет+фото';">
                    <div class="product-vegan-icon" style="display: ${product.for_vegans && product.for_vegans !== 'N/A' ? 'block' : 'none'};">
                        <svg class="svg svg-vegan">
                            <use xlink:href="sprite.svg#vegan"></use>
                        </svg>
                    </div>
                </div>
                <div class="product-info">
                    <div class="product-name">
                        ${product.name}
                        ${product.availability_days && product.availability_days !== 'N/A' ? 
                            `<span class="availability-info"> (${product.availability_days})</span>` : ''}
                    </div>
                    <span class="details-text" data-product-id="${product.id}">Подробнее</span>
                    <div class="product-bottom-row">
                        <div class="product-weight">
                            ${product.weight && product.weight !== 'N/A' ? `${product.weight} гр.` : ''}
                        </div>
                        <div class="product-controls">
                            <div class="product-price">${parseFloat(product.price).toFixed(2)} р.</div>
                            <div class="quantity-controls">
                                <button data-product-id="${product.id}" data-action="decrease">-</button>
                                <span class="quantity-display" id="qty-${product.id}">${quantityInCart}</span>
                                <button data-product-id="${product.id}" data-action="increase">+</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            if (productListElement) productListElement.appendChild(productCard);
        });

        // Добавляем обработчики событий для кнопок +/-
        if (productListElement) {
            productListElement.querySelectorAll('.quantity-controls button').forEach(button => {
                button.addEventListener('click', (e) => {
                    const clickedButton = e.target.closest('button[data-product-id]');
                    if (!clickedButton) {
                        console.error('ОЧЕНЬ ВАЖНО: Кнопка управления количеством не найдена или не имеет data-product-id. e.target:', e.target);
                        return;
                    }
                    const productId = clickedButton.dataset.productId;
                    const action = clickedButton.dataset.action;

                    if (action === 'increase') {
                        updateProductQuantity(productId, 1);
                    } else if (action === 'decrease') {
                        updateProductQuantity(productId, -1);
                    }
                });
            });

            // Добавляем обработчики событий для текста "Подробнее"
            productListElement.querySelectorAll('.details-text').forEach(text => {
                text.addEventListener('click', (e) => {
                    const productId = e.target.dataset.productId;
                    showProductScreen(productId, categoryKey);
                });
            });

            // Добавляем обработчики событий для кликабельных изображений
            productListElement.querySelectorAll('.clickable-image').forEach(image => {
                image.addEventListener('click', (e) => {
                    const productId = e.target.dataset.productId;
                    showProductScreen(productId, categoryKey);
                });
            });

            // Добавляем обработчики событий для названий продуктов
            productListElement.querySelectorAll('.product-name').forEach(productName => {
                productName.addEventListener('click', (e) => {
                    // Не обрабатываем клик если он на availability-info
                    if (e.target.classList.contains('availability-info')) {
                        return;
                    }
                    const productCard = e.target.closest('.product-card');
                    if (productCard) {
                        const productId = productCard.dataset.productId;
                        showProductScreen(productId, categoryKey);
                    }
                });
            });
            
            // Hide loading logo after products are loaded
            if (loadingLogoContainer) loadingLogoContainer.classList.add('hidden');
        }
    }

    function updateProductQuantity(productId, change) {
        let product = null;
        for (const catKey in productsData) {
            product = productsData[catKey].find(p => p.id === productId);
            if (product) break;
        }

        if (!product) {
            console.error('Продукт не найден:', productId);
            return;
        }

        if (!cart[productId]) {
            cart[productId] = { ...product, quantity: 0 };
        }

        cart[productId].quantity += change;

        if (cart[productId].quantity <= 0) {
            delete cart[productId];
        }

        saveCartWithMetadata(cart);
        updateProductCardUI(productId);
        updateMainButtonCartInfo();
    }

    function updateProductCardUI(productId) {
        const quantitySpan = document.getElementById(`qty-${productId}`);
        if (quantitySpan) {
            const currentQuantity = cart[productId] ? cart[productId].quantity : 0;
            quantitySpan.textContent = currentQuantity;
        }
        
        // Also update product screen counter if it exists
        const productScreenCounter = document.getElementById(`screen-quantity-${productId}`);
        if (productScreenCounter) {
            const currentQuantity = cart[productId] ? cart[productId].quantity : 0;
            productScreenCounter.value = currentQuantity;
        }
        
        if (cartContainer && !cartContainer.classList.contains('hidden')) {
            renderCart();
        }
    }


    function renderCart() {
        if (cartItemsList) cartItemsList.innerHTML = '';
        let total = 0;

        const cartItems = Object.values(cart);
        if (cartItems.length === 0) {
            if (cartItemsList) cartItemsList.innerHTML = '<p class="empty-cart-message">Ваша корзина пуста.</p>';
            if (cartTotalElement) cartTotalElement.textContent = 'Общая сумма: 0.00 р.';
            
            // Скрываем cart-summary-row когда корзина пуста
            const cartSummaryRow = document.querySelector('.cart-summary-row');
            if (cartSummaryRow) cartSummaryRow.classList.add('hidden');
            
            const cartActionsBottom = document.querySelector('.cart-actions-bottom');
            if (cartActionsBottom) cartActionsBottom.classList.add('hidden');
            if (continueShoppingButton) continueShoppingButton.classList.add('hidden');

            // Показываем кнопку "Наше меню" для пустой корзины
            const emptyCartMenuButton = document.getElementById('empty-cart-menu-button');
            if (emptyCartMenuButton) emptyCartMenuButton.classList.remove('hidden');
            
            // Удаляем контейнер с информацией об условиях реализации продуктов когда корзина пуста
            renderAvailabilityInfo(cartItems);
            return;
        } else {
            // Показываем cart-summary-row когда в корзине есть товары
            const cartSummaryRow = document.querySelector('.cart-summary-row');
            if (cartSummaryRow) cartSummaryRow.classList.remove('hidden');
            
            const cartActionsBottom = document.querySelector('.cart-actions-bottom');
            if (cartActionsBottom) cartActionsBottom.classList.remove('hidden');
            if (continueShoppingButton) continueShoppingButton.classList.remove('hidden');

            // Скрываем кнопку "Наше меню" когда в корзине есть товары
            const emptyCartMenuButton = document.getElementById('empty-cart-menu-button');
            if (emptyCartMenuButton) emptyCartMenuButton.classList.add('hidden');
        }

        cartItems.forEach(item => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            // Check if product is still available
            const isAvailable = isProductAvailable(item.id);

            // Find the category for this product to pass to showProductScreen
            let productCategory = null;
            for (const catKey in productsData) {
                if (productsData[catKey].find(p => p.id === item.id)) {
                    productCategory = catKey;
                    break;
                }
            }

            const cartItemElement = document.createElement('div');
            cartItemElement.className = `cart-item ${!isAvailable ? 'disabled-product' : ''}`;
            cartItemElement.dataset.productId = item.id;

            cartItemElement.innerHTML = `
                <div class="cart-item-image-container" 
                     style="cursor: ${isAvailable ? 'pointer' : 'default'};" 
                     onclick="${isAvailable ? `showProductScreen('${item.id}', '${productCategory}')` : 'return false;'}">
                    <img src="${item.image_url || 'https://placehold.co/80x80/cccccc/333333?text=No+Image'}" 
                         alt="${item.name}" class="cart-item-image"
                         onerror="this.onerror=null;this.src='https://placehold.co/80x80/cccccc/333333?text=No+Image';">
                    ${!isAvailable ? '<div class="unavailable-label">Недоступен</div>' : ''}
                </div>
                <div class="cart-item-details">
                    <h4 class="cart-item-name" 
                        style="cursor: ${isAvailable ? 'pointer' : 'default'};" 
                        onclick="${isAvailable ? `showProductScreen('${item.id}', '${productCategory}')` : 'return false;'}">${item.name}</h4>
                    <p class="cart-item-price">
                        <span class="price-per-unit">${item.price} р. за шт.</span>
                        <span class="cart-item-total">${itemTotal.toFixed(2)} р.</span>
                    </p>
                    <div class="cart-item-controls">
                        <div class="input-group input-group-sm d-flex align-items-center justify-content-center justify-content-md-start">
                            <div class="changer count_minus cur-p pos-r w-200 w-xs-300 h-200 h-xs-300 br-50p d-flex align-items-center justify-content-center decrease-cart-quantity" 
                                 data-product-id="${item.id}" 
                                 style="background-color: #d7d7d7; ${!isAvailable ? 'opacity: 0.5; pointer-events: none;' : ''}">
                                <span class="fz-150 fw-400 fc-1 mb-25">-</span>
                            </div>
                            <input type="number" name="count" value="${item.quantity}" min="1" readonly="" 
                                   class="count mssaleprice-count cur-p form-control ptb-25 fz-175 mlr-50 text-center mx-w-300 cart-item-quantity" 
                                   style="border: none !important; background-color:transparent !important; ${!isAvailable ? 'opacity: 0.5;' : ''}">
                            <div class="changer count_plus cur-p pos-r w-200 w-xs-300 h-200 h-xs-300 br-50p d-flex align-items-center justify-content-center increase-cart-quantity" 
                                 data-product-id="${item.id}" 
                                 style="background-color: #d7d7d7; ${!isAvailable ? 'opacity: 0.5; pointer-events: none;' : ''}">
                                <span class="fz-150 fw-400 fc-1">+</span>
                            </div>
                        </div>
                        <button class="btn--noborder bgc-t fc-1 h-fc h-fc-acc-1 pr-0 remove-btn" data-product-id="${item.id}" type="button">
                            <svg class="svg svg-as_close fz-125">
                                <use xlink:href="#as_close"></use>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
            if (cartItemsList) cartItemsList.appendChild(cartItemElement);
        });

        if (cartTotalElement) cartTotalElement.textContent = `Общая сумма: ${total.toFixed(2)} р.`;

        // NEW: Check for disabled products and render error message
        const disabledProducts = getDisabledProducts(cartItems);
        
        // Добавляем контейнер с информацией об условиях реализации продуктов
        renderAvailabilityInfo(cartItems);
        
        // Render error message AFTER availability info
        renderDisabledProductsError(disabledProducts);
        updateCheckoutButtonState(disabledProducts);

        // Добавляем обработчики для кнопок в корзине
        if (cartItemsList) {
            cartItemsList.querySelectorAll('.increase-cart-quantity').forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    updateProductQuantity(e.currentTarget.dataset.productId, 1);
                });
            });
            cartItemsList.querySelectorAll('.decrease-cart-quantity').forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    updateProductQuantity(e.currentTarget.dataset.productId, -1);
                });
            });
            cartItemsList.querySelectorAll('.remove-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    const productId = e.currentTarget.dataset.productId;
                    delete cart[productId];
                    saveCartWithMetadata(cart);
                    renderCart();
                    updateMainButtonCartInfo();
                });
            });
        }
        const clearCartButton = document.getElementById('clear-cart-button');
        if (clearCartButton) {
            clearCartButton.addEventListener('click', clearCart);
        } else {
            console.error('Элемент с ID "clear-cart-button" не найден в DOM. Невозможно прикрепить слушатель кликов.');
        }

        const checkoutButton = document.getElementById('checkout-button');
        if (checkoutButton) {
            checkoutButton.addEventListener('click', () => {
                if (Object.keys(cart).length === 0) {
                                    console.warn('Cart is empty. Add items to checkout.');
                    return;
                }
                displayView('checkout');
            });
        } else {
            console.error('Элемент с ID "checkout-button" не найден в DOM. Невозможно прикрепить слушатель кликов.');
        }
    }

    function getProductById(productId) {
        if (!productsData) return null;
        
        // Поиск продукта во всех категориях
        for (const category of Object.values(productsData)) {
            if (Array.isArray(category)) {
                const product = category.find(p => p.id === productId);
                if (product) return product;
            }
        }
        return null;
    }

    // NEW: Function to check if a product is still available in the catalog
    function isProductAvailable(productId) {
        const product = getProductById(productId);
        return product !== null;
    }

    // NEW: Function to get disabled products from cart
    function getDisabledProducts(cartItems) {
        return cartItems.filter(item => !isProductAvailable(item.id));
    }

    // NEW: Function to render disabled product error message
    function renderDisabledProductsError(disabledProducts) {
        console.log('🔍 Rendering disabled products error for:', disabledProducts.length, 'products');
        
        // Remove existing error message if it exists
        const existingError = document.getElementById('disabled-products-error');
        if (existingError) {
            existingError.remove();
        }

        if (disabledProducts.length === 0) {
            console.log('✅ No disabled products, no error message needed');
            return;
        }

        const errorContainer = document.createElement('div');
        errorContainer.id = 'disabled-products-error';
        errorContainer.className = 'disabled-products-error';
        errorContainer.innerHTML = `
            <div class="alert alert-danger d-flex align-items-center" role="alert">
                <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Danger:">
                    <use xlink:href="#exclamation-triangle-fill"/>
                </svg>
                <div>
                    Удалите недоступные товары из корзины
                </div>
            </div>
        `;

        // Insert error message between availability-info-container and cart-actions-bottom
        const availabilityInfoContainer = document.getElementById('availability-info-container');
        const cartActionsBottom = document.querySelector('.cart-actions-bottom');
        
        console.log('🔍 Availability info container:', availabilityInfoContainer);
        console.log('🔍 Cart actions bottom:', cartActionsBottom);
        
        if (availabilityInfoContainer && cartActionsBottom) {
            // Insert AFTER availability info (below it) and BEFORE cart actions
            availabilityInfoContainer.after(errorContainer);
            console.log('✅ Error message inserted after availability info');
        } else if (cartActionsBottom) {
            // Fallback: insert above cart actions if availability info doesn't exist
            cartActionsBottom.parentNode.insertBefore(errorContainer, cartActionsBottom);
            console.log('✅ Error message inserted above cart actions (fallback)');
        } else {
            console.error('❌ Could not find cart-actions-bottom element');
        }
    }

    // NEW: Function to update checkout button state
    function updateCheckoutButtonState(disabledProducts) {
        const checkoutButton = document.getElementById('checkout-button');
        if (checkoutButton) {
            if (disabledProducts.length > 0) {
                checkoutButton.disabled = true;
                checkoutButton.classList.add('disabled');
            } else {
                checkoutButton.disabled = false;
                checkoutButton.classList.remove('disabled');
            }
        }
    }

    function renderAvailabilityInfo(cartItems) {
        // Удаляем существующий контейнер если он есть
        const existingContainer = document.getElementById('availability-info-container');
        if (existingContainer) {
            existingContainer.remove();
        }

        // Находим продукты с особыми условиями реализации (availability_days не равно "N/A")
        const productsWithAvailability = cartItems.filter(item => {
            const product = getProductById(item.id);
            return product && product.availability_days && product.availability_days !== 'N/A' && product.availability_days.trim() !== '';
        });

        // Если есть продукты с особыми условиями, показываем контейнер
        if (productsWithAvailability.length > 0) {
            const container = document.createElement('div');
            container.id = 'availability-info-container';
            container.className = 'availability-info-container';
            
            let productsListHTML = '';
            productsWithAvailability.forEach(item => {
                const product = getProductById(item.id);
                if (product && product.availability_days) {
                    productsListHTML += `<li><strong>${product.name}:</strong> ${product.availability_days}</li>`;
                }
            });

            container.innerHTML = `
                <div class="availability-info-content">
                    <p class="availability-info-title">Обратите внимание, что некоторые из продуктов имеют особые условия реализации:</p>
                    <ul class="availability-info-list">
                        ${productsListHTML}
                    </ul>
                </div>
            `;

            // Вставляем контейнер после итоговой суммы, но перед кнопками действий (place order button)
            const cartActionsBottom = document.querySelector('.cart-actions-bottom');
            if (cartActionsBottom) {
                cartActionsBottom.parentNode.insertBefore(container, cartActionsBottom);
            }
        } else {
            // Явно удаляем контейнер если нет продуктов с особыми условиями
            const existingContainer = document.getElementById('availability-info-container');
            if (existingContainer) {
                existingContainer.remove();
            }
        }
    }

    function clearCart() {
        cart = {};
        localStorage.removeItem('cart');
        renderCart();
        updateMainButtonCartInfo();
        
        // 🔄 Refresh product grid and product screen to update availability
        const currentView = getCurrentView();
        if (currentView === 'products') {
            const currentCategory = localStorage.getItem('lastProductCategory');
            if (currentCategory) {
                console.log('🔄 Refreshing product grid after cart clear');
                loadProducts(currentCategory);
            }
        }
        
        console.log('🗑️ Cart cleared successfully');
    }

    // Manual cache clearing function for debugging/development
    async function clearAllCaches() {
        try {
            const success = await clearBrowserCache();
            if (success) {
                console.log('✅ All caches cleared successfully');
                // Optionally show user feedback
                if (typeof Telegram !== 'undefined' && Telegram.WebApp && Telegram.WebApp.showAlert) {
                    Telegram.WebApp.showAlert('Кеш очищен успешно!');
                }
            } else {
                console.error('❌ Failed to clear caches');
            }
        } catch (error) {
            console.error('❌ Error clearing caches:', error);
        }
    }

    // Cache status function for debugging
    async function getCacheStatus() {
        try {
            const status = {
                appVersion: CACHE_VERSION,
                storedVersion: localStorage.getItem('app_version'),
                cacheSupported: 'caches' in window,
                localStorageSize: JSON.stringify(localStorage).length,
                sessionStorageSize: JSON.stringify(sessionStorage).length,
                cartInfo: {
                    version: CART_DATA_VERSION,
                    expirationDays: CART_EXPIRATION_DAYS,
                    currentAge: getCartAge(),
                    itemCount: Object.keys(cart).length,
                    totalValue: Object.values(cart).reduce((sum, item) => sum + (item.price * item.quantity), 0)
                },
                serviceWorker: {
                    supported: false,
                    status: 'removed'
                }
            };
            
            if ('caches' in window) {
                const cacheNames = await caches.keys();
                status.cacheNames = cacheNames;
                status.cacheCount = cacheNames.length;
            }
            
            console.log('📊 Cache Status:', status);
            return status;
        } catch (error) {
            console.error('❌ Error getting cache status:', error);
            return null;
        }
    }

    function renderCheckoutSummary() {
        // Removed checkoutItemsList rendering (element not present in HTML)
        let total = 0;

        Object.values(cart).forEach(item => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            // No per-item list in checkout summary; UI shows only total and form
        });

        if (checkoutTotalElement) checkoutTotalElement.textContent = `${total.toFixed(2)} р.`;

        const selectedDeliveryMethod = document.querySelector('input[name="deliveryMethod"]:checked')?.value;
        toggleDeliveryFields(selectedDeliveryMethod);

        const backFromCheckoutToCartButton = document.getElementById('back-from-checkout-to-cart');
        if (backFromCheckoutToCartButton) {
            backFromCheckoutToCartButton.addEventListener('click', (event) => {
                event.preventDefault();
                // Clear all errors before navigating back
                clearAllErrors();
                // Force scroll to top immediately
                window.scrollTo(0, 0);
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
                displayView('cart');
            });
        } else {
            console.error('Элемент с ID "back-from-checkout-to-cart" не найден в DOM. Невозможно прикрепить слушатель кликов.');
        }

        console.log('🔍 === FORM INITIALIZATION DEBUG ===');
        console.log('🔍 checkoutForm element found:', !!checkoutForm);
        console.log('🔍 checkoutForm element:', checkoutForm);
        
        if (checkoutForm) {
            console.log('✅ Adding submit event listener to checkoutForm');
            checkoutForm.addEventListener('submit', (event) => {
                event.preventDefault();
                
                console.log('🚀 === PLACE ORDER BUTTON CLICKED ===');
                console.log('📅 Current timestamp:', new Date().toISOString());

                // Use unified form data collection
                const orderDetails = collectFormData();
                console.log('📋 === COLLECTED FORM DATA ===');
                console.log('orderDetails:', JSON.stringify(orderDetails, null, 2));
                console.log('firstName value:', orderDetails.firstName);
                console.log('lastName value:', orderDetails.lastName);
                console.log('middleName value:', orderDetails.middleName);
                console.log('phoneNumber value:', orderDetails.phoneNumber);
                console.log('email value:', orderDetails.email);
                
                // Keep pickup address ID as-is for backend processing
                // The backend _get_pickup_details function expects the numeric ID
                // No conversion needed here - backend will handle the mapping

                // Use unified validation system
                const validationResult = validateOrderForm(orderDetails);
                const { isValid, errors: errorMessages, errorFields } = validationResult;

                // Validation is already complete from validateOrderForm()
                // Just handle the validation result
                if (!isValid) {
                    console.log('❌ === FORM VALIDATION FAILED ===');
                    console.log('🎯 First error field that will get focus:', errorFields[0] ? errorFields[0].field : 'none');
                    console.log('🎯 First error field element:', errorFields[0] ? errorFields[0].element : 'none');
                    // Show errors and focus on first error field
                    showValidationErrors(errorFields, errorMessages);
                    return;
                }

                // Check minimum order amount (70.00) only for courier delivery
                const totalAmount = parseFloat(checkoutTotalElement.textContent.replace(' р.', ''));
                const courierRadio = document.getElementById('delivery-courier-radio');
                const isCourierSelected = courierRadio && courierRadio.checked;
                
                if (isCourierSelected && totalAmount < 70.00) {
                    console.error('Minimum order amount not met for courier delivery');
                    return;
                }

                // Get selected payment method
                let selectedPaymentMethod = '';
                if (orderDetails.deliveryMethod === 'courier') {
                    selectedPaymentMethod = orderDetails.paymentMethod || '';
                } else if (orderDetails.deliveryMethod === 'pickup') {
                    selectedPaymentMethod = orderDetails.paymentMethodPickup || '';
                }



                const orderPayload = {
                    action: 'checkout_order',
                    order_details: {
                        lastName: orderDetails.lastName,
                        firstName: orderDetails.firstName,
                        middleName: orderDetails.middleName,
                        phone: orderDetails.phoneNumber,
                        email: orderDetails.email,
                        deliveryDate: orderDetails.deliveryDate,
                        deliveryMethod: orderDetails.deliveryMethod,
                        city: orderDetails.city || '',
                        addressLine: orderDetails.addressLine || '',
                        comment: orderDetails.commentDelivery || '',
                        pickupAddress: orderDetails.pickupAddress || '',
                        commentPickup: orderDetails.commentPickup || '',
                        paymentMethod: selectedPaymentMethod
                    },
                    cart_items: Object.values(cart).map(item => ({
                        id: item.id,
                        name: item.name,
                        quantity: item.quantity,
                        price: item.price
                    })),
                    total_amount: parseFloat(checkoutTotalElement.textContent.replace(' р.', ''))
                };

                try {
                    console.log('Отправка заказа:', orderPayload);
                    Telegram.WebApp.sendData(JSON.stringify(orderPayload));
                    
                    // Save customer data for future prepopulation
                    const customerData = extractCustomerDataFromForm();
                    if (Object.keys(customerData).length > 0) {
                        saveCustomerDataWithMetadata(customerData);
                        console.log('💾 Customer data saved for future prepopulation');
                    }
                    
                    // Order sent successfully - close WebApp after delay to ensure data is sent
                    setTimeout(() => {
                        try {
                            if (Telegram.WebApp.close) {
                                Telegram.WebApp.close();
                                // Clear cart ONLY after WebApp closes successfully
                                clearCart();
                                console.log('✅ Cart cleared after successful order completion');
                            }
                        } catch (closeError) {
                            console.warn('Could not close WebApp automatically');
                        }
                    }, 2000);
                    
                } catch (error) {
                    console.error('Ошибка при отправке заказа:', error);
                    // Show error in console only - no popups
                }
            });
        } else {
            console.error('❌ Элемент с ID "checkout-form" не найден. Невозможно прикрепить слушатель отправки.');
        }
        
        // Submit button is handled by the form's submit event listener
        // No need for separate click handler to avoid double execution
        const submitButton = document.querySelector('.submit-order-button');
        if (submitButton) {
            console.log('✅ Submit button found, form submission handled by form submit event');
        } else {
            console.error('❌ Submit button not found');
        }
    }

    function toggleDeliveryFields(method) {
        if (courierDeliveryFields && pickupAddresses) {
            if (method === 'courier') {
                courierDeliveryFields.classList.remove('hidden');
                pickupAddresses.classList.add('hidden');
                document.getElementById('last-name').required = true;
                document.getElementById('first-name').required = true;
                document.getElementById('middle-name').required = true;
                document.getElementById('phone-number').required = true;
                document.getElementById('email').required = true;
                document.getElementById('delivery-date').required = true;
                document.getElementById('city').required = true;
                document.getElementById('address-line').required = true;
                document.querySelectorAll('input[name="pickupAddress"]').forEach(input => input.required = false);

                // Очищаем поля самовывоза при переключении на доставку курьером
                document.querySelectorAll('input[name="pickupAddress"]').forEach(input => input.checked = false);
                document.getElementById('comment-pickup').value = '';
                
                // Show courier payment methods, hide pickup payment methods
                const courierPaymentSection = document.getElementById('payment-method-section');
                const pickupPaymentSection = document.getElementById('payment-method-section-pickup');
                if (courierPaymentSection) courierPaymentSection.classList.remove('hidden');
                if (pickupPaymentSection) pickupPaymentSection.classList.add('hidden');
            } else if (method === 'pickup') {
                courierDeliveryFields.classList.add('hidden');
                pickupAddresses.classList.remove('hidden');
                document.getElementById('last-name').required = true;
                document.getElementById('first-name').required = true;
                document.getElementById('middle-name').required = true;
                document.getElementById('phone-number').required = true;
                document.getElementById('email').required = true;
                document.getElementById('delivery-date').required = true;
                document.getElementById('city').required = false;
                document.getElementById('address-line').required = false;
                document.querySelectorAll('input[name="pickupAddress"]').forEach(input => input.required = true);

                // Очищаем поля доставки курьером при переключении на самовывоз
                document.getElementById('city').value = '';
                document.getElementById('address-line').value = '';
                document.getElementById('comment-delivery').value = '';
                
                // Hide courier payment methods, show pickup payment methods
                const courierPaymentSection = document.getElementById('payment-method-section');
                const pickupPaymentSection = document.getElementById('payment-method-section-pickup');
                if (courierPaymentSection) courierPaymentSection.classList.add('hidden');
                if (pickupPaymentSection) pickupPaymentSection.classList.remove('hidden');
            } else {
                courierDeliveryFields.classList.add('hidden');
                pickupAddresses.classList.add('hidden');
                document.getElementById('last-name').required = false;
                document.getElementById('first-name').required = false;
                document.getElementById('middle-name').required = false;
                document.getElementById('phone-number').required = false;
                document.getElementById('email').required = false;
                document.getElementById('delivery-date').required = false;
                document.getElementById('city').required = false;
                document.getElementById('address-line').required = false;
                document.querySelectorAll('input[name="pickupAddress"]').forEach(input => input.required = false);
            }
        }

        if (courierInfoText && pickupInfoText) {
            if (method === 'courier') {
                courierInfoText.classList.remove('hidden');
                pickupInfoText.classList.add('hidden');
            } else if (method === 'pickup') {
                courierInfoText.classList.add('hidden');
                pickupInfoText.classList.remove('hidden');
            } else {
                courierInfoText.classList.add('hidden');
                pickupInfoText.classList.add('hidden');
            }
        }
    }

    if (deliveryMethodRadios.length > 0) {
        deliveryMethodRadios.forEach(radio => {
            radio.addEventListener('change', (event) => {
                // Remove selected class from all delivery method items
                document.querySelectorAll('.delivery-method-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // Add selected class to the current delivery method item
                const currentItem = event.target.closest('.delivery-method-item');
                if (currentItem) {
                    currentItem.classList.add('selected');
                }
                
                toggleDeliveryFields(event.target.value);
                updateSubmitButtonState();
            });
        });
        const initialSelectedMethod = document.querySelector('input[name="deliveryMethod"]:checked')?.value;
        toggleDeliveryFields(initialSelectedMethod);
        updateSubmitButtonState();
        
        // Set initial selected state for delivery method
        const initialSelectedRadio = document.querySelector('input[name="deliveryMethod"]:checked');
        if (initialSelectedRadio) {
            const initialItem = initialSelectedRadio.closest('.delivery-method-item');
            if (initialItem) {
                initialItem.classList.add('selected');
            }
        }
    } else {
        console.warn('Кнопки выбора способа доставки не найдены.');
    }

    // Add pickup address selection functionality
    const pickupAddressRadios = document.querySelectorAll('input[name="pickupAddress"]');
    if (pickupAddressRadios.length > 0) {
        pickupAddressRadios.forEach(radio => {
            radio.addEventListener('change', (event) => {
                // Remove selected class from all items
                document.querySelectorAll('.pickup-address-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // Add selected class to the current item
                const currentItem = event.target.closest('.pickup-address-item');
                if (currentItem) {
                    currentItem.classList.add('selected');
                }
                
                // Hide all pickup detail blocks
                document.querySelectorAll('.pickup-details').forEach(block => {
                    block.style.display = 'none';
                });
                
                // Show the selected pickup detail block
                const selectedValue = event.target.value;
                const detailBlock = document.getElementById(`pickup-block_${selectedValue}`);
                if (detailBlock) {
                    detailBlock.style.display = 'block';
                }
            });
        });
        
            // Add click handlers for the entire pickup address item
    const pickupAddressItems = document.querySelectorAll('.pickup-address-item');
    pickupAddressItems.forEach(item => {
        item.addEventListener('click', (event) => {
            const radio = item.querySelector('input[type="radio"]');
            if (radio && !event.target.matches('input[type="radio"]')) {
                radio.checked = true;
                radio.dispatchEvent(new Event('change'));
            }
        });
    });
    
    // Add click handlers for delivery method items
    const deliveryMethodItems = document.querySelectorAll('.delivery-method-item');
    deliveryMethodItems.forEach(item => {
        item.addEventListener('click', (event) => {
            const radio = item.querySelector('input[type="radio"]');
            if (radio && !event.target.matches('input[type="radio"]')) {
                radio.checked = true;
                radio.dispatchEvent(new Event('change'));
            }
        });
    });
    
    // Add payment method functionality
    const paymentMethodRadios = document.querySelectorAll('input[name="paymentMethod"]');
    if (paymentMethodRadios.length > 0) {
        paymentMethodRadios.forEach(radio => {
            radio.addEventListener('change', (event) => {
                // Remove selected class from all payment method items
                document.querySelectorAll('.payment-method-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // Add selected class to the current payment method item
                const currentItem = event.target.closest('.payment-method-item');
                if (currentItem) {
                    currentItem.classList.add('selected');
                }
                
                // Clear payment method error when user makes a selection
                clearFieldError('paymentMethod');
            });
        });
        
        // No initial selection for courier delivery payment methods
        // They will be selected by user choice
    }
    
    // Add click handlers for payment method items
    const paymentMethodItems = document.querySelectorAll('.payment-method-item');
    paymentMethodItems.forEach(item => {
        item.addEventListener('click', (event) => {
            const radio = item.querySelector('input[type="radio"]');
            if (radio && !event.target.matches('input[type="radio"]')) {
                radio.checked = true;
                radio.dispatchEvent(new Event('change'));
            }
        });
    });
    
        // Add click handlers for payment method headers specifically
    const paymentMethodHeaders = document.querySelectorAll('.payment-method-header');
    paymentMethodHeaders.forEach(header => {
        header.addEventListener('click', (event) => {
            const radio = header.querySelector('input[type="radio"]');
            if (radio && !event.target.matches('input[type="radio"]')) {
                radio.checked = true;
                radio.dispatchEvent(new Event('change'));
            }
        });
    });
    
    // Add error clearing event listeners to all form fields
    addErrorClearingListeners();
}

// Function to add error clearing event listeners to form fields
function addErrorClearingListeners() {
    // Text input fields
    const textInputs = ['last-name', 'first-name', 'middle-name', 'phone-number', 'email', 'address-line'];
    textInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('input', () => clearFieldError(inputId));
            input.addEventListener('focus', () => clearFieldError(inputId));
        }
    });
    
    // Textarea fields
    const textareaInputs = ['comment-delivery', 'comment-pickup'];
    textareaInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('input', () => clearFieldError(inputId));
            input.addEventListener('focus', () => clearFieldError(inputId));
        }
    });
    
    // Select fields
    const selectInputs = ['city'];
    selectInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('change', () => clearFieldError(inputId));
            input.addEventListener('focus', () => clearFieldError(inputId));
        }
    });
    
    // Date field
    const dateInput = document.getElementById('delivery-date');
    if (dateInput) {
        dateInput.addEventListener('focus', () => clearFieldError('deliveryDate'));
        // Also clear error when date is selected via calendar
        dateInput.addEventListener('change', () => {
            clearFieldError('deliveryDate');
            const value = dateInput.value || '';
            const re = /^(\d{2})\.(\d{2})\.(\d{4})$/;
            const match = value.trim().match(re);
            if (!match) {
                try { dateInput.dataset.valid = 'false'; } catch (e) {}
            }
        });
    }
    
    // Delivery method radios
    const deliveryRadios = document.querySelectorAll('input[name="deliveryMethod"]');
    deliveryRadios.forEach(radio => {
        radio.addEventListener('change', () => clearFieldError('deliveryMethod'));
    });
    
    // Pickup address radios
    const pickupRadios = document.querySelectorAll('input[name="pickupAddress"]');
    pickupRadios.forEach(radio => {
        radio.addEventListener('change', () => clearFieldError('pickupAddress'));
    });
    
    // Payment method radios for pickup
    const pickupPaymentRadios = document.querySelectorAll('input[name="paymentMethodPickup"]');
    pickupPaymentRadios.forEach(radio => {
        radio.addEventListener('change', () => clearFieldError('paymentMethodPickup'));
    });
    
    // Payment method radios for courier delivery
    const courierPaymentRadios = document.querySelectorAll('input[name="paymentMethod"]');
    courierPaymentRadios.forEach(radio => {
        radio.addEventListener('change', () => clearFieldError('paymentMethod'));
    });
}



    function updateMainButtonCartInfo() {
        const currentView = getCurrentView();
        
        // Update page title
        updatePageTitle();
        
        // Debug logging
        console.log('🔍 updateMainButtonCartInfo called - currentView:', currentView);
        
        // Hide the main button if we're on cart or checkout screens
        if (currentView === 'cart' || currentView === 'checkout') {
            console.log('🔍 Hiding cart button - on cart/checkout screen');
            Telegram.WebApp.MainButton.hide();
            return;
        }
        
        const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        const totalPrice = Object.values(cart).reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        console.log('🔍 Cart items:', totalItems, 'Total price:', totalPrice);

        if (totalItems > 0) {
            console.log('🔍 Showing cart button with:', totalItems, 'items');
            Telegram.WebApp.MainButton.setText(`Корзина (${totalItems}) - ${totalPrice.toFixed(2)} р.`);
            // Устанавливаем коричневый цвет как у кнопок + и - и "Начать покупки"
            Telegram.WebApp.MainButton.setParams({
                color: '#b76c4b'
            });
            Telegram.WebApp.MainButton.show();
        } else {
            console.log('🔍 Hiding cart button - no items');
            Telegram.WebApp.MainButton.hide();
        }
    }

    function updateSubmitButtonState() {
        const submitButton = document.querySelector('.submit-order-button');
        if (submitButton && checkoutTotalElement) {
            const totalAmount = parseFloat(checkoutTotalElement.textContent.replace(' р.', ''));
            const courierRadio = document.getElementById('delivery-courier-radio');
            const pickupRadio = document.getElementById('delivery-pickup-radio');
            
            // Check if courier delivery is selected
            const isCourierSelected = courierRadio && courierRadio.checked;
            
            // Disable button only if courier is selected AND total is less than 70.00
            if (isCourierSelected && totalAmount < 70.00) {
                submitButton.disabled = true;
                submitButton.title = 'Минимальная сумма заказа для доставки курьером составляет 70.00 р.';
            } else {
                submitButton.disabled = false;
                submitButton.title = '';
            }
        }
    }

    function setupDateInput() {
        // Flatpickr removed; ClassicalCalendar handles date picking.
        // Keep this function for compatibility with existing calls.
        return;
    }

    const initialCategory = getUrlParameter('category');
    const initialView = getUrlParameter('view');

    // Show loading overlay first - critical for Android
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.remove('hidden');
        loadingOverlay.style.display = 'flex'; // Force display for Android
    }

    // Hide all content initially - Android-specific fixes
    if (mainPageContainer) {
        mainPageContainer.classList.add('hidden');
        if (isAndroidDevice) {
            mainPageContainer.style.display = 'none'; // Force hide for Android
        }
    }
    if (welcomeContainer) {
        welcomeContainer.classList.add('hidden');
        if (isAndroidDevice) {
            welcomeContainer.style.display = 'none'; // Force hide for Android
        }
    }

    // Hide Telegram Web App buttons during loading
    if (Telegram.WebApp.MainButton) {
        Telegram.WebApp.MainButton.hide();
    }
    if (Telegram.WebApp.BackButton) {
        Telegram.WebApp.BackButton.hide();
    }

    // Helper to proceed to initial view and hide loading overlay
    function proceedToInitialView() {
        try { document.body.classList.add('loaded'); } catch {}
        if (loadingOverlay) loadingOverlay.classList.add('hidden');
        if (initialView === 'checkout') {
            displayView('checkout');
        } else if (initialView === 'cart' || initialCategory === 'cart') {
            displayView('cart');
        } else if (initialView === 'categories') {
            displayView('categories');
        } else if (initialCategory) {
            displayView('products', initialCategory);
        } else {
            displayView('welcome');
        }
    }

    // Wait for background image to load
    const img = new Image();
    img.src = '/bot-app/images/Hleb.jpg?v=1.3.96&t=1756283401';
    // Safety timeout in case onload never fires
    const loadingSafetyTimeout = setTimeout(() => {
        console.warn('Loading safety timeout reached. Proceeding to initial view.');
        proceedToInitialView();
    }, 2500);
    img.onload = () => {
        clearTimeout(loadingSafetyTimeout);
        // Add loaded class to body to show background
        document.body.classList.add('loaded');
        // Hide loading overlay and show appropriate view after a short delay
        setTimeout(() => {
            proceedToInitialView();
        }, 400);
    };
    
    // Fallback in case image fails to load
    img.onerror = () => {
        clearTimeout(loadingSafetyTimeout);
        proceedToInitialView();
    };

    if (Telegram.WebApp.MainButton) {
        Telegram.WebApp.MainButton.onClick(() => {
            displayView('cart');
        });
        // Don't show the button during loading - it will be shown when appropriate views are displayed
    }

    // Инициализация кнопок, которые всегда присутствуют в DOM
    if (continueShoppingButton) {
        continueShoppingButton.addEventListener('click', () => {
            // Всегда ведем на страницу "Наше меню" (категории)
            displayView('categories');
        });
    } else {
        console.error('Элемент с ID "continue-shopping-button" не найден в DOM. Невозможно прикрепить слушатель кликов.');
    }

    if (startShoppingButton) {
        startShoppingButton.addEventListener('click', () => {
            // 🔗 ПЕРЕНАПРАВЛЕНИЕ В БОТ ЧАТ С ЗАДЕРЖКОЙ ЗАКРЫТИЯ: Кнопка "Заказать с доставкой" 
            // перенаправляет пользователя в основной чат бота, а затем закрывает WebApp через полсекунды
            console.log('🔗 Перенаправление в бот чат с задержкой закрытия WebApp');
            
            // Redirect to bot chat immediately
            try {
                Telegram.WebApp.openTelegramLink('https://t.me/drazhin_bakery_bot');
            } catch (redirectError) {
                console.warn('Could not redirect to bot chat:', redirectError);
                // Fallback: try to open in new window/tab
                window.open('https://t.me/drazhin_bakery_bot', '_blank');
            }
            
            // Close the WebApp after half a second delay
            setTimeout(() => {
                try {
                    if (Telegram.WebApp.close) {
                        Telegram.WebApp.close();
                    }
                } catch (closeError) {
                    console.warn('Could not close WebApp automatically:', closeError);
                }
            }, 500); // 500ms = half a second
        });
    } else {
        console.error('Элемент с ID "start-shopping-button" не найден в DOM. Невозможно прикрепить слушатель кликов.');
    }

    // Инициализация кнопки "Наше меню" для пустой корзины
    const emptyCartMenuButton = document.getElementById('empty-cart-menu-button');
    if (emptyCartMenuButton) {
        emptyCartMenuButton.addEventListener('click', () => {
            displayView('categories');
        });
    } else {
        console.error('Элемент с ID "empty-cart-menu-button" не найден в DOM. Невозможно прикрепить слушатель кликов.');
    }

    // Cart rendering is now initialized earlier after products data is loaded

    // Функция для показа экрана с информацией о продукте
    function showProductScreen(productId, categoryKey) {
        let product = null;

        // Ищем продукт во всех категориях
        for (const catKey in productsData) {
            product = productsData[catKey].find(p => p.id === productId);
            if (product) break;
        }

        if (!product) {
            console.error('Продукт не найден:', productId);
            return;
        }

        // Сохраняем текущую категорию для возврата
        currentProductCategory = categoryKey;

        const screenBody = document.getElementById('product-screen-body');
        if (!screenBody) {
            console.error('Элемент product-screen-body не найден');
            return;
        }

        // Формируем HTML для экрана продукта
        let screenHTML = `
            <img src="${product.image_url || 'https://placehold.co/400x300/e0e0e0/555?text=Нет+фото'}" 
                 alt="${product.name}" 
                 class="product-screen-image" 
                 onerror="this.onerror=null;this.src='https://placehold.co/400x300/e0e0e0/555?text=Нет+фото';">

            <div class="product-screen-name">${product.name}</div>
            <div class="product-screen-price">${parseFloat(product.price).toFixed(2)} р.</div>
            
            <!-- Кнопки управления количеством -->
            <div class="input-group input-group-sm d-flex align-items-center justify-content-center justify-content-md-start">
                <div class="changer count_minus cur-p pos-r w-200 w-xs-300 h-200 h-xs-300 br-50p d-flex align-items-center justify-content-center screen-decrease-quantity" data-product-id="${product.id}" style="background-color: #d7d7d7;">
                    <span class="fz-150 fw-400 fc-1 mb-25">-</span>
                </div>
                <input type="number" name="count" value="0" min="0" readonly="" class="count mssaleprice-count cur-p form-control ptb-25 fz-175 mlr-50 text-center mx-w-300 product-screen-quantity-display" id="screen-quantity-${product.id}" style="border: none !important; background-color:transparent !important;">
                <div class="changer count_plus cur-p pos-r w-200 w-xs-300 h-200 h-xs-300 br-50p d-flex align-items-center justify-content-center screen-increase-quantity" data-product-id="${product.id}" style="background-color: #d7d7d7;">
                    <span class="fz-150 fw-400 fc-1">+</span>
                </div>
            </div>

            <div class="product-screen-info">`;

                        // Добавляем информацию о доступности
                if (product.availability_days && product.availability_days !== 'N/A') {
                    screenHTML += `
                        <div class="product-screen-info-item product-screen-info-item-availability">
                            <div class="availability fz-100" style="color: #b76c4b; text-align: center;">
                                ${product.availability_days}
                            </div>
                        </div>`;
                }

                        // Добавляем краткое описание
                if (product.short_description && product.short_description !== 'N/A') {
                    screenHTML += `
                        <div class="product-screen-info-item product-screen-info-item-short-description">
                            <div class="short-description fz-100">
                                ${product.short_description}
                            </div>
                        </div>`;
                }

                        // Добавляем информацию о весе
                if (product.weight && product.weight !== 'N/A') {
                    screenHTML += `
                        <div class="product-screen-info-item product-screen-info-item-weight">
                            <div class="wight fz-100">
                                <span class="weight-label">Вес:</span>
                                ${product.weight} гр
                            </div>
                        </div>`;
                }

                        // Добавляем информацию о веганстве
                if (product.for_vegans && product.for_vegans !== 'N/A') {
                    screenHTML += `
                        <div class="product-screen-info-item product-screen-info-item-vegan">
                            <div class="vegan fz-100">
                                <span class="vegan-label">Подходит веганам</span>
                                <svg class="svg svg-vegan fz-150 ml-50">
                                    <use xlink:href="sprite.svg#vegan"></use>
                                </svg>
                            </div>
                        </div>`;
                }

        screenHTML += `</div>`;

                        // Добавляем состав (ингредиенты)
                if (product.ingredients && product.ingredients !== 'N/A') {
                    screenHTML += `
                        <div class="product-screen-ingredients">
                            <div class="structure fz-100">
                                <span class="ingredients-label">Состав:</span>
                                ${product.ingredients}
                            </div>
                        </div>`;
                }

                        // Добавляем пищевую ценность
                if (product.calories && product.calories !== 'N/A') {
                    screenHTML += `
                        <div class="product-screen-nutrition">
                            <div class="product-screen-nutrition-value">
                                <div class="calories fz-100">
                                    <span class="calories-label">Калорийность:</span>
                                    ${product.calories}
                                </div>`;

                    if (product.energy_value && product.energy_value !== 'N/A') {
                        screenHTML += `<div class="energy-value fz-100">
                                    <span class="energy-label">Энергетическая ценность:</span>
                                    ${product.energy_value}
                                </div>`;
                    }

                    screenHTML += `
                            </div>
                        </div>`;
                }

        screenBody.innerHTML = screenHTML;

        // Обновляем счетчик количества в экране продукта
        const quantityDisplay = document.getElementById(`screen-quantity-${product.id}`);
        if (quantityDisplay) {
            const currentQuantity = cart[product.id] ? cart[product.id].quantity : 0;
            quantityDisplay.value = currentQuantity;
        }

        // Показываем экран продукта
        displayView('product');

        // Добавляем обработчики для кнопок управления количеством в экране продукта
        const decreaseButton = screenBody.querySelector('.screen-decrease-quantity');
        const increaseButton = screenBody.querySelector('.screen-increase-quantity');
        
        if (decreaseButton) {
            decreaseButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const productId = e.currentTarget.dataset.productId;
                updateProductQuantity(productId, -1);
                // Обновляем счетчик в экране продукта
                const quantityDisplay = document.getElementById(`screen-quantity-${productId}`);
                if (quantityDisplay) {
                    quantityDisplay.value = cart[productId] ? cart[productId].quantity : 0;
                }
            });
        }
        
        if (increaseButton) {
            increaseButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const productId = e.currentTarget.dataset.productId;
                updateProductQuantity(productId, 1);
                // Обновляем счетчик в экране продукта
                const quantityDisplay = document.getElementById(`screen-quantity-${productId}`);
                if (quantityDisplay) {
                    quantityDisplay.value = cart[productId] ? cart[productId].quantity : 0;
                }
            });
        }
    }

    // Делаем функции доступными глобально
    window.showProductScreen = showProductScreen;
    
    // Cache management functions for debugging
    window.clearAllCaches = clearAllCaches;
    window.getCacheStatus = getCacheStatus;
    window.CACHE_VERSION = CACHE_VERSION;
    
    // Cart management functions for debugging
    window.getCartAge = getCartAge;
    window.checkCartExpiration = checkCartExpiration;
    window.CART_DATA_VERSION = CART_DATA_VERSION;
    window.CART_EXPIRATION_DAYS = CART_EXPIRATION_DAYS;
    
    // Customer data management functions for debugging
    window.loadCustomerDataWithExpiration = loadCustomerDataWithExpiration;
    window.saveCustomerDataWithMetadata = saveCustomerDataWithMetadata;
    window.extractCustomerDataFromForm = extractCustomerDataFromForm;
    window.populateFormWithCustomerData = populateFormWithCustomerData;
    window.clearCustomerData = clearCustomerData;
    window.checkCustomerDataExpiration = checkCustomerDataExpiration;
    window.getCustomerDataAge = getCustomerDataAge;
    window.CUSTOMER_DATA_KEY = CUSTOMER_DATA_KEY;
    window.CUSTOMER_DATA_VERSION = CUSTOMER_DATA_VERSION;
    window.CUSTOMER_DATA_EXPIRATION_DAYS = CUSTOMER_DATA_EXPIRATION_DAYS;
    
    // Service Worker functions removed to fix iOS twitching issues

    // ===== CLASSICAL CALENDAR IMPLEMENTATION =====
    class ClassicalCalendar {
        constructor() {
            this.dateInput = document.getElementById('delivery-date');
            this.calendarIcon = document.getElementById('calendar-icon');
            this.calendarOverlay = document.getElementById('calendar-overlay');
            this.calendarClose = document.getElementById('calendar-close');
            this.calendarMonthYear = document.getElementById('calendar-month-year');
            this.calendarDates = document.getElementById('calendar-dates');
            
            this.selectedDate = null;
            this.currentDate = new Date();
            this.viewDate = new Date();
            
            this.monthNames = [
                'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
            ];
            
            this.init();
        }
        
        init() {
            if (!this.dateInput || !this.calendarOverlay) return;
            
            // Ensure field starts empty
            this.dateInput.value = '';
            
            // Add event listeners
            this.dateInput.addEventListener('click', () => this.openCalendar());
            // Restore original behavior if needed: open on focus as well
            this.dateInput.addEventListener('focus', () => this.openCalendar());
            this.calendarIcon.addEventListener('click', () => this.openCalendar());
            this.calendarClose.addEventListener('click', () => this.closeCalendar());
            this.calendarOverlay.addEventListener('click', (e) => {
                if (e.target === this.calendarOverlay) {
                    this.closeCalendar();
                }
            });
            
            // Initialize calendar view
            this.renderCalendar();
            
            console.log('✅ Classical Calendar initialized');
        }
        
        formatDate(date) {
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}.${month}.${year}`;
        }
        
        isDateEnabled(date) {
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            // Reset time for comparison
            today.setHours(0, 0, 0, 0);
            tomorrow.setHours(0, 0, 0, 0);
            const checkDate = new Date(date);
            checkDate.setHours(0, 0, 0, 0);
            
            return checkDate.getTime() === today.getTime() || checkDate.getTime() === tomorrow.getTime();
        }
        
        renderCalendar() {
            // Update month/year display
            this.calendarMonthYear.textContent = `${this.monthNames[this.viewDate.getMonth()]} ${this.viewDate.getFullYear()}`;
            
            // Clear previous dates
            this.calendarDates.innerHTML = '';
            
            // Get first day of the month
            const firstDay = new Date(this.viewDate.getFullYear(), this.viewDate.getMonth(), 1);
            const lastDay = new Date(this.viewDate.getFullYear(), this.viewDate.getMonth() + 1, 0);
            
            // Get first Monday of the calendar (might be from previous month)
            const startDate = new Date(firstDay);
            const dayOfWeek = firstDay.getDay();
            const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // Monday = 0
            startDate.setDate(firstDay.getDate() - daysToSubtract);
            
            // Generate 6 weeks (42 days)
            for (let i = 0; i < 42; i++) {
                const currentDate = new Date(startDate);
                currentDate.setDate(startDate.getDate() + i);
                
                const dateElement = document.createElement('div');
                dateElement.className = 'calendar-date';
                dateElement.textContent = currentDate.getDate();
                
                // Add classes based on date status
                const isCurrentMonth = currentDate.getMonth() === this.viewDate.getMonth();
                const isEnabled = this.isDateEnabled(currentDate);
                const isSelected = this.selectedDate && 
                    currentDate.getTime() === this.selectedDate.getTime();
                
                if (!isCurrentMonth) {
                    dateElement.classList.add('other-month');
                }
                
                if (isEnabled) {
                    dateElement.classList.add('enabled');
                    dateElement.addEventListener('click', () => this.selectDate(currentDate));
                } else {
                    dateElement.classList.add('disabled');
                }
                
                if (isSelected) {
                    dateElement.classList.add('selected');
                }
                
                this.calendarDates.appendChild(dateElement);
            }
        }
        
        selectDate(date) {
            if (!this.isDateEnabled(date)) return;
            
            // Update selected date
            this.selectedDate = new Date(date);
            this.selectedDate.setHours(0, 0, 0, 0);
            
            // Update input field
            const formattedDate = this.formatDate(date);
            this.dateInput.value = formattedDate;
            // Mark as valid selection for state-based checks
            try { this.dateInput.dataset.valid = 'true'; } catch (e) {}
            
            // Clear any error and sync validity state
            const errorElement = document.getElementById('deliveryDate-error');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
            try { this.dateInput.dataset.valid = 'true'; } catch (e) {}
            
            // Re-render calendar to show selection
            this.renderCalendar();
            
            // Close calendar after short delay for better UX
            setTimeout(() => {
                this.closeCalendar();
            }, 300);
            
            console.log('📅 Date selected:', formattedDate);
            
            // Do not trigger full form validation here to avoid loops
        }
        
        // Month navigation removed - calendar automatically follows current date
        
        openCalendar() {
            // Automatically determine which month to show based on available dates
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            // If tomorrow is in next month, show the month that contains both dates
            // Otherwise, show current month
            if (today.getMonth() !== tomorrow.getMonth()) {
                // Today is last day of month, tomorrow is first day of next month
                // Show current month (where today is)
                this.viewDate = new Date(today);
            } else {
                // Both dates are in same month, show that month
                this.viewDate = new Date(today);
            }
            
            this.renderCalendar();
            
            this.calendarOverlay.classList.add('active');
            console.log('📅 Classical calendar opened - showing month with available dates');
            
            // Prevent body scroll on mobile
            if (isMobileDevice) {
                document.body.style.overflow = 'hidden';
            }
        }
        
        closeCalendar() {
            this.calendarOverlay.classList.remove('active');
            console.log('📅 Classical calendar closed');
            
            // Restore body scroll
            if (isMobileDevice) {
                document.body.style.overflow = '';
            }
        }
        
        getSelectedDate() {
            return this.selectedDate;
        }
        
        getFormattedDate() {
            return this.dateInput.value;
        }
        
        reset() {
            this.dateInput.value = '';
            this.selectedDate = null;
            this.renderCalendar();
            try { this.dateInput.dataset.valid = 'false'; } catch (e) {}
        }
    }
    
    // Legacy validateDeliveryDate removed; unified validateDeliveryDateField is used
    
    // Initialize classical calendar
    let classicalCalendar;
    
    // Initialize calendar when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            classicalCalendar = new ClassicalCalendar();
        });
    } else {
        classicalCalendar = new ClassicalCalendar();
    }
    
    // Make calendar globally accessible for debugging
    if (DEBUG) {
        window.classicalCalendar = classicalCalendar;
    }
    
    // ===== END CUSTOM CALENDAR IMPLEMENTATION =====

    // Mobile detection for animation optimization
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    
    // iOS detection
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
                  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);



    // Update page title with cart status
    function updatePageTitle() {
        const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        const totalPrice = Object.values(cart).reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        if (totalItems > 0) {
            document.title = `Корзина: ${totalItems} товаров - ${totalPrice.toFixed(2)} р.`;
        } else {
            document.title = 'Пекарня Дражина';
        }
    }

});