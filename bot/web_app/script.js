// Инициализация Telegram Web App
Telegram.WebApp.ready();
Telegram.WebApp.expand(); // Разворачиваем Web App на весь экран

// --- ВРЕМЕННО ДЛЯ ОТЛАДКИ: ОЧИСТИТЬ LOCAL STORAGE ПРИ КАЖДОМ ЗАПУСКЕ ---
// УДАЛИТЕ ЭТУ СТРОКУ ПОСЛЕ ЗАВЕРШЕНИЯ ОТЛАДКИ!
// localStorage.clear();
// ---------------------------------------------------------------------

// Оборачиваем весь основной код в обработчик DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {

    const mainPageContainer = document.getElementById('main-page-container'); // NEW: The main .container element
    const welcomeContainer = document.getElementById('welcome-container');
    const categoriesContainer = document.getElementById('categories-container');
    const categoriesMainTitle = document.getElementById('categories-main-title');
    const productsContainer = document.getElementById('products-container');
    const cartContainer = document.getElementById('cart-container');
    const checkoutContainer = document.getElementById('checkout-container');
    const categoryTitle = document.getElementById('main-category-title'); // Main title for products/cart/checkout

    const courierInfoText = document.getElementById('courier-text'); // These might be null if not in current HTML, need to check
    const pickupInfoText = document.getElementById('pickup-text'); // These might be null if not in current HTML, need to check

    const cartItemsList = document.getElementById('cart-items-list');
    const cartTotalDisplay = document.getElementById('cart-total');
    const checkoutForm = document.getElementById('checkout-form');
    const courierDeliveryFields = document.getElementById('courier-delivery-fields');
    const pickupAddresses = document.getElementById('pickup-addresses');
    const deliveryMethodRadios = document.querySelectorAll('input[name="deliveryMethod"]');
    const startShoppingButton = document.getElementById('start-shopping-button');

    // Локальное хранилище корзины в Web App
    let cart = JSON.parse(localStorage.getItem('drazhin_bakery_cart')) || {};

    // Глобальная переменная для хранения данных о продуктах, загруженных через API
    let productsDataCache = {};

    // Функция для сохранения корзины в localStorage
    function saveCart() {
        localStorage.setItem('drazhin_bakery_cart', JSON.stringify(cart));
        // Больше не обновляем MainButton здесь, так как она убрана
    }

    // Global BackButton setup
    if (Telegram.WebApp.BackButton && Telegram.WebApp.version && parseFloat(Telegram.WebApp.version) >= 6.1) {
        Telegram.WebApp.BackButton.onClick(() => {
            console.log("DEBUG: Telegram Web App BackButton clicked.");
            // Определяем, куда вернуться
            const currentView = getUrlParameter('view');
            const currentCategory = getUrlParameter('category');

            if (currentView === 'checkout') {
                displayView('cart'); // Из чекаута всегда в корзину
            } else if (currentView === 'cart') { // If current view is cart
                displayView('categories'); // From cart, go to categories
            } else if (currentView === 'products' && currentCategory) {
                displayView('categories'); // Из продуктов на экран категорий
            } else if (currentView === 'categories') {
                Telegram.WebApp.close(); // С экрана категорий закрываем Web App
            } else {
                Telegram.WebApp.close(); // По умолчанию закрываем
            }
        });
    } else {
        console.log("DEBUG: Telegram Web App BackButton not supported or version is too old.");
    }


    // Функция для получения параметров URL
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    // Function to display the correct view (categories, products, cart, checkout, welcome)
    function displayView(viewName, category = null) {
        console.log(`DEBUG: displayView called with viewName: ${viewName}, category: ${category}`);

        // Hide all main content containers and titles
        welcomeContainer.classList.add('hidden');
        categoriesContainer.classList.add('hidden');
        productsContainer.classList.add('hidden');
        cartContainer.classList.add('hidden');
        checkoutContainer.classList.add('hidden');
        categoryTitle.classList.add('hidden');
        categoriesMainTitle.classList.add('hidden');

        // Manage the main .container visibility
        if (viewName === 'welcome') {
            mainPageContainer.classList.add('hidden'); // Hide the white background container for welcome screen
            welcomeContainer.classList.remove('hidden');
        } else {
            mainPageContainer.classList.remove('hidden'); // Show the white background container for other views
            if (viewName === 'categories') {
                categoriesMainTitle.classList.remove('hidden');
                categoriesContainer.classList.remove('hidden');
                loadCategories();
            } else if (viewName === 'products' && category) {
                categoryTitle.textContent = getCategoryDisplayName(category);
                categoryTitle.classList.remove('hidden');
                productsContainer.classList.remove('hidden');
                loadProducts(category);
            } else if (viewName === 'cart') {
                categoryTitle.textContent = 'Ваша корзина';
                categoryTitle.classList.remove('hidden');
                cartContainer.classList.remove('hidden');
                displayCart();
            } else if (viewName === 'checkout') {
                categoryTitle.textContent = 'Оформление заказа';
                categoryTitle.classList.remove('hidden');
                checkoutContainer.classList.remove('hidden');
                setupCheckoutForm();
            }
        }

        // Update BackButton visibility based on the current view
        if (Telegram.WebApp.BackButton && Telegram.WebApp.version && parseFloat(Telegram.WebApp.version) >= 6.1) {
            if (viewName === 'welcome' || viewName === 'categories') {
                Telegram.WebApp.BackButton.hide();
            } else {
                Telegram.WebApp.BackButton.show();
            }
        }

        // Update MainButton (Cart) visibility
        const totalItemsInCart = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        if (Telegram.WebApp.MainButton) {
            if (viewName === 'products' || viewName === 'categories') {
                if (totalItemsInCart > 0) {
                    Telegram.WebApp.MainButton.setText(`Корзина (${totalItemsInCart} товаров) - ${calculateCartTotal().toFixed(2)} р.`);
                    Telegram.WebApp.MainButton.show();
                } else {
                    Telegram.WebApp.MainButton.hide();
                }
            } else {
                Telegram.WebApp.MainButton.hide();
            }
        }
    }

    // Вспомогательная функция для получения отображаемого имени категории
    function getCategoryDisplayName(categoryKey) {
        const map = {
            'bakery': 'Выпечка',
            'croissants': 'Круассаны',
            'artisan_bread': 'Ремесленный хлеб',
            'desserts': 'Десерты',
            'cart': 'Корзина', // This key is for internal use, not a product category
            'categories': 'Наше меню' // Added for the categories view title
        };
        return map[categoryKey] || 'Каталог товаров';
    }

    // Function to fetch product data from API
    async function fetchProductsData(category) {
        const apiUrl = `/api/products?category=${category}`;
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Ошибка при получении данных о продуктах с API:", error);
            Telegram.WebApp.showAlert(`Не удалось загрузить товары для категории "${getCategoryDisplayName(category)}". Пожалуйста, попробуйте позже.`);
            return [];
        }
    }

    // NEW FUNCTION: Load and display categories
    async function loadCategories() {
        categoriesContainer.innerHTML = '<div style="text-align: center; padding: 20px;">Загрузка категорий...</div>';
        const apiUrl = `/api/categories`; // Assuming you'll add a /api/categories endpoint
        let categories = [];

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            categories = await response.json();
            console.log("DEBUG: Загружены категории:", categories);
        } catch (error) {
            console.error("Ошибка при получении данных о категориях с API:", error);
            Telegram.WebApp.showAlert("Не удалось загрузить категории товаров. Пожалуйста, попробуйте позже.");
            categoriesContainer.innerHTML = '<div style="text-align: center; padding: 20px;">Не удалось загрузить категории.</div>';
            return;
        }

        categoriesContainer.innerHTML = ''; // Clear "Loading..."

        if (categories.length === 0) {
            categoriesContainer.innerHTML = '<div style="text-align: center; padding: 20px;">Категории не найдены.</div>';
            return;
        }

        categories.forEach(category => {
            const categoryCard = document.createElement('div');
            categoryCard.className = 'col-12 col-sm-6 col-lg-3 catalog-item mb-200'; // Using classes from drazhin.by
            categoryCard.innerHTML = `
                <a href="#" data-category-key="${category.key}">
                    <div class="catalog-item__wrapper h-fx-item pos-r">
                        <div class="catalog-item__image-wrapper pos-r ovfl-h">
                            <img src="${category.image_url}" alt="${category.name}" class="catalog-item__image fade-box w-100p h-auto of-c h-fx-item__img lazyloaded" width="300" height="200" onerror="this.onerror=null;this.src='https://placehold.co/300x200/e0e0e0/555?text=Нет+фото';">
                            <div class="catalog-item__image-filter pos-a trbl-0 bgc-gr-1"></div>
                        </div>
                        <div class="catalog-item__text-wrapper h-fx-item__text pos-a trbl-0 ptb-125 plr-150 d-flex flex-column justify-content-end">
                            <h3 class="first-line fz-150 fc-wh ff-2 pt-100 dec-line-top-short dec-color-wh">${category.name}</h3>
                            <div class="second-line btn-arrow mt-75 d-flex align-items-center">
                                <span class="fc-wh fz-75 fw-500 h-fc-wh tt-u ls-7 mr-875">перейти в каталог</span>
                                <svg class="svg svg-arrow-right-white" style="margin-bottom: 0.15rem" viewBox="0 0 24 24" fill="white">
                                    <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
                                </svg>
                            </div>
                        </div>
                    </div>
                </a>
            `;
            categoriesContainer.appendChild(categoryCard);
        });

        // Add click handlers to category cards
        categoriesContainer.querySelectorAll('.catalog-item a').forEach(link => {
            link.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent default link behavior
                const categoryKey = event.currentTarget.dataset.categoryKey;
                console.log(`DEBUG: Category clicked: ${categoryKey}`);
                displayView('products', categoryKey); // Go to products screen for selected category
            });
        });
    }


    // Function to load and display products
    async function loadProducts(category) {
        productsContainer.innerHTML = '<div style="text-align: center; padding: 20px;">Загрузка товаров...</div>';
        const products = await fetchProductsData(category);
        productsDataCache[category] = products; // Cache the data
        productsContainer.innerHTML = ''; // Clear "Loading..."

        if (products.length === 0) {
            productsContainer.innerHTML = '<div style="text-align: center; padding: 20px;">В этой категории пока нет товаров.</div>';
            return;
        }

        products.forEach((product, index) => {
            // Use category_index as productId for uniqueness
            // productId will be, for example, "bakery_0", "artisan_bread_1"
            const productId = `${category}_${index}`;
            const currentQuantity = cart[productId] ? cart[productId].quantity : 0;

            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
                <div class="product-image-container">
                    <img src="${product.image_url || 'https://placehold.co/300x225/e0e0e0/555?text=Нет+фото'}" alt="${product.name}" class="product-image" onerror="this.onerror=null;this.src='https://placehold.co/300x225/e0e0e0/555?text=Нет+фото';">
                </div>
                <div class="product-info">
                    <div>
                        <div class="product-name">${product.name}</div>
                        <div class="product-price">${parseFloat(product.price).toFixed(2)} р.</div>
                        <div class="product-details">
                            ${product.weight && product.weight !== 'N/A' ? `<span>Вес: ${product.weight} гр.</span>` : ''}
                            ${product.availability_days && product.availability_days !== 'N/A' ? `<span>Доступность: ${product.availability_days}</span>` : ''}
                        </div>
                    </div>
                    <div>
                        <div class="quantity-controls">
                            <button data-product-id="${productId}" data-action="decrease">-</button>
                            <span class="quantity-display" id="qty-${productId}">${currentQuantity}</span>
                            <button data-product-id="${productId}" data-action="increase">+</button>
                        </div>
                        <a href="${product.url}" target="_blank" class="details-link">Подробнее</a>
                    </div>
                </div>
            `;
            productsContainer.appendChild(productCard);
        });

        // Add event listeners for +/- buttons
        productsContainer.querySelectorAll('.quantity-controls button').forEach(button => {
            button.addEventListener('click', (event) => {
                const productId = event.target.dataset.productId;
                const action = event.target.dataset.action;
                updateCartQuantity(productId, action);
            });
        });
    }

    // Function to update product quantity in cart
    function updateCartQuantity(productId, action) {
        let currentQuantity = cart[productId] ? cart[productId].quantity : 0;

        if (action === 'increase') {
            currentQuantity++;
        } else if (action === 'decrease') {
            currentQuantity--;
            if (currentQuantity < 0) currentQuantity = 0;
        }

        if (currentQuantity === 0) {
            delete cart[productId];
        } else {
            // Correctly parse category and index from productId
            const parts = productId.split('_');
            const index = parseInt(parts.pop()); // Last part is the index
            const category = parts.join('_'); // Remaining parts form the category key

            const productInfo = productsDataCache[category] ? productsDataCache[category][index] : null;

            if (productInfo) {
                cart[productId] = {
                    id: productId,
                    name: productInfo.name,
                    price: parseFloat(productInfo.price),
                    quantity: currentQuantity,
                    image_url: productInfo.image_url,
                    url: productInfo.url,
                    weight: productInfo.weight,
                    availability_days: productInfo.availability_days
                };
            } else {
                console.warn(`Продукт с ID ${productId} не найден в кэше при обновлении корзины. Возможно, старая запись.`);
                // If product not found in cache, save only ID and quantity
                // In this case, image_url will be missing, and "Нет фото" will be displayed
                cart[productId] = { id: productId, quantity: currentQuantity, name: "Неизвестный товар", price: 0 };
            }
        }

        // Update quantity display on product card
        const qtyDisplay = document.getElementById(`qty-${productId}`);
        if (qtyDisplay) {
            qtyDisplay.textContent = currentQuantity;
        }
        saveCart(); // Save cart
        updateMainButtonCartInfo(); // Update info on main button
    }

    // Function to update info on Telegram Web App's Main Button
    function updateMainButtonCartInfo() {
        const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        const totalAmount = calculateCartTotal();

        if (Telegram.WebApp.MainButton) {
            if (totalItems > 0) {
                Telegram.WebApp.MainButton.setText(`Корзина (${totalItems} товаров) - ${totalAmount.toFixed(2)} р.`);
                Telegram.WebApp.MainButton.show();
            } else {
                Telegram.WebApp.MainButton.hide();
            }
        }
    }

    // Function to calculate total cart amount
    function calculateCartTotal() {
        let total = 0;
        for (const productId in cart) {
            if (cart[productId] && cart[productId].price) { // Check that price exists
                total += cart[productId].price * cart[productId].quantity;
            }
        }
        return total;
    }

    // Function to display cart
    async function displayCart() {
        console.log('DEBUG: Entering displayCart function.');
        cartItemsList.innerHTML = ''; // Clear item list in cart
        let totalPrice = 0;

        // Clean up cart from potentially malformed productIds
        const cleanedCart = {};
        for (const productId in cart) {
            const itemInCart = cart[productId];
            const parts = productId.split('_');
            // Check for valid format: at least two parts, last part is a number
            if (parts.length >= 2 && /^\d+$/.test(parts[parts.length - 1])) {
                const categoryPart = parts.slice(0, parts.length - 1).join('_');
                // Ensure the category part is NOT 'cart' or 'checkout' or other non-product categories
                if (categoryPart !== 'cart' && categoryPart !== 'checkout' && categoryPart !== 'welcome' && categoryPart !== 'categories') {
                    cleanedCart[productId] = itemInCart;
                } else {
                    console.warn(`WARN: Invalid category '${categoryPart}' found in productId '${productId}'. Skipping item.`);
                }
            } else {
                console.warn(`WARN: Malformed productId '${productId}'. Skipping item.`);
            }
        }
        cart = cleanedCart; // Update the global cart object with cleaned data
        saveCart(); // Persist the cleaned cart to localStorage

        const productIdsInCart = Object.keys(cart);
        if (productIdsInCart.length === 0) {
            console.log('DEBUG: Cart is empty after cleaning.');
            cartItemsList.innerHTML = '<p style="text-align: center; color: #666;">Ваша корзина пуста.</p>';
            cartTotalDisplay.textContent = 'Общая сумма: 0.00 р.';
            Telegram.WebApp.MainButton.hide(); // Hide cart button if empty
            return;
        }

        // Collect all unique categories from items in the cart that might need data fetching
        const categoriesToFetch = new Set();
        for (const productId in cart) {
            const itemInCart = cart[productId];
            // Correctly extract category key from productId
            const parts = productId.split('_');
            const categoryFromId = parts.slice(0, parts.length - 1).join('_'); // Get full category name
            const indexFromId = parseInt(parts[parts.length - 1]);

            // IMPORTANT: Only consider fetching if product details are incomplete AND it's a valid product ID format
            // AND the category is NOT 'cart' (to prevent fetching /api/products?category=cart)
            if ((!itemInCart.name || !itemInCart.price || !itemInCart.image_url) &&
                categoryFromId && !isNaN(indexFromId) && categoryFromId !== 'cart') {
                categoriesToFetch.add(categoryFromId);
            }
        }

        // Fetch missing product data for categories if needed
        // Use Promise.all to fetch all categories concurrently
        const fetchPromises = Array.from(categoriesToFetch).map(async (category) => {
            if (!productsDataCache[category] || productsDataCache[category].length === 0) {
                console.log(`DEBUG: Fetching missing product data for category: ${category}`);
                const products = await fetchProductsData(category);
                productsDataCache[category] = products;

                // Update cart items with full details if they were missing
                products.forEach((product, index) => {
                    const productIdInCache = `${category}_${index}`;
                    if (cart[productIdInCache] && (!cart[productIdInCache].name || !cart[productIdInCache].image_url)) {
                        cart[productIdInCache] = {
                            id: productIdInCache,
                            name: product.name,
                            price: parseFloat(product.price),
                            quantity: cart[productIdInCache].quantity, // Keep existing quantity
                            image_url: product.image_url,
                            url: product.url,
                            weight: product.weight,
                            availability_days: product.availability_days
                        };
                        console.log(`DEBUG: Updated cart item ${productIdInCache} with full details.`);
                    }
                });
            }
        });
        await Promise.all(fetchPromises); // Wait for all fetches to complete
        saveCart(); // Save cart after potentially updating with full details


        // Now iterate and display, all items in cart should have full details
        for (const productId in cart) {
            const itemInCart = cart[productId];
            const quantity = itemInCart.quantity;

            if (quantity > 0) {
                const itemPrice = parseFloat(itemInCart.price);
                const lineTotal = itemPrice * quantity;
                totalPrice += lineTotal;

                const cartItem = document.createElement('div');
                cartItem.className = 'cart-item';
                cartItem.innerHTML = `
                        <img src="${itemInCart.image_url || 'https://placehold.co/80x80/e0e0e0/555?text=Нет+фото'}" alt="${itemInCart.name}" class="cart-item-image" onerror="this.onerror=null;this.src='https://placehold.co/80x80/e0e0e0/555?text=Нет+фото';">
                        <div class="cart-item-details">
                            <div class="cart-item-name">${itemInCart.name}</div>
                            <div class="cart-item-price">${quantity} шт. x ${itemPrice.toFixed(2)} р. = ${lineTotal.toFixed(2)} р.</div>
                        </div>
                        <div class="cart-item-controls">
                            <button data-product-id="${productId}" data-action="decrease">-</button>
                            <span class="quantity-display">${quantity}</span>
                            <button data-product-id="${productId}" data-action="increase">+</button>
                            <button data-product-id="${productId}" data-action="remove" class="remove-btn">🗑</button>
                        </div>
                    `;
                cartItemsList.appendChild(cartItem);
            }
        }

        cartTotalDisplay.textContent = `Общая сумма: ${totalPrice.toFixed(2)} р.`;

        // Add event listeners for cart buttons
        cartItemsList.querySelectorAll('.cart-item-controls button').forEach(button => {
            button.addEventListener('click', (event) => {
                const productId = event.target.dataset.productId;
                const action = event.target.dataset.action;
                if (action === 'remove') {
                    delete cart[productId];
                    saveCart();
                    displayCart(); // Re-render cart
                } else {
                    updateCartQuantity(productId, action);
                    displayCart(); // Re-render cart to update totals
                }
            });
        });
        console.log('DEBUG: Exiting displayCart function.');
    }

    // Function to clear cart
    document.getElementById('clear-cart-webapp').addEventListener('click', () => {
        cart = {};
        saveCart();
        displayCart(); // Update cart display
        Telegram.WebApp.showAlert('Корзина очищена!');
        sendCartUpdateToBot(); // Send update to bot after clearing
    });

    // Function to proceed to checkout
    document.getElementById('proceed-to-checkout-webapp').addEventListener('click', () => {
        if (Object.keys(cart).length === 0) {
            Telegram.WebApp.showAlert('Ваша корзина пуста. Нечего оформлять!');
            return;
        }
        displayView('checkout');
    });

    // Function to send cart data to bot (programmatically, only on close or explicit action)
    function sendCartUpdateToBot() {
        const cart_sync_data = {
            type: 'cart_sync', // New data type for cart synchronization
            items: Object.values(cart) // Send array of item objects
        };
        try {
            Telegram.WebApp.sendData(JSON.stringify(cart_sync_data));
            console.log("DEBUG: Cart data sent programmatically.");
        } catch (error) {
            console.error("ERROR: Failed to send cart data programmatically:", error);
        }
    }

    // Event handler for Web App closing to sync cart
    Telegram.WebApp.onEvent('closing', () => {
        console.log("DEBUG: Telegram Web App 'closing' event triggered.");
        sendCartUpdateToBot(); // Send data directly, as this is the last chance
    });


    // Function to return from cart to main bot menu (close Web App)
    document.getElementById('back-to-main-menu-webapp').addEventListener('click', () => {
        sendCartUpdateToBot(); // Explicitly send data
        // Small delay to allow Telegram.WebApp.sendData() to process
        setTimeout(() => {
            Telegram.WebApp.close(); // Close Web App
        }, 500); // Increased delay
    });

    // Function to return from checkout to cart
    document.getElementById('back-from-checkout-to-cart').addEventListener('click', () => {
        displayView('cart'); // Return to cart view
    });

    // Setup checkout form
    function setupCheckoutForm() {
        // Initialize delivery fields
        toggleDeliveryFields();
        deliveryMethodRadios.forEach(radio => {
            radio.addEventListener('change', toggleDeliveryFields);
        });

        // Set min date for delivery-date
        const today = new Date();
        const year = today.getFullYear();
        const month = (today.getMonth() + 1).toString().padStart(2, '0');
        const day = today.getDate().toString().padStart(2, '0');
        document.getElementById('delivery-date').min = `${year}-${month}-${day}`;
    }

    function toggleDeliveryFields() {
        const isCourier = document.querySelector('input[name="deliveryMethod"]:checked').value === 'courier';

        // Show/hide info texts
        if (courierInfoText) { // Check if element exists
            if (isCourier) {
                courierInfoText.classList.remove('hidden');
            } else {
                courierInfoText.classList.add('hidden');
            }
        }
        if (pickupInfoText) { // Check if element exists
            if (!isCourier) {
                pickupInfoText.classList.remove('hidden');
            } else {
                pickupInfoText.classList.add('hidden');
            }
        }

        // Manage required attributes for fields
        const lastName = document.getElementById('last-name');
        const firstName = document.getElementById('first-name');
        const middleName = document.getElementById('middle-name');
        const phoneNumber = document.getElementById('phone-number');
        const email = document.getElementById('email');
        const deliveryDate = document.getElementById('delivery-date');
        const city = document.getElementById('city');
        const addressLine = document.getElementById('address-line');
        const pickupRadios = document.getElementById('pickup-radio-group').querySelectorAll('input[type="radio"]');

        // Always required fields
        lastName.setAttribute('required', 'required');
        firstName.setAttribute('required', 'required');
        middleName.setAttribute('required', 'required');
        phoneNumber.setAttribute('required', 'required');
        email.setAttribute('required', 'required');
        deliveryDate.setAttribute('required', 'required');

        if (isCourier) {
            courierDeliveryFields.classList.remove('hidden');
            pickupAddresses.classList.add('hidden');

            city.setAttribute('required', 'required');
            addressLine.setAttribute('required', 'required');
            pickupRadios.forEach(radio => radio.removeAttribute('required'));
        } else {
            courierDeliveryFields.classList.add('hidden');
            pickupAddresses.classList.remove('hidden');

            city.removeAttribute('required');
            addressLine.removeAttribute('required');
            pickupRadios.forEach(radio => radio.setAttribute('required', 'required'));
        }
    }

    // Form validation
    function validateForm() {
        let isValid = true;
        const lastName = document.getElementById('last-name');
        const firstName = document.getElementById('first-name');
        const middleName = document.getElementById('middle-name');
        const phoneNumber = document.getElementById('phone-number');
        const email = document.getElementById('email');
        const deliveryDate = document.getElementById('delivery-date');
        const city = document.getElementById('city');
        const addressLine = document.getElementById('address-line');
        const pickupSelected = document.querySelector('input[name="pickupAddress"]:checked');

        // Hide all error messages before new validation
        document.querySelectorAll('.error-message').forEach(el => el.style.display = 'none');

        if (lastName.value.trim() === '') {
            document.getElementById('lastName-error').style.display = 'block';
            isValid = false;
        }
        if (firstName.value.trim() === '') {
            document.getElementById('firstName-error').style.display = 'block';
            isValid = false;
        }
        if (middleName.value.trim() === '') {
            document.getElementById('middleName-error').style.display = 'block';
            isValid = false;
        }

        // Simple phone number validation (can be improved)
        if (!/^\+?\d{9,15}$/.test(phoneNumber.value.trim())) {
            document.getElementById('phoneNumber-error').style.display = 'block';
            isValid = false;
        }

        // Simple Email validation
        if (!/^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$/.test(email.value.trim())) {
            document.getElementById('email-error').style.display = 'block';
            isValid = false;
        }

        if (deliveryDate.value.trim() === '') {
            document.getElementById('deliveryDate-error').style.display = 'block';
            isValid = false;
        }

        if (document.querySelector('input[name="deliveryMethod"]:checked').value === 'courier') {
            if (city.value.trim() === '') {
                document.getElementById('city-error').style.display = 'block';
                isValid = false;
            }
            if (addressLine.value.trim() === '') {
                document.getElementById('addressLine-error').style.display = 'block';
                isValid = false;
            }
        } else { // Pickup
            if (!pickupSelected) {
                document.getElementById('pickupAddress-error').style.display = 'block';
                isValid = false;
            }
        }
        return isValid;
    }


    // Order form submission handler
    checkoutForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        if (!validateForm()) {
            Telegram.WebApp.showAlert('Пожалуйста, заполните все обязательные поля корректно.');
            return;
        }

        const formData = new FormData(checkoutForm);
        const orderDetails = {};
        // Collect data from form
        orderDetails.lastName = formData.get('lastName');
        orderDetails.firstName = formData.get('firstName');
        orderDetails.middleName = formData.get('middleName');
        orderDetails.phoneNumber = formData.get('phoneNumber');
        orderDetails.email = formData.get('email');
        orderDetails.deliveryDate = formData.get('deliveryDate');
        orderDetails.deliveryMethod = formData.get('deliveryMethod');

        if (orderDetails.deliveryMethod === 'courier') {
            orderDetails.city = formData.get('city');
            orderDetails.addressLine = formData.get('addressLine');
            orderDetails.comment = formData.get('comment'); // Comment for courier
        } else { // pickup
            orderDetails.pickupAddress = formData.get('pickupAddress');
            orderDetails.comment = formData.get('comment');
        }


        // Add items from cart to orderDetails
        orderDetails.items = [];
        let totalOrderPrice = 0;

        // Collect all unique categories from items in the cart that might need data fetching
        const categoriesToFetchForOrder = new Set();
        for (const productId in cart) {
            const itemInCart = cart[productId];
            // Correctly extract category key from productId
            const parts = productId.split('_');
            const category = parts.join('_'); // Get full category name

            if (category) {
                categoriesToFetchForOrder.add(category);
            }
        }

        // Fetch missing product data for categories if needed for order details
        const fetchPromisesForOrder = Array.from(categoriesToFetchForOrder).map(async (category) => {
            if (!productsDataCache[category] || productsDataCache[category].length === 0) {
                console.log(`DEBUG: Fetching missing product data for order submission category: ${category}`);
                const products = await fetchProductsData(category);
                productsDataCache[category] = products;
            }
        });
        await Promise.all(fetchPromisesForOrder); // Wait for all fetches to complete


        for (const productId in cart) {
            const itemInCart = cart[productId];
            const quantity = itemInCart.quantity;

            // Correctly parse category and index from productId for lookup in productsDataCache
            const parts = productId.split('_');
            const index = parseInt(parts.pop());
            const category = parts.join('_');

            const productInfo = productsDataCache[category] ? productsDataCache[category][index] : null;

            if (productInfo) {
                const itemPrice = parseFloat(productInfo.price);
                const lineTotal = itemPrice * quantity;
                totalOrderPrice += lineTotal;

                orderDetails.items.push({
                    id: productId,
                    name: productInfo.name,
                    price: itemPrice,
                    quantity: quantity,
                    lineTotal: lineTotal,
                    image_url: productInfo.image_url,
                    url: productInfo.url,
                    weight: productInfo.weight,
                    availability_days: productInfo.availability_days
                });
            } else {
                // Fallback if product info is still not found (should be rare with fetching)
                console.warn(`WARN: Product with ID ${productId} not found in cache during order submission. Using fallback.`);
                orderDetails.items.push({
                    id: productId,
                    name: itemInCart.name || "Неизвестный товар", // Use name from cart if available, else fallback
                    price: itemInCart.price || 0,
                    quantity: quantity,
                    lineTotal: (itemInCart.price || 0) * quantity
                });
            }
        }
        orderDetails.totalPrice = totalOrderPrice.toFixed(2);

        // Add data type for bot
        orderDetails.type = 'order_submission';

        // Send data to bot
        try {
            Telegram.WebApp.sendData(JSON.stringify(orderDetails));
            console.log("DEBUG: Данные заказа отправлены боту.");
        } catch (error) {
            console.error("ERROR: Failed to send order data:", error);
        }

        // Clear cart after sending order
        cart = {};
        saveCart(); // This will call saveCart, which will NOT call sendCartUpdateToBotProgrammatic
        sendCartUpdateToBot(); // Explicitly send data after order to update counter

        // Small delay to allow Telegram.WebApp.sendData() to process
        setTimeout(() => {
            Telegram.WebApp.close(); // Close Web App
        }, 500); // Increased delay
    });

    // Handler for "Start Shopping" button on welcome screen
    startShoppingButton.addEventListener('click', () => {
        // Open Telegram bot link
        Telegram.WebApp.openTelegramLink('https://t.me/drazhin_bakery_bot');
        Telegram.WebApp.close(); // Close Web App
    });

    // Initialize display on page load
    const initialCategory = getUrlParameter('category');
    const initialView = getUrlParameter('view');
    console.log(`DEBUG: Initializing Web App. initialView='${initialView}', initialCategory='${initialCategory}'`);


    if (initialView === 'checkout') {
        displayView('checkout');
    } else if (initialView === 'cart' || initialCategory === 'cart') {
        console.log('DEBUG: Initializing to cart view based on URL parameters.');
        displayView('cart');
    } else if (initialCategory) {
        console.log(`DEBUG: Initializing to products view for category: ${initialCategory}`);
        displayView('products', initialCategory);
    } else {
        console.log('DEBUG: Initializing to welcome view (no specific parameters).');
        displayView('welcome'); // Default to welcome view if no specific view/category is provided
    }

    // Initialize Telegram Web App Main Button on load
    if (Telegram.WebApp.MainButton) {
        Telegram.WebApp.MainButton.onClick(() => {
            displayView('cart'); // On main button click, always go to cart
        });
        updateMainButtonCartInfo(); // Update button state on load
    }

}); // End of DOMContentLoaded handler
