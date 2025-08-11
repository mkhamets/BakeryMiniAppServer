// Инициализация Telegram Web App
Telegram.WebApp.ready();
Telegram.WebApp.expand(); // Разворачиваем Web App на весь экран

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

// Оборачиваем весь основной код в обработчик DOMContentLoaded
document.addEventListener('DOMContentLoaded', async () => {

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

    let cart = JSON.parse(localStorage.getItem('cart')) || {};
    let productsData = {};
    let isSubmitting = false; // Флаг для предотвращения двойной отправки
    let currentProductCategory = null; // Для отслеживания категории продукта

    const CATEGORY_DISPLAY_MAP = {
        "category_bakery": { name: "Выпечка", icon: "images/bakery.svg", image: "images/bakery.svg" },
        "category_croissants": { name: "Круассаны", icon: "images/crouasan.svg", image: "images/crouasan.svg" },
        "category_artisan_bread": { name: "Ремесленный хлеб", icon: "images/bread1.svg", image: "images/bread1.svg" },
        "category_desserts": { name: "Десерты", icon: "images/cookie.svg", image: "images/cookie.svg" }
    };

    await fetchProductsData();
    
    // Only initialize cart rendering after products data is loaded
    renderCart();
    
    // Initialize icons in the UI (excluding location icons for form fields)
    initializeIcons();

    function displayView(viewName, categoryKey = null) {
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
                if (welcomeContainer) welcomeContainer.classList.remove('hidden');
                if (mainPageContainer) mainPageContainer.classList.add('hidden');
                Telegram.WebApp.MainButton.hide();
                break;
            case 'categories':
                if (mainPageContainer) mainPageContainer.classList.remove('hidden');
                if (categoriesContainer) categoriesContainer.classList.remove('hidden');
                if (mainCategoryTitle) {
                    mainCategoryTitle.textContent = 'Наше меню';
                    mainCategoryTitle.classList.remove('hidden');
                }
                loadCategories();
                // Show basket button for categories view
                if (Telegram.WebApp.MainButton) {
                    updateMainButtonCartInfo();
                }
                // Scroll to top of the page when categories view is displayed
                window.scrollTo(0, 0);
                break;
            case 'products':
                if (mainPageContainer) mainPageContainer.classList.remove('hidden');
                if (productsContainer) productsContainer.classList.remove('hidden');
                if (mainCategoryTitle) mainCategoryTitle.classList.remove('hidden');
                loadProducts(categoryKey);
                // Show basket button for products view
                if (Telegram.WebApp.MainButton) {
                    updateMainButtonCartInfo();
                }
                // Scroll to top of the page when products view is displayed
                window.scrollTo(0, 0);
                break;
            case 'product':
                if (productScreen) productScreen.classList.remove('hidden');
                Telegram.WebApp.MainButton.hide();
                break;
            case 'cart':
                if (mainPageContainer) mainPageContainer.classList.remove('hidden');
                if (cartContainer) cartContainer.classList.remove('hidden');
                if (mainCategoryTitle) {
                    mainCategoryTitle.textContent = 'Ваша корзина';
                    mainCategoryTitle.classList.remove('hidden');
                }
                renderCart();
                Telegram.WebApp.MainButton.hide();
                // Scroll to top of the page when cart view is displayed
                window.scrollTo(0, 0);
                break;
            case 'checkout':
                if (mainPageContainer) mainPageContainer.classList.remove('hidden');
                if (checkoutContainer) checkoutContainer.classList.remove('hidden');
                if (mainCategoryTitle) {
                    mainCategoryTitle.textContent = 'Оформление заказа';
                    mainCategoryTitle.classList.remove('hidden');
                }
                renderCheckoutSummary();
                setupDateInput();
                updateSubmitButtonState();
                Telegram.WebApp.MainButton.hide();
                // Scroll to top of the page when checkout view is displayed
                window.scrollTo(0, 0);
                break;
            default:
                console.warn('Неизвестное представление:', viewName);
                break;
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
                         onerror="this.onerror=null;this.src='https://placehold.co/300x225/e0e0e0/555?text=Нет+фото';">
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

        localStorage.setItem('cart', JSON.stringify(cart));
        updateProductCardUI(productId);
        updateMainButtonCartInfo();
    }

    function updateProductCardUI(productId) {
        const quantitySpan = document.getElementById(`qty-${productId}`);
        if (quantitySpan) {
            const currentQuantity = cart[productId] ? cart[productId].quantity : 0;
            quantitySpan.textContent = currentQuantity;
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

            const cartItemElement = document.createElement('div');
            cartItemElement.className = 'cart-item';
            cartItemElement.dataset.productId = item.id;

            cartItemElement.innerHTML = `
                <img src="${item.image_url || 'https://placehold.co/80x80/cccccc/333333?text=No+Image'}" 
                     alt="${item.name}" class="cart-item-image"
                     onerror="this.onerror=null;this.src='https://placehold.co/80x80/cccccc/333333?text=No+Image';">
                <div class="cart-item-details">
                    <h4 class="cart-item-name">${item.name}</h4>
                    <p class="cart-item-price">
                        <span class="price-per-unit">${item.price} р. за шт.</span>
                        <span class="cart-item-total">${itemTotal.toFixed(2)} р.</span>
                    </p>
                    <div class="cart-item-controls">
                        <div class="input-group input-group-sm d-flex align-items-center justify-content-center justify-content-md-start">
                            <div class="changer count_minus cur-p pos-r w-200 w-xs-300 h-200 h-xs-300 br-50p d-flex align-items-center justify-content-center decrease-cart-quantity" data-product-id="${item.id}" style="background-color: #d7d7d7;">
                                <span class="fz-150 fw-400 fc-1 mb-25">-</span>
                            </div>
                            <input type="number" name="count" value="${item.quantity}" min="1" readonly="" class="count mssaleprice-count cur-p form-control ptb-25 fz-175 mlr-50 text-center mx-w-300 cart-item-quantity" style="border: none !important; background-color:transparent !important;">
                            <div class="changer count_plus cur-p pos-r w-200 w-xs-300 h-200 h-xs-300 br-50p d-flex align-items-center justify-content-center increase-cart-quantity" data-product-id="${item.id}" style="background-color: #d7d7d7;">
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

        // Добавляем контейнер с информацией об условиях реализации продуктов
        renderAvailabilityInfo(cartItems);

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
                    localStorage.setItem('cart', JSON.stringify(cart));
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
        }
    }

    function clearCart() {
        cart = {};
        localStorage.removeItem('cart');
        renderCart();
        updateMainButtonCartInfo();
    }

    function renderCheckoutSummary() {
        if (checkoutItemsList) checkoutItemsList.innerHTML = '';
        let total = 0;

        Object.values(cart).forEach(item => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            const checkoutItemElement = document.createElement('li');
            checkoutItemElement.className = 'checkout-item-summary';
            checkoutItemElement.textContent = `${item.name} x ${item.quantity} - ${itemTotal.toFixed(2)} р.`;
            if (checkoutItemsList) checkoutItemsList.appendChild(checkoutItemElement);
        });

        if (checkoutTotalElement) checkoutTotalElement.textContent = `${total.toFixed(2)} р.`;

        const selectedDeliveryMethod = document.querySelector('input[name="deliveryMethod"]:checked')?.value;
        toggleDeliveryFields(selectedDeliveryMethod);

        const backFromCheckoutToCartButton = document.getElementById('back-from-checkout-to-cart');
        if (backFromCheckoutToCartButton) {
            backFromCheckoutToCartButton.addEventListener('click', () => displayView('cart'));
        } else {
            console.error('Элемент с ID "back-from-checkout-to-cart" не найден в DOM. Невозможно прикрепить слушатель кликов.');
        }

        if (checkoutForm) {
            checkoutForm.addEventListener('submit', (event) => {
                event.preventDefault();

                const formData = new FormData(checkoutForm);
                const orderDetails = {};
                for (let [key, value] of formData.entries()) {
                    orderDetails[key] = value;
                }

                let isValid = true;
                const errorMessages = [];

                if (!orderDetails.lastName) { isValid = false; errorMessages.push('Пожалуйста, введите вашу фамилию.'); }
                if (!orderDetails.firstName) { isValid = false; errorMessages.push('Пожалуйста, введите ваше имя.'); }
                if (!orderDetails.middleName) { isValid = false; errorMessages.push('Пожалуйста, введите ваше отчество.'); }

                const phoneRegex = /^\+?[\d\s\-\(\)]{7,20}$/;
                if (!orderDetails.phoneNumber || !phoneRegex.test(orderDetails.phoneNumber)) {
                    isValid = false;
                    errorMessages.push('Пожалуйста, введите корректный номер телефона.');
                }

                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!orderDetails.email || !emailRegex.test(orderDetails.email)) {
                    isValid = false;
                    errorMessages.push('Пожалуйста, введите корректный Email.');
                }

                if (!orderDetails.deliveryDate) { isValid = false; errorMessages.push('Пожалуйста, выберите дату доставки/самовывоза.'); }

                if (!orderDetails.deliveryMethod) {
                    isValid = false;
                    errorMessages.push('Пожалуйста, выберите способ получения.');
                } else {
                    if (orderDetails.deliveryMethod === 'courier') {
                        if (!orderDetails.city) { isValid = false; errorMessages.push('Пожалуйста, выберите город для доставки.'); }
                        if (!orderDetails.addressLine) { isValid = false; errorMessages.push('Пожалуйста, введите адрес доставки.'); }
                    } else if (orderDetails.deliveryMethod === 'pickup') {
                        if (!orderDetails.pickupAddress) { isValid = false; errorMessages.push('Пожалуйста, выберите адрес самовывоза.'); }
                    }
                }

                if (!isValid) {
                    console.error('Validation errors:', errorMessages.join('\n'));
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
                        commentPickup: orderDetails.commentPickup || ''
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
                    
                    clearCart();
                    
                    // Order sent successfully - close WebApp after delay to ensure data is sent
                    setTimeout(() => {
                        try {
                            if (Telegram.WebApp.close) {
                                Telegram.WebApp.close();
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
            console.error('Элемент с ID "checkout-form" не найден. Невозможно прикрепить слушатель отправки.');
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
    }



    function updateMainButtonCartInfo() {
        const currentView = getCurrentView();
        
        // Hide the main button if we're on cart or checkout screens
        if (currentView === 'cart' || currentView === 'checkout') {
            Telegram.WebApp.MainButton.hide();
            return;
        }
        
        const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        const totalPrice = Object.values(cart).reduce((sum, item) => sum + (item.price * item.quantity), 0);

        if (totalItems > 0) {
            Telegram.WebApp.MainButton.setText(`Корзина (${totalItems}) - ${totalPrice.toFixed(2)} р.`);
            // Устанавливаем коричневый цвет как у кнопок + и - и "Начать покупки"
            Telegram.WebApp.MainButton.setParams({
                color: '#b76c4b'
            });
            Telegram.WebApp.MainButton.show();
        } else {
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
        const dateInput = document.getElementById('delivery-date');
        if (dateInput) {
            // Get today's date
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            // Format dates for input (YYYY-MM-DD)
            const todayFormatted = today.toISOString().split('T')[0];
            const tomorrowFormatted = tomorrow.toISOString().split('T')[0];
            
            // Set min and max dates
            dateInput.min = todayFormatted;
            dateInput.max = tomorrowFormatted;
            
            // Set default value to today
            dateInput.value = todayFormatted;
            
            // Add event listener to prevent selecting other dates
            dateInput.addEventListener('input', function() {
                const selectedDate = new Date(this.value);
                const today = new Date();
                const tomorrow = new Date(today);
                tomorrow.setDate(tomorrow.getDate() + 1);
                
                // Reset to today if date is not today or tomorrow
                if (selectedDate < today || selectedDate > tomorrow) {
                    this.value = today.toISOString().split('T')[0];
                }
            });
        }
    }

    const initialCategory = getUrlParameter('category');
    const initialView = getUrlParameter('view');

    // Show loading overlay first
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) loadingOverlay.classList.remove('hidden');

    // Hide all content initially
    if (mainPageContainer) mainPageContainer.classList.add('hidden');
    if (welcomeContainer) welcomeContainer.classList.add('hidden');

    // Hide Telegram Web App buttons during loading
    if (Telegram.WebApp.MainButton) {
        Telegram.WebApp.MainButton.hide();
    }
    if (Telegram.WebApp.BackButton) {
        Telegram.WebApp.BackButton.hide();
    }

    // Wait for background image to load
    const img = new Image();
    img.src = '/bot-app/images/Hleb.jpg?v=1.0.18';
    img.onload = () => {
        // Add loaded class to body to show background
        document.body.classList.add('loaded');
        
        // Hide loading overlay and show appropriate view after a short delay
        setTimeout(() => {
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
                // Only show welcome if no specific view is requested
                displayView('welcome');
            }
        }, 1000); // 1 second delay to show the logo
    };
    
    // Fallback in case image fails to load
    img.onerror = () => {
        document.body.classList.add('loaded');
        if (loadingOverlay) loadingOverlay.classList.add('hidden');
        displayView('welcome');
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
            // 🔗 ПЕРЕНАПРАВЛЕНИЕ В БОТ ЧАТ: Кнопка "Узнать об условиях доставки" 
            // перенаправляет пользователя в основной чат бота для получения информации о доставке
            console.log('🔗 Перенаправление в бот чат для получения информации о доставке');
            Telegram.WebApp.openTelegramLink('https://t.me/drazhin_bakery_bot');
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

        // Добавляем информацию о весе
        if (product.weight && product.weight !== 'N/A') {
            screenHTML += `
                <div class="product-screen-info-item product-screen-info-item-weight">
                    <div class="product-screen-info-label">Вес: ${product.weight} гр.</div>
                </div>`;
        }

        // Добавляем информацию о доступности
        if (product.availability_days && product.availability_days !== 'N/A') {
            screenHTML += `
                <div class="product-screen-info-item product-screen-info-item-availability">
                    <div class="product-screen-info-label">Доступен для заказа: ${product.availability_days}</div>
                </div>`;
        }

        screenHTML += `</div>`;

        // Добавляем состав (ингредиенты)
        if (product.ingredients && product.ingredients !== 'N/A') {
            screenHTML += `
                <div class="product-screen-ingredients">
                    <div class="product-screen-ingredients-label">Состав:</div>
                    <div class="product-screen-ingredients-value">${product.ingredients}</div>
                </div>`;
        }

        // Добавляем пищевую ценность
        if (product.calories && product.calories !== 'N/A') {
            screenHTML += `
                <div class="product-screen-nutrition">
                    <div class="product-screen-nutrition-label">Пищевая ценность:</div>
                    <div class="product-screen-nutrition-value">
                        <div><strong>Калорийность:</strong> ${product.calories}</div>`;

            if (product.energy_value && product.energy_value !== 'N/A') {
                screenHTML += `<div><strong>Энергетическая ценность:</strong> ${product.energy_value}</div>`;
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
            quantityDisplay.textContent = currentQuantity;
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

});