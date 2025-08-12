// ===== PHASE 6: SERVICE WORKER INTEGRATION =====
// Service Worker for offline caching and intelligent cache strategies

const CACHE_NAME = 'bakery-app-v1.2.0';
const CACHE_VERSION = '1.2.0';

// Cache strategies configuration
const CACHE_STRATEGIES = {
    // Static assets: Cache first, then network
    STATIC: 'cache-first',
    // API responses: Network first, then cache
    API: 'network-first',
    // HTML: Network first, then cache
    HTML: 'network-first'
};

// Files to cache immediately on install
const STATIC_ASSETS = [
    '/bot-app/',
    '/bot-app/index.html',
    '/bot-app/main.min.css',
    '/bot-app/style.css',
    '/bot-app/script.js',
    '/bot-app/images/logo.svg',
    '/bot-app/images/logo-dark.svg',
    '/bot-app/images/bakery.svg',
    '/bot-app/images/bread1.svg',
    '/bot-app/images/cookie.svg',
    '/bot-app/images/crouasan.svg',
    '/bot-app/images/sprite.svg'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('🔄 Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('📦 Caching static assets...');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('✅ Service Worker installed successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('❌ Service Worker installation failed:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('🚀 Service Worker activating...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('🗑️ Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker activated successfully');
                return self.clients.claim();
            })
            .catch((error) => {
                console.error('❌ Service Worker activation failed:', error);
            })
    );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip unsupported schemes (chrome-extension, data, etc.)
    if (url.protocol === 'chrome-extension:' || url.protocol === 'data:' || url.protocol === 'moz-extension:') {
        console.log(`⚠️ Skipping unsupported scheme: ${url.protocol}`);
        return;
    }
    
    // Determine cache strategy based on request type
    const strategy = getCacheStrategy(url);
    
    console.log(`🌐 Fetch: ${url.pathname} (${strategy})`);
    
    switch (strategy) {
        case 'cache-first':
            event.respondWith(cacheFirst(request));
            break;
        case 'network-first':
            event.respondWith(networkFirst(request));
            break;
        default:
            event.respondWith(networkFirst(request));
    }
});

// Cache-first strategy: Check cache first, fallback to network
async function cacheFirst(request) {
    try {
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            console.log('📦 Cache hit:', request.url);
            return cachedResponse;
        }
        
        console.log('🌐 Cache miss, fetching from network:', request.url);
        const networkResponse = await fetch(request);
        
        // Cache the response for future use
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
            console.log('💾 Cached response:', request.url);
        }
        
        return networkResponse;
    } catch (error) {
        console.error('❌ Cache-first strategy failed:', error);
        // Fallback to network
        return fetch(request);
    }
}

// Network-first strategy: Check network first, fallback to cache
async function networkFirst(request) {
    try {
        console.log('🌐 Fetching from network:', request.url);
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache successful responses
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
            console.log('💾 Cached network response:', request.url);
        }
        
        return networkResponse;
    } catch (error) {
        console.log('🌐 Network failed, checking cache:', request.url);
        
        // Fallback to cache
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            console.log('📦 Serving from cache (offline):', request.url);
            return cachedResponse;
        }
        
        // If no cache available, return offline page or error
        console.log('❌ No cache available for:', request.url);
        return new Response('Offline - No cached version available', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Determine cache strategy based on URL
function getCacheStrategy(url) {
    const path = url.pathname;
    
    // Static assets - cache first
    if (path.includes('/images/') || 
        path.includes('/css/') || 
        path.includes('/js/') ||
        path.endsWith('.svg') ||
        path.endsWith('.css') ||
        path.endsWith('.js')) {
        return CACHE_STRATEGIES.STATIC;
    }
    
    // API endpoints - network first
    if (path.includes('/api/')) {
        return CACHE_STRATEGIES.API;
    }
    
    // HTML pages - network first
    if (path.endsWith('.html') || path === '/bot-app/' || path === '/bot-app') {
        return CACHE_STRATEGIES.HTML;
    }
    
    // Default to network first
    return CACHE_STRATEGIES.API;
}

// Message handling for cache management
self.addEventListener('message', (event) => {
    const { type, data } = event.data;
    
    switch (type) {
        case 'SKIP_WAITING':
            console.log('🔄 Skipping waiting...');
            self.skipWaiting();
            break;
            
        case 'CLEAR_CACHE':
            console.log('🗑️ Clearing cache...');
            clearAllCaches();
            break;
            
        case 'GET_CACHE_STATUS':
            console.log('📊 Getting cache status...');
            getCacheStatus().then(status => {
                event.ports[0].postMessage(status);
            });
            break;
            
        default:
            console.log('📨 Unknown message type:', type);
    }
});

// Clear all caches
async function clearAllCaches() {
    try {
        const cacheNames = await caches.keys();
        await Promise.all(
            cacheNames.map(cacheName => caches.delete(cacheName))
        );
        console.log('✅ All caches cleared successfully');
    } catch (error) {
        console.error('❌ Error clearing caches:', error);
    }
}

// Get cache status
async function getCacheStatus() {
    try {
        const cache = await caches.open(CACHE_NAME);
        const keys = await cache.keys();
        
        return {
            cacheName: CACHE_NAME,
            version: CACHE_VERSION,
            cachedItems: keys.length,
            strategies: CACHE_STRATEGIES
        };
    } catch (error) {
        console.error('❌ Error getting cache status:', error);
        return { error: error.message };
    }
}

// ===== END PHASE 6 =====
