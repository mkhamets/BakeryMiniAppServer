from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Базовый URL для Web App. Он должен быть таким же, как в main.py и BotFather.
# Убедитесь, что он заканчивается на '/bot-app/'
BASE_WEBAPP_URL = "https://bakery-mini-app-server-440955f475ad.herokuapp.com/bot-app/"

# Удалена клавиатура для возврата в меню (back_to_menu)

def generate_main_menu(cart_items_count: int = 0) -> ReplyKeyboardMarkup:
    """
    Генерирует главное меню с учетом количества товаров в корзине.
    """
    cart_button_text = f"🛒 Проверить корзину ({cart_items_count})" if cart_items_count > 0 else "🛒 Проверить корзину"

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Наше меню", web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?view=categories"))
            ],
            [
                KeyboardButton(text=cart_button_text, web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?view=cart"))
            ],
            [
                KeyboardButton(text="Наши адреса"),
                KeyboardButton(text="О доставке"),
                KeyboardButton(text="О нас")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True, # Добавлено обратно
        one_time_keyboard=False,
        input_field_placeholder="Выберите категорию или действие ⬇️" # Добавлено обратно
    )
    return keyboard

# Примечание: Кнопка "Оформить заказ" теперь обрабатывается в main.py через callback_query
# и открывает WebApp с параметром ?view=checkout
