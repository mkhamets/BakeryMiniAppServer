import asyncio
import logging
import json
import os
import re

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web # Импортируем web для TCPSite

from .api_server import setup_api_server # Убедитесь, что импортируется setup_api_server
from .config import BOT_TOKEN, BASE_WEBAPP_URL
from .keyboards import back_to_menu, generate_main_menu

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=BOT_TOKEN
)
dp = Dispatcher()

# Путь к файлу с данными
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_DATA_FILE = os.path.join(BASE_DIR, 'data', 'products_scraped.json')
logger.info(f"Ожидаемый путь к файлу данных: {PRODUCTS_DATA_FILE}")


# Глобальная переменная для хранения данных о продуктах
products_data = {}

async def load_products_data():
    """Загружает данные о продуктах из JSON-файла."""
    global products_data
    if os.path.exists(PRODUCTS_DATA_FILE):
        try:
            with open(PRODUCTS_DATA_FILE, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            logger.info(f"Данные о продуктах успешно загружены из {PRODUCTS_DATA_FILE}. Найдено категорий: {len(products_data)}")
            for category, products in products_data.items():
                logger.info(f"Категория '{category}': найдено {len(products)} продуктов.")
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при чтении JSON-файла '{PRODUCTS_DATA_FILE}': {e}")
            products_data = {} # Сброс данных, если файл поврежден
        except Exception as e:
            logger.error(f"Неизвестная ошибка при загрузке данных о продуктах: {e}")
            products_data = {}
    else:
        logger.warning(f"Файл '{PRODUCTS_DATA_FILE}' не найден. Бот не сможет отдавать данные о продуктах.")
        products_data = {}

# Словарь для маппинга названий категорий на ключи в products_data
CATEGORY_MAP = {
    "🥨 Выпечка": "category_bakery",
    "🥐 Круассаны": "category_croissants",
    "🍞 Ремесленный хлеб": "category_artisan_bread",
    "🍰 Десерты": "category_desserts"
}

# Словарь для хранения корзин пользователей
user_carts = {} # user_id: {product_id: quantity, ...}

# Функция для получения корзины пользователя
def get_user_cart(user_id: int) -> dict:
    return user_carts.setdefault(user_id, {})

# Функция для обновления количества товаров в корзине
def update_cart_item_quantity(user_id: int, product_id: str, quantity: int):
    cart = get_user_cart(user_id)
    if quantity <= 0:
        if product_id in cart:
            del cart[product_id]
    else:
        cart[product_id] = quantity
    logger.info(f"Корзина пользователя {user_id} обновлена: {cart}")

# Функция для очистки корзины
def clear_user_cart(user_id: int):
    if user_id in user_carts:
        del user_carts[user_id]
    logger.info(f"Корзина пользователя {user_id} очищена.")

# ЗАГЛУШКА: Функция для очистки сообщений корзины (если она нужна)
# Если у тебя есть конкретная реализация этой функции, замени ее.
async def clear_user_cart_messages(chat_id: int):
    logger.info(f"Функция clear_user_cart_messages вызвана для чата {chat_id}. (ЗАГЛУШКА)")
    # Здесь может быть логика удаления предыдущих сообщений корзины
    pass

# Хендлер команды /start
@dp.message(F.text == "/start")
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    cart_count = sum(get_user_cart(user_id).values())
    await message.answer(
        "Привет! Я бот-помощник пекарни Дражина. Используй меню ниже, чтобы выбрать категорию товаров или узнать информацию о нас.",
        reply_markup=generate_main_menu(cart_count)
    )

# Хендлер для кнопки "О нас"
@dp.message(F.text == "ℹ️ О нас")
async def about_us(message: Message):
    await clear_user_cart_messages(message.chat.id) # Очищаем корзину, если пользователь переходит в другой раздел
    text = (
        "<b>О пекарне Дражина</b>\n\n"
        "Наша пекарня — это место, где традиции встречаются с современными технологиями. "
        "Мы готовим хлеб и выпечку по классическим рецептам, используя только натуральные ингредиенты.\n\n"
        "🌾 Ремесленный подход\n"
        "🍞 Свежайшие продукты\n"
        "❤️ Любовь к своему делу\n\n"
        "Подробнее: https://drazhin.by/o-pekarne"
    ) # Добавлена закрывающая скобка
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=back_to_menu) # Добавлен вызов answer

# Хендлер для кнопки "Наши адреса"
@dp.message(F.text == "📍 Наши адреса")
async def show_addresses(message: Message):
    await clear_user_cart_messages(message.chat.id) # Очищаем корзину, если пользователь переходит в другой раздел
    text = (
        "<b>📍 Наши магазины</b>\n\n"
        "🏬 <b>ТЦ \"Green City\"</b>\n"
        "ул. Притыцкого, 156, напротив Грин Сити\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIEUl9'>Yandex</a>\n\n"

        "🏬 <b>ТЦ \"Замок\"</b>\n"
        "пр‑т Победителей, 65, 1 этаж возле «Ив Роше»\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIEJ3Z'>Yandex</a>\n\n"

        "🏠 <b>ул. Л. Беды, 26</b>\n"
        "вход в WINE&SPIRITS\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIEXnX'>Yandex</a>\n\n"

        "🏠 <b>ул. Мстиславца, 8</b>\n"
        "в Маяк Минска, вход со двора\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIIYme'>Yandex</a>\n\n"

        "🏠 <b>ул. Лученка, 1</b>\n"
        "в ЖК «Minsk World»\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIII6lt'>Yandex</a>\n\n"

        "🏠 <b>ул. Авиационная, 8</b>\n"
        "Копище, Новая Боровая\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIIDl~'>Yandex</a>\n\n"

        "🏠 <b>ул. Нововиленская, 45</b>\n"
        "Minsk\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIIDl~'>Yandex</a>\n\n"

        "🏠 <b>ул. Морской риф 1/4</b>\n"
        "а/г Ратомка, ЖК «Пирс»\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIMRKA'>Yandex</a>\n\n"

        "🏠 <b>г. Заславль, ул. Вокзальная, 11</b>\n"
        "у ж/д станции «Беларусь»\n"
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIMOpa'>Yandex</a>\n\n"

        "<b>📞 Наши контакты:</b>\n"
        "📱 +375 (29) 117‑25‑77\n"
        "📧 info@drazhin.by\n"
        "<a href='https://drazhin.by/kontakty'>Подробнее на сайте</a>"
    ) # Добавлена закрывающая скобка
    await message.answer(text, reply_markup=back_to_menu, disable_web_page_preview=True, parse_mode=ParseMode.HTML)

# Хендлер для кнопки "О доставке"
@dp.message(F.text == "⚡ О доставке")
async def delivery_info(message: Message):
    await clear_user_cart_messages(message.chat.id) # Очищаем корзину, если пользователь переходит в другой раздел
    text = (
        "<b>🚚 Условия доставки</b>\n\n"
        "✅ Бесплатная доставка.\n"
        "❗️Минимальная сумма заказа для осуществления доставки — <b>70 рублей</b>.\n"
        "🔴 Минимальная сумма заказа для доставки в праздничные и предпраздничные дни — <b>200 рублей</b>.\n\n"
        "<b>🕒 Время доставки</b>\n"
        "Мы доставляем заказы ежедневно с <b>12:30 до 17:00</b>.\n"
        "<b>День в день</b>. Доставим товары день в день при оформлении заказа <b>до 11:00</b>.\n"
        "<b>На завтра</b>. Заказы, оформленные <b>после 11:00</b>, доставляются на следующий день.\n"
        "<b>🗺 Зона доставки</b>\n\n"
        "<a href=\"https://yandex.com/maps/157/minsk/?from=mapframe&ll=27.513432%2C53.935659&mode=usermaps&source=mapframe&um=constructor%3Acaf348232a3eb659f0e8355c6c34c51b8307a553b53ad5723ecfdb4ff43ad6da&utm_source=mapframe&z=10.6\">📍 Посмотреть карту зоны доставки</a>\n\n"
        "<b>📞 Контакты для уточнений</b>\n"
        "Телефон: +375 (29) 117‑25‑77\n"
        "📧 info@drazhin.by\n"
        "<a href='https://drazhin.by/kontakty'>Подробнее на сайте</a>"
    )
    await message.answer(text, reply_markup=back_to_menu, disable_web_page_preview=True, parse_mode=ParseMode.HTML)

# Хендлер для кнопки "Назад в меню"
@dp.message(F.text == "⬅️ Назад в меню")
async def back_to_menu_handler(message: Message) -> None:
    user_id = message.from_user.id
    cart_count = sum(get_user_cart(user_id).values())
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=generate_main_menu(cart_count)
    )

# Хендлер для данных из Web App
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    user_id = message.from_user.id
    web_app_data_raw = message.web_app_data.data
    logger.info(f"Получены данные из Web App для пользователя {user_id}: {web_app_data_raw}")

    try:
        data = json.loads(web_app_data_raw)
        action = data.get('action')

        if action == 'update_cart':
            cart_items = data.get('cart', [])
            current_cart = get_user_cart(user_id)

            # Очищаем корзину перед обновлением, чтобы избежать устаревших данных
            clear_user_cart(user_id)

            for item in cart_items:
                product_id = item.get('id')
                quantity = item.get('quantity')
                if product_id and quantity is not None:
                    update_cart_item_quantity(user_id, product_id, quantity)

            cart_count = sum(get_user_cart(user_id).values())
            await message.answer(
                f"Корзина обновлена. Товаров в корзине: {cart_count}.",
                reply_markup=generate_main_menu(cart_count)
            )
            logger.info(f"Корзина пользователя {user_id} успешно обновлена из Web App. Текущая корзина: {get_user_cart(user_id)}")

        elif action == 'checkout_order':
            order_details = data.get('order_details')
            cart_items = data.get('cart_items')
            total_amount = data.get('total_amount')

            if order_details and cart_items and total_amount is not None:
                # Формируем сообщение для администратора или для подтверждения пользователю
                order_summary = "Новый заказ:\n"
                order_summary += f"Фамилия: {order_details.get('lastName', 'Не указано')}\n"
                order_summary += f"Имя: {order_details.get('firstName', 'Не указано')}\n"
                order_summary += f"Отчество: {order_details.get('middleName', 'Не указано')}\n"
                order_summary += f"Телефон: {order_details.get('phone', 'Не указан')}\n"
                order_summary += f"Email: {order_details.get('email', 'Не указан')}\n"
                order_summary += f"Дата доставки/самовывоза: {order_details.get('deliveryDate', 'Не указано')}\n"
                order_summary += f"Способ получения: {order_details.get('deliveryMethod', 'Не указан')}\n"

                if order_details.get('deliveryMethod') == 'courier':
                    order_summary += f"Город: {order_details.get('city', 'Не указан')}\n"
                    order_summary += f"Адрес доставки: {order_details.get('addressLine', 'Не указан')}\n"
                    order_summary += f"Комментарий: {order_details.get('comment', 'Нет')}\n"
                elif order_details.get('deliveryMethod') == 'pickup':
                    order_summary += f"Адрес самовывоза: {order_details.get('pickupAddress', 'Не указан')}\n"


                order_summary += "\nСостав заказа:\n"
                for item in cart_items:
                    order_summary += f"- {item.get('name')} x {item.get('quantity')} шт. ({item.get('price')} BYN/шт.)\n"
                order_summary += f"\nОбщая сумма: {total_amount} BYN"

                await message.answer(
                    f"Ваш заказ принят! Мы свяжемся с вами в ближайшее время для подтверждения.\n\n{order_summary}",
                    reply_markup=back_to_menu # Возвращаем пользователя в главное меню после заказа
                )
                clear_user_cart(user_id) # Очищаем корзину после успешного заказа
                logger.info(f"Заказ от пользователя {user_id} успешно оформлен. Корзина очищена.")
            else:
                await message.answer("Ошибка при оформлении заказа. Пожалуйста, попробуйте снова.", reply_markup=back_to_menu)
                logger.error(f"Неполные данные заказа от пользователя {user_id}: {data}")
        else:
            await message.answer("Неизвестное действие из Web App.", reply_markup=back_to_menu)
            logger.warning(f"Получено неизвестное действие из Web App для пользователя {user_id}: {action}")

    except json.JSONDecodeError:
        logger.error(f"Неверный формат JSON данных из Web App для пользователя {user_id}: {web_app_data_raw}")
        await message.answer("Ошибка обработки данных из Web App. Пожалуйста, попробуйте снова.", reply_markup=back_to_menu)
    except Exception as e:
        logger.error(f"Неизвестная ошибка при обработке данных из Web App для пользователя {user_id}: {e}")
        await message.answer("Произошла внутренняя ошибка. Пожалуйста, попробуйте позже.", reply_markup=back_to_menu)


# Хендлер для текстового ввода, который не является командой или кнопкой
@dp.message(F.text)
async def block_text_input(message: Message):
    if message.text not in CATEGORY_MAP.keys() and \
       message.text not in ["ℹ️ О нас", "📍 Наши адреса", "⚡ О доставке", "⬅️ Назад в меню"] and \
       not re.match(r"🛒 Корзина(\s\(\d+\))?", message.text) and \
       message.text != "/start":
        await message.answer("⚠️ Пожалуйста, используйте кнопки внизу для управления ботом �")


async def main():
    logger.info("Загрузка данных о продуктах при запуске бота...")
    await load_products_data()

    # Включение хендлера для Web App данных
    dp.message.register(handle_web_app_data, F.web_app_data)

    # Настраиваем API сервер
    # ИЗМЕНЕНО: setup_api_server теперь только настраивает runner
    runner = await setup_api_server()
    port = int(os.environ.get("PORT", 8080)) # Получаем порт из переменных окружения или используем 8080
    site = web.TCPSite(runner, '0.0.0.0', port) # Создаем TCPSite
    await site.start() # Запускаем TCPSite только здесь
    logger.info(f"API сервер запущен на http://0.0.0.0:{port}")

    # Запускаем бота и API сервер одновременно
    bot_polling_task = asyncio.create_task(dp.start_polling(bot))

    try:
        await bot_polling_task
    except asyncio.CancelledError:
        pass
    finally:
        # Очистка ресурсов runner при завершении работы бота
        await runner.cleanup()
        logger.info("API сервер остановлен.")

if __name__ == '__main__':
    asyncio.run(main())
