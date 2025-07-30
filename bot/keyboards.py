from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from .config import BASE_WEBAPP_URL  # Убедись, что эта переменная есть в config.py

def generate_main_menu(cart_count: int = 0) -> ReplyKeyboardMarkup:
    cart_text = f"🛒 Корзина ({cart_count})" if cart_count > 0 else "🛒 Корзина"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🥨 Выпечка",
                    web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?category=bakery&v=2")
                ),
                KeyboardButton(
                    text="🥐 Круассаны",
                    web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?category=croissants&v=2")
                )
            ],
            [
                KeyboardButton(
                    text="🍞 Ремесленный хлеб",
                    web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?category=artisan_bread&v=2")
                ),
                KeyboardButton(
                    text="🍰 Десерты",
                    web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?category=desserts&v=2")
                )
            ],
            [
                KeyboardButton(
                    text=cart_text,
                    web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?category=cart&v=2")
                )
            ],
            [
                KeyboardButton(text="📍 Наши адреса"),
                KeyboardButton(text="⚡ О доставке"),
                KeyboardButton(text="ℹ️ О нас")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите категорию или действие ⬇️"
    )

back_to_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад в меню")]
    ],
    resize_keyboard=True,
    is_persistent=True,
    one_time_keyboard=False,
    input_field_placeholder="Вернуться в главное меню ⬇️"
)