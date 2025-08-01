// Инициализация Telegram Web App
Telegram.WebApp.ready();
Telegram.WebApp.expand(); // Разворачиваем Web App на весь экран

// Оборачиваем весь основной код в обработчик DOMContentLoaded
document.addEventListener('DOMContentLoaded', async () => {

    const mainPageContainer = document.getElementById('main-page-container');
    const welcomeContainer = document.getElementById('welcome-container');
    const categoriesContainer = document.getElementById('categories-container');
    const productsContainer = document.getElementById('products-container');
    const cartContainer = document.getElementById('cart-container');
    const checkoutContainer = document.getElementById('checkout-container');
    const mainCategoryTitle = document.getElementById('main-category-title');

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

    const CATEGORY_DISPLAY_MAP = {
        "category_bakery": { name: "Выпечка", emoji: "🥨" },
        "category_croissants": { name: "Круассаны", emoji: "🥐" },
        "category_artisan_bread": { name: "Ремесленный хлеб", emoji: "🍞" },
        "category_desserts": { name: "Десерты", emoji: "🍰" }
    };

    await fetchProductsData();

    function displayView(viewName, categoryKey = null) {
        if (welcomeContainer) welcomeContainer.classList.add('hidden');
        if (mainPageContainer) mainPageContainer.classList.add('hidden');
        if (categoriesContainer) categoriesContainer.classList.add('hidden');
        if (productsContainer) productsContainer.classList.add('hidden');
        if (cartContainer) cartContainer.classList.add('hidden');
        if (checkoutContainer) checkoutContainer.classList.add('hidden');
        if (mainCategoryTitle) mainCategoryTitle.classList.add('hidden');

        if (viewName === 'welcome' || viewName === 'categories') {
            Telegram.WebApp.BackButton.hide();
        } else {
            Telegram.WebApp.BackButton.show();
        }

        switch (viewName) {
            case 'welcome':
                if (welcomeContainer) welcomeContainer.classList.remove('hidden');
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
                Telegram.WebApp.MainButton.hide();
                break;
            case 'products':
                if (mainPageContainer) mainPageContainer.classList.remove('hidden');
                if (productsContainer) productsContainer.classList.remove('hidden');
                if (mainCategoryTitle) mainCategoryTitle.classList.remove('hidden');
                loadProducts(categoryKey);
                updateMainButtonCartInfo();
                break;
            case 'cart':
                if (mainPageContainer) mainPageContainer.classList.remove('hidden');
                if (cartContainer) cartContainer.classList.remove('hidden');
                if (mainCategoryTitle) {
                    mainCategoryTitle.textContent = 'Ваша корзина';
                    mainCategoryTitle.classList.remove('hidden');
                }
                renderCart();
                updateMainButtonCartInfo();
                Telegram.WebApp.MainButton.hide();
                break;
            case 'checkout':
                if (mainPageContainer) mainPageContainer.classList.remove('hidden');
                if (checkoutContainer) checkoutContainer.classList.remove('hidden');
                if (mainCategoryTitle) {
                    mainCategoryTitle.textContent = 'Оформление заказа';
                    mainCategoryTitle.classList.remove('hidden');
                }
                renderCheckoutSummary();
                updateMainButtonCartInfo();
                Telegram.WebApp.MainButton.hide();
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
            if (welcomeContainer && welcomeContainer.classList.contains('hidden')) {
                 Telegram.WebApp.close();
            } else {
                displayView('welcome');
            }
        } else {
            Telegram.WebApp.close();
        }
    });

    function getCurrentView() {
        if (welcomeContainer && !welcomeContainer.classList.contains('hidden')) return 'welcome';
        if (categoriesContainer && !categoriesContainer.classList.contains('hidden')) return 'categories';
        if (productsContainer && !productsContainer.classList.contains('hidden')) return 'products';
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
            if (Telegram.WebApp.showAlert) {
                Telegram.WebApp.showAlert('Не удалось загрузить данные о продуктах. Пожалуйста, попробуйте позже.');
            } else {
                alert('Не удалось загрузить данные о продуктах. Пожалуйста, попробуйте позже.');
            }
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
                const categoryInfo = CATEGORY_DISPLAY_MAP[category.key] || { name: category.key, emoji: '' };
                const categoryDisplayName = categoryInfo.name;
                const categoryEmoji = categoryInfo.emoji;

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
                        <h3 class="category-title-text">${categoryEmoji} ${categoryDisplayName}</h3>
                        <div class="category-link-text">
                            <span>перейти в каталог</span>
                            <svg class="category-arrow-svg" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M10.707 2.293a1 1 0 010 1.414L6.414 8l4.293 4.293a1 1 0 01-1.414 1.414l-5-5a1 1 0 010-1.414l5-5a1 1 0 011.414 0z" transform="rotate(180 8 8)"></path>
                            </svg>
                        </div>
                    </div>
                `;
                console.log('DEBUG: Attaching click listener to categoryCard for:', category.key, categoryCard); // NEW LOG
                categoryCard.addEventListener('click', () => {
                    console.log('DEBUG: Category card clicked for:', category.key); // NEW LOG
                    displayView('products', category.key);
                    localStorage.setItem('lastProductCategory', category.key);
                });
                if (categoriesGrid) categoriesGrid.appendChild(categoryCard);
            });
            if (categoriesContainer) categoriesContainer.appendChild(categoriesGrid);
        } catch (error) {
            console.error('Ошибка при загрузке категорий:', error);
            if (Telegram.WebApp.showAlert) {
                Telegram.WebApp.showAlert('Не удалось загрузить категории. Пожалуйста, попробуйте позже.');
            } else {
                alert('Не удалось загрузить категории. Пожалуйста, попробуйте позже.');
            }
        }
    }

    async function loadProducts(categoryKey) {
        if (!productsData[categoryKey]) {
            await fetchProductsData();
            if (!productsData[categoryKey]) {
                if (Telegram.WebApp.showAlert) {
                    Telegram.WebApp.showAlert('Продукты для этой категории не найдены.');
                } else {
                    alert('Продукты для этой категории не найдены.');
                }
                displayView('categories');
                return;
            }
        }

        const products = productsData[categoryKey];
        if (mainCategoryTitle) mainCategoryTitle.textContent = CATEGORY_DISPLAY_MAP[categoryKey] ? CATEGORY_DISPLAY_MAP[categoryKey].name : 'Продукты';
        if (productListElement) productListElement.innerHTML = '';

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.dataset.productId = product.id;

            const quantityInCart = cart[product.id] ? cart[product.id].quantity : 0;

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
                            ${product.availability_days && product.availability_days !== 'N/A' ? `<span>Доступен для заказа: ${product.availability_days}</span>` : ''}
                        </div>
                    </div>
                    <div>
                        <div class="quantity-controls">
                            <button data-product-id="${product.id}" data-action="decrease">-</button>
                            <span class="quantity-display" id="qty-${product.id}">${quantityInCart}</span>
                            <button data-product-id="${product.id}" data-action="increase">+</button>
                        </div>
                        <a href="${product.url}" target="_blank" class="details-link" data-product-url="${product.url}">Подробнее</a>
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

            // Добавляем обработчики событий для кнопок "Подробнее"
            productListElement.querySelectorAll('.details-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const productUrl = e.target.dataset.productUrl;
                    if (productUrl) {
                        Telegram.WebApp.openLink(productUrl);
                    } else {
                        console.warn('Предупреждение: URL продукта отсутствует для ссылки "Подробнее".');
                    }
                });
            });
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
            if (cartTotalElement) cartTotalElement.textContent = '0.00 р.';
            const cartActionsBottom = document.querySelector('.cart-actions-bottom');
            if (cartActionsBottom) cartActionsBottom.classList.add('hidden');
            if (continueShoppingButton) continueShoppingButton.classList.add('hidden');
            return;
        } else {
            const cartActionsBottom = document.querySelector('.cart-actions-bottom');
            if (cartActionsBottom) cartActionsBottom.classList.remove('hidden');
            if (continueShoppingButton) continueShoppingButton.classList.remove('hidden');
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
                    <p class="cart-item-price">${item.price} BYN за шт.</p>
                    <div class="cart-item-controls">
                        <button class="quantity-button decrease-cart-quantity" data-product-id="${item.id}">-</button>
                        <span class="cart-item-quantity">${item.quantity}</span>
                        <button class="quantity-button increase-cart-quantity" data-product-id="${item.id}">+</button>
                        <button class="remove-btn" data-product-id="${item.id}">Удалить</button>
                    </div>
                </div>
                <div class="cart-item-total">${itemTotal.toFixed(2)} BYN</div>
            `;
            if (cartItemsList) cartItemsList.appendChild(cartItemElement);
        });

        if (cartTotalElement) cartTotalElement.textContent = `${total.toFixed(2)} р.`;

        // Добавляем обработчики для кнопок в корзине
        if (cartItemsList) {
            cartItemsList.querySelectorAll('.increase-cart-quantity').forEach(button => {
                button.addEventListener('click', (e) => updateProductQuantity(e.target.dataset.productId, 1));
            });
            cartItemsList.querySelectorAll('.decrease-cart-quantity').forEach(button => {
                button.addEventListener('click', (e) => updateProductQuantity(e.target.dataset.productId, -1));
            });
            cartItemsList.querySelectorAll('.remove-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    const productId = e.target.dataset.productId;
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
                    if (Telegram.WebApp.showAlert) {
                        Telegram.WebApp.showAlert('Ваша корзина пуста. Добавьте товары, чтобы оформить заказ.');
                    } else {
                        alert('Ваша корзина пуста. Добавьте товары, чтобы оформить заказ.');
                    }
                    return;
                }
                displayView('checkout');
            });
        } else {
            console.error('Элемент с ID "checkout-button" не найден в DOM. Невозможно прикрепить слушатель кликов.');
        }
    }

    function clearCart() {
        cart = {};
        localStorage.removeItem('cart');
        renderCart();
        updateMainButtonCartInfo();
        if (Telegram.WebApp.showAlert) {
            Telegram.WebApp.showAlert('Корзина очищена!');
        } else {
            alert('Корзина очищена!');
        }
    }

    function renderCheckoutSummary() {
        if (checkoutItemsList) checkoutItemsList.innerHTML = '';
        let total = 0;

        Object.values(cart).forEach(item => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            const checkoutItemElement = document.createElement('li');
            checkoutItemElement.className = 'checkout-item-summary';
            checkoutItemElement.textContent = `${item.name} x ${item.quantity} - ${itemTotal.toFixed(2)} BYN`;
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

                // Проверяем, не отправляется ли уже заказ
                if (isSubmitting) {
                    console.log('Заказ уже отправляется, игнорируем повторную отправку');
                    return;
                }

                isSubmitting = true; // Устанавливаем флаг отправки

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
                    isSubmitting = false; // Сбрасываем флаг при ошибке
                    if (Telegram.WebApp.showAlert) {
                        Telegram.WebApp.showAlert(errorMessages.join('\n'));
                    } else {
                        alert(errorMessages.join('\n'));
                    }
                    return;
                }

                // Проверяем, что корзина не пустая
                if (Object.keys(cart).length === 0) {
                    isSubmitting = false; // Сбрасываем флаг при ошибке
                    if (Telegram.WebApp.showAlert) {
                        Telegram.WebApp.showAlert('Корзина пуста. Пожалуйста, добавьте товары в корзину.');
                    } else {
                        alert('Корзина пуста. Пожалуйста, добавьте товары в корзину.');
                    }
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

                // Отправляем данные заказа
                Telegram.WebApp.sendData(JSON.stringify(orderPayload));

                // Показываем сообщение об успешном заказе
                if (Telegram.WebApp.showAlert) {
                    Telegram.WebApp.showAlert('Ваш заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.');
                } else {
                    alert('Ваш заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.');
                }

                // Очищаем корзину и закрываем Web App только после отправки
                clearCart();
                Telegram.WebApp.close();
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
                toggleDeliveryFields(event.target.value);
            });
        });
        const initialSelectedMethod = document.querySelector('input[name="deliveryMethod"]:checked')?.value;
        toggleDeliveryFields(initialSelectedMethod);
    } else {
        console.warn('Кнопки выбора способа доставки не найдены.');
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
                    if (!orderDetails.pickupAddress || orderDetails.pickupAddress.trim() === '') { 
                        isValid = false; 
                        errorMessages.push('Пожалуйста, выберите адрес самовывоза.'); 
                    }
                }
            }

            if (!isValid) {
                if (Telegram.WebApp.showAlert) {
                    Telegram.WebApp.showAlert(errorMessages.join('\n'));
                } else {
                    alert('Ваш заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.');
                }
                return;
            }

            // Проверяем, что корзина не пустая
            if (Object.keys(cart).length === 0) {
                if (Telegram.WebApp.showAlert) {
                    Telegram.WebApp.showAlert('Корзина пуста. Пожалуйста, добавьте товары в корзину.');
                } else {
                    alert('Корзина пуста. Пожалуйста, добавьте товары в корзину.');
                }
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


            // Отправляем данные заказа
            Telegram.WebApp.sendData(JSON.stringify(orderPayload));

            // Показываем сообщение об успешном заказе
            if (Telegram.WebApp.showAlert) {
                Telegram.WebApp.showAlert('Ваш заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.');
            } else {
                alert('Ваш заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.');
            }

            // Очищаем корзину и закрываем Web App только после отправки
            clearCart();
            Telegram.WebApp.close();
        });
    } else {
        console.error('Элемент с ID "checkout-form" не найден. Невозможно прикрепить слушатель отправки.');
    }

    function updateMainButtonCartInfo() {
        const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        const totalPrice = Object.values(cart).reduce((sum, item) => sum + (item.price * item.quantity), 0);

        if (totalItems > 0) {
            Telegram.WebApp.MainButton.setText(`🛒 Корзина (${totalItems} товаров) - ${totalPrice.toFixed(2)} р.`);
            Telegram.WebApp.MainButton.show();
        } else {
            Telegram.WebApp.MainButton.hide();
        }
    }

    const initialCategory = getUrlParameter('category');
    const initialView = getUrlParameter('view');

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

    if (Telegram.WebApp.MainButton) {
        Telegram.WebApp.MainButton.onClick(() => {
            displayView('cart');
        });
        updateMainButtonCartInfo();
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
            displayView('categories');
        });
    } else {
        console.error('Элемент с ID "start-shopping-button" не найден в DOM. Невозможно прикрепить слушатель кликов.');
    }

});
