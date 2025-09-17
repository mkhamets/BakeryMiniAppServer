from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from .config import SecureConfig

# Получаем URL из конфигурации
config = SecureConfig()
BASE_WEBAPP_URL = config.BASE_WEBAPP_URL

# Удалена клавиатура для возврата в меню (back_to_menu)

def generate_main_menu(cart_items_count: int = 0) -> InlineKeyboardMarkup:
    """
    Генерирует главное меню (inline) с учетом количества товаров в корзине.
    """
    cart_button_text = (
        f"🛒 Проверить корзину ({cart_items_count})" if cart_items_count > 0 else "🛒 Проверить корзину"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Наше меню",
                web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?view=categories")
            )
        ],
        [
            InlineKeyboardButton(
                text=cart_button_text,
                web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?view=cart")
            )
        ],
        [
            InlineKeyboardButton(text="Наши адреса", callback_data="info:addresses"),
            InlineKeyboardButton(text="О доставке", callback_data="info:delivery"),
            InlineKeyboardButton(text="О нас", callback_data="info:about"),
        ]
    ])
    return keyboard

# Примечание: Кнопка "Оформить заказ" теперь обрабатывается в main.py через callback_query
# и открывает WebApp с параметром ?view=checkout
