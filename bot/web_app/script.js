// Инициализация Telegram Web App
Telegram.WebApp.ready();
Telegram.WebApp.expand(); // Разворачиваем Web App на весь экран

// --- ВРЕМЕННО ДЛЯ ОТЛАДКИ: ОЧИСТИТЬ LOCAL STORAGE ПРИ КАЖДОМ ЗАПУСКЕ ---
// УДАЛИТЕ ЭТУ СТРОКУ ПОСЛЕ ЗАВЕРШЕНИЯ ОТЛАДКИ!
// localStorage.clear(); // <-- ЭТА СТРОКА УДАЛЕНА ИЛИ ЗАКОММЕНТИРОВАНА
// ---------------------------------------------------------------------

// Оборачиваем весь основной код в обработчик DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {

    // Reset the flag when the DOM is loaded (i.e., Web App is opened/reloaded)
    // This flag is now primarily for programmatic calls, not the 'closing' event.
    let isClosingHandledProgrammatically = false; 

    const welcomeContainer = document.getElementById('welcome-container');
    const productsContainer = document.getElementById('products-container');
    const cartContainer = document.getElementById('cart-container');
    const checkoutContainer = document.getElementById('checkout-container');
    const categoryTitle = document.getElementById('main-category-title'); // Главный заголовок
    const cartItemsList = document.getElementById('cart-items-list');
    const cartTotalDisplay = document.getElementById('cart-total');
    const checkoutForm = document.getElementById('checkout-form');
    const courierDeliveryFields = document.getElementById('courier-delivery-fields');
    const pickupAddresses = document.getElementById('pickup-addresses');
    const deliveryMethodRadios = document.querySelectorAll('input[name="deliveryMethod"]');
    const mainAppContent = document.getElementById('app-content');
    const startShoppingButton = document.getElementById('start-shopping-button');

    // Новые элементы для текста условий доставки
    const courierInfoText = document.getElementById('courier-text');
    const pickupInfoText = document.getElementById('pickup-text');


    // Локальное хранилище корзины в Web App
    let cart = JSON.parse(localStorage.getItem('drazhin_bakery_cart')) || {};

    // Глобальная переменная для хранения данных о продуктах, загруженных через API
    let productsDataCache = {}; // Изменено на productsDataCache для ясности

    // Функция для сохранения корзины в localStorage
    function saveCart() {
        localStorage.setItem('drazhin_bakery_cart', JSON.stringify(cart));
        updateMainButtonVisibility();
    }

    // Функция для обновления видимости главной кнопки Telegram Web App
    function updateMainButtonVisibility() {
        const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        if (totalItems > 0 && Telegram.WebApp.MainButton) {
            Telegram.WebApp.MainButton.setText(`Корзина (${totalItems} товаров) - ${calculateCartTotal().toFixed(2)} р.`);
            Telegram.WebApp.MainButton.show();
        } else if (Telegram.WebApp.MainButton) {
            Telegram.WebApp.MainButton.hide();
        }
    }

    // Обработчик для главной кнопки Telegram Web App (Корзина)
    if (Telegram.WebApp.MainButton) {
        Telegram.WebApp.MainButton.onClick(() => {
            displayView('cart');
        });
        updateMainButtonVisibility(); // Инициализация при загрузке
    }

    // Global BackButton setup
    if (Telegram.WebApp.BackButton) {
        Telegram.WebApp.BackButton.onClick(() => {
            console.log("DEBUG: Telegram Web App BackButton clicked.");
            // Send data and then close, similar to 'back-to-main-menu-webapp'
            sendCartUpdateToBotProgrammatic();
            setTimeout(() => {
                Telegram.WebApp.close();
            }, 50); // Small delay to allow sendData to initiate
        });
    }

    // Функция для получения параметров URL
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    // Функция для отображения нужного вида (каталог, корзина, оформление, приветствие)
    function displayView(viewName, category = null) {
        console.log(`DEBUG: displayView called with viewName: ${viewName}, category: ${category}`);
        welcomeContainer.classList.add('hidden');
        productsContainer.classList.add('hidden');
        cartContainer.classList.add('hidden');
        checkoutContainer.classList.add('hidden');
        categoryTitle.classList.add('hidden'); // Скрываем заголовок по умолчанию

        // Manage BackButton visibility
        if (Telegram.WebApp.BackButton) {
            if (viewName === 'welcome') {
                Telegram.WebApp.BackButton.hide();
            } else {
                Telegram.WebApp.BackButton.show();
            }
        }

        if (viewName === 'welcome') {
            console.log('DEBUG: Displaying welcome view.');
            welcomeContainer.classList.remove('hidden');
            Telegram.WebApp.MainButton.hide(); // Скрываем кнопку корзины на приветственном экране
        } else if (viewName === 'products' && category) {
            console.log(`DEBUG: Displaying products view for category: ${category}`);
            categoryTitle.textContent = getCategoryDisplayName(category);
            categoryTitle.classList.remove('hidden');
            productsContainer.classList.remove('hidden');
            loadProducts(category);
            updateMainButtonVisibility(); // Показываем/скрываем кнопку корзины
        } else if (viewName === 'cart') {
            console.log('DEBUG: Displaying cart view.');
            categoryTitle.textContent = 'Ваша корзина';
            categoryTitle.classList.remove('hidden');
            cartContainer.classList.remove('hidden');
            displayCart(); // Вызываем displayCart без await, так как она теперь синхронна
            updateMainButtonVisibility(); // Показываем/скрываем кнопку корзины
        } else if (viewName === 'checkout') {
            console.log('DEBUG: Displaying checkout view.');
            categoryTitle.textContent = 'Оформление заказа';
            categoryTitle.classList.remove('hidden');
            checkoutContainer.classList.remove('hidden');
            setupCheckoutForm();
            Telegram.WebApp.MainButton.hide(); // Скрываем кнопку корзины на экране оформления заказа
        }
    }

    // Вспомогательная функция для получения отображаемого имени категории
    function getCategoryDisplayName(categoryKey) {
        const map = {
            'bakery': 'Выпечка',
            'croissants': 'Круассаны',
            'artisan_bread': 'Ремесленный хлеб',
            'desserts': 'Десерты',
            'cart': 'Корзина'
        };
        return map[categoryKey] || 'Каталог товаров';
    }

    // Функция для получения данных о продуктах с API
    async function fetchProductsData(category) {
        const apiUrl = `/api/products?category=${category}`; // Используем относительный путь, category уже должен быть правильным
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


    // Функция для загрузки и отображения продуктов
    async function loadProducts(category) {
        productsContainer.innerHTML = '<div style="text-align: center; padding: 20px;">Загрузка товаров...</div>';
        const products = await fetchProductsData(category); // category уже будет "category_bakery" или "bakery"
        productsDataCache[category] = products; // Кэшируем данные
        productsContainer.innerHTML = ''; // Очищаем "Загрузка..."

        if (products.length === 0) {
            productsContainer.innerHTML = '<div style="text-align: center; padding: 20px;">В этой категории пока нет товаров.</div>';
            return;
        }

        products.forEach((product, index) => {
            // Используем category_index в качестве productId для уникальности
            // productId будет, например, "bakery_0", "artisan_bread_1"
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

        // Добавляем обработчики событий для кнопок +/-
        productsContainer.querySelectorAll('.quantity-controls button').forEach(button => {
            button.addEventListener('click', (event) => {
                const productId = event.target.dataset.productId;
                const action = event.target.dataset.action;
                updateCartQuantity(productId, action);
            });
        });
    }

    // Функция для обновления количества товара в корзине
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
                // Если продукт не найден в кэше, сохраняем только ID и количество
                // В этом случае, image_url будет отсутствовать, и отобразится "Нет фото"
                cart[productId] = { id: productId, quantity: currentQuantity, name: "Неизвестный товар", price: 0 };
            }
        }

        // Обновляем отображение количества на карточке товара
        const qtyDisplay = document.getElementById(`qty-${productId}`);
        if (qtyDisplay) {
            qtyDisplay.textContent = currentQuantity;
        }
        saveCart(); // Сохраняем корзину
    }

    // Функция для расчета общей суммы корзины
    function calculateCartTotal() {
        let total = 0;
        for (const productId in cart) {
            if (cart[productId] && cart[productId].price) { // Проверяем, что цена существует
                total += cart[productId].price * cart[productId].quantity;
            }
        }
        return total;
    }

    // Функция для отображения корзины
    async function displayCart() {
        console.log('DEBUG: Entering displayCart function.');
        cartItemsList.innerHTML = ''; // Очищаем список товаров в корзине
        let totalPrice = 0;

        // Clean up cart from potentially malformed productIds
        const cleanedCart = {};
        for (const productId in cart) {
            const itemInCart = cart[productId];
            const parts = productId.split('_');
            // Check for valid format: at least two parts, last part is a number
            if (parts.length >= 2 && /^\d+$/.test(parts[parts.length - 1])) {
                const categoryPart = parts.slice(0, parts.length - 1).join('_');
                // Ensure the category part is not 'cart' or 'checkout' or other non-product categories
                if (categoryPart !== 'cart' && categoryPart !== 'checkout' && categoryPart !== 'welcome') {
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
            Telegram.WebApp.MainButton.hide(); // Скрываем кнопку корзины если она пуста
            return;
        }

        // Collect all unique categories from items in the cart that might need data fetching
        const categoriesToFetch = new Set();
        for (const productId in cart) {
            const itemInCart = cart[productId];
            // Check if essential product details are missing (e.g., if loaded from localStorage from a previous session)
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

        // Добавляем обработчики событий для кнопок корзины
        cartItemsList.querySelectorAll('.cart-item-controls button').forEach(button => {
            button.addEventListener('click', (event) => {
                const productId = event.target.dataset.productId;
                const action = event.target.dataset.action;
                if (action === 'remove') {
                    delete cart[productId];
                    saveCart();
                    displayCart(); // Перерисовываем корзину
                } else {
                    updateCartQuantity(productId, action);
                    displayCart(); // Перерисовываем корзину, чтобы обновились суммы
                }
            });
        });
        console.log('DEBUG: Exiting displayCart function.');
    }

    // Функция для очистки корзины
    document.getElementById('clear-cart-webapp').addEventListener('click', () => {
        cart = {};
        saveCart();
        displayCart(); // Обновляем отображение корзины
        Telegram.WebApp.showAlert('Корзина очищена!');
    });

    // Функция для перехода к оформлению заказа
    document.getElementById('proceed-to-checkout-webapp').addEventListener('click', () => {
        if (Object.keys(cart).length === 0) {
            Telegram.WebApp.showAlert('Ваша корзина пуста. Нечего оформлять!');
            return;
        }
        displayView('checkout');
    });

    // Функция для отправки данных корзины боту (программно)
    function sendCartUpdateToBotProgrammatic() {
        // Проверяем флаг, чтобы избежать дублирования отправки
        if (isClosingHandledProgrammatically) {
            console.log("DEBUG: sendCartUpdateToBotProgrammatic skipped, already handled for this session.");
            return;
        }
        const cart_sync_data = {
            type: 'cart_sync', // Новый тип данных для синхронизации корзины
            items: Object.values(cart) // Отправляем массив объектов товаров
        };
        Telegram.WebApp.sendData(JSON.stringify(cart_sync_data));
        console.log("DEBUG: Cart data sent programmatically.");
        isClosingHandledProgrammatically = true; // Устанавливаем флаг после отправки
    }

    // NEW: Обработчик события закрытия Web App для синхронизации корзины
    // Это событие срабатывает, когда Web App собирается быть закрытым (пользователем или программно)
    Telegram.WebApp.onEvent('closing', () => {
        console.log("DEBUG: Telegram Web App 'closing' event triggered.");
        // Directly send data here, without relying on isClosingHandledProgrammatically,
        // as this is the final moment and we want to guarantee sending.
        const cart_sync_data = {
            type: 'cart_sync',
            items: Object.values(cart)
        };
        Telegram.WebApp.sendData(JSON.stringify(cart_sync_data));
        console.log("DEBUG: Cart data sent directly on 'closing' event.");
    });


    // Функция для возврата из корзины в главное меню бота (закрытие Web App)
    document.getElementById('back-to-main-menu-webapp').addEventListener('click', () => {
        sendCartUpdateToBotProgrammatic(); // Явно отправляем данные
        // Небольшая задержка, чтобы дать Telegram.WebApp.sendData() время на обработку
        setTimeout(() => {
            Telegram.WebApp.close(); // Закрываем Web App
        }, 50);
    });

    // Функция для возврата из оформления заказа к корзине
    document.getElementById('back-from-checkout-to-cart').addEventListener('click', () => {
        displayCart(); // Возвращаемся к отображению корзины
    });

    // Настройка формы оформления заказа
    function setupCheckoutForm() {
        // Инициализация полей доставки
        toggleDeliveryFields();
        deliveryMethodRadios.forEach(radio => {
            radio.addEventListener('change', toggleDeliveryFields);
        });

        // Установка минимальной даты для delivery-date
        const today = new Date();
        const year = today.getFullYear();
        const month = (today.getMonth() + 1).toString().padStart(2, '0');
        const day = today.getDate().toString().padStart(2, '0');
        document.getElementById('delivery-date').min = `${year}-${month}-${day}`;
    }

    function toggleDeliveryFields() {
        const isCourier = document.querySelector('input[name="deliveryMethod"]:checked').value === 'courier';

        // Показываем/скрываем информационные тексты
        if (courierInfoText) {
            if (isCourier) {
                courierInfoText.classList.remove('hidden');
            } else {
                courierInfoText.classList.add('hidden');
            }
        }
        if (pickupInfoText) {
            if (!isCourier) {
                pickupInfoText.classList.remove('hidden');
            } else {
                pickupInfoText.classList.add('hidden');
            }
        }

        // Управление required атрибутами для полей
        const lastName = document.getElementById('last-name');
        const firstName = document.getElementById('first-name');
        const middleName = document.getElementById('middle-name');
        const phoneNumber = document.getElementById('phone-number');
        const email = document.getElementById('email');
        const deliveryDate = document.getElementById('delivery-date');
        const city = document.getElementById('city');
        const addressLine = document.getElementById('address-line');
        const pickupRadios = document.getElementById('pickup-radio-group').querySelectorAll('input[type="radio"]');

        // Всегда обязательные поля
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

    // Валидация формы
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

        // Скрываем все сообщения об ошибках перед новой валидацией
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

        // Простая валидация номера телефона (можно улучшить)
        if (!/^\+?\d{9,15}$/.test(phoneNumber.value.trim())) {
            document.getElementById('phoneNumber-error').style.display = 'block';
            isValid = false;
        }

        // Простая валидация Email
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
        } else { // Самовывоз
            if (!pickupSelected) {
                document.getElementById('pickupAddress-error').style.display = 'block';
                isValid = false;
            }
        }
        return isValid;
    }


    // Обработчик отправки формы заказа
    checkoutForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Предотвращаем стандартную отправку формы

        if (!validateForm()) {
            Telegram.WebApp.showAlert('Пожалуйста, заполните все обязательные поля корректно.');
            return;
        }

        const formData = new FormData(checkoutForm);
        const orderDetails = {};
        // Собираем данные из формы
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
            orderDetails.comment = formData.get('comment'); // Комментарий для курьера
        } else { // pickup
            orderDetails.pickupAddress = formData.get('pickupAddress');
            orderDetails.comment = formData.get('comment');
        }


        // Добавляем товары из корзины в orderDetails
        orderDetails.items = [];
        let totalOrderPrice = 0;

        // Collect all unique categories from items in the cart that might need data fetching
        const categoriesToFetchForOrder = new Set();
        for (const productId in cart) {
            const itemInCart = cart[productId];
            // Correctly extract category key from productId
            const parts = productId.split('_');
            const category = parts.slice(0, parts.length - 1).join('_');

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

        // Добавляем тип данных для бота
        orderDetails.type = 'order_submission';

        // Отправляем данные боту
        Telegram.WebApp.sendData(JSON.stringify(orderDetails));
        console.log("DEBUG: Данные заказа отправлены боту.");

        // Очищаем корзину после отправки заказа
        cart = {};
        saveCart(); // Это вызовет saveCart, которая НЕ будет вызывать sendCartUpdateToBotProgrammatic
        sendCartUpdateToBotProgrammatic(); // Явно отправляем данные после заказа, чтобы обновить счетчик

        // Небольшая задержка, чтобы дать Telegram.WebApp.sendData() время на обработку
        setTimeout(() => {
            Telegram.WebApp.close(); // Закрываем Web App
        }, 50);
    });

    // Обработчик для кнопки "Начать покупки" на приветственном экране
    startShoppingButton.addEventListener('click', () => {
        // Открываем ссылку на бота Telegram
        Telegram.WebApp.openTelegramLink('https://t.me/drazhin_bakery_bot');
        Telegram.WebApp.close(); // Закрываем Web App
    });

    // Инициализация отображения при загрузке страницы
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
        displayView('welcome');
    }
}); // Конец обработчика DOMContentLoaded
