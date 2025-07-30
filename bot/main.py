import asyncio
import logging
import json # Добавлен импорт json
import os
import re

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web # Импортируем web для TCPSite

from .api_server import setup_api_server
from .config import BOT_TOKEN, BASE_WEBAPP_URL # Добавлен BASE_WEBAPP_URL
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
            products_data = {}
        except Exception as e:
            logger.error(f"Неизвестная ошибка при загрузке данных о продуктах: {e}")
            products_data = {}
    else:
        logger.warning(f"Файл '{PRODUCTS_DATA_FILE}' не найден. Пожалуйста, запустите парсер.")
        products_data = {}


# Хранилище корзин по пользователям
# Ключ: chat_id, Значение: {
#   'items': { product_unique_id: {id, name, price, quantity, ...} },
#   'message_ids': [],
#   'summary_message_id': None
# }
cart_state = {}

# Функция для извлечения числового значения цены
def parse_price(price_str):
    if not price_str or is_na(price_str):
        return 0.0
    cleaned_price = re.sub(r'[^\d,.]', '', str(price_str)).replace(',', '.')
    try:
        return float(cleaned_price)
    except ValueError:
        logger.warning(f"Не удалось распарсить цену: {price_str} (очищенная: {cleaned_price})")
        return 0.0

# Функция для проверки значения на N/A (с учетом регистра и пробелов)
def is_na(value):
    return not value or str(value).strip().lower() == 'n/a'

# Функции для работы с product_unique_id
def get_product_unique_id(category_key, index):
    return f"{category_key}_{index}"

def get_product_data_from_id(product_id):
    parts = product_id.split('_')
    if len(parts) >= 2 and parts[-1].isdigit():
        product_index = int(parts[-1])
        category_key = "_".join(parts[:-1])

        if category_key in products_data and 0 <= product_index < len(products_data[category_key]):
            return products_data[category_key][product_index], category_key, product_index
    return None, None, None


# Вспомогательная функция для удаления всех сообщений корзины пользователя
async def clear_user_cart_messages(chat_id: int):
    # Удаляем итоговое сообщение, если оно есть
    if chat_id in cart_state and 'summary_message_id' in cart_state[chat_id] and cart_state[chat_id]['summary_message_id']:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=cart_state[chat_id]['summary_message_id'])
        except Exception as e:
            logger.warning(f"Не удалось удалить итоговое сообщение корзины {cart_state[chat_id]['summary_message_id']} для пользователя {chat_id}: {e}")
        del cart_state[chat_id]['summary_message_id'] # Очищаем после попытки удаления

    # Удаляем сообщения отдельных товаров
    if chat_id in cart_state and 'message_ids' in cart_state[chat_id]:
        for message_id in cart_state[chat_id]['message_ids']:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение {message_id} для пользователя {chat_id}: {e}")
        cart_state[chat_id]['message_ids'] = [] # Очищаем список после удаления


# Вспомогательная функция для получения актуального количества товаров в корзине (для счетчика)
def get_current_cart_items_count(chat_id: int) -> int:
    if chat_id not in cart_state or 'items' not in cart_state[chat_id]:
        return 0
    # Суммируем quantity из объектов товаров в корзине
    return sum(item['quantity'] for item in cart_state[chat_id]['items'].values())


# Вспомогательная функция для отправки/обновления итогового сообщения корзины
async def send_or_update_overall_cart_summary(chat_id: int):
    # Получаем актуальное состояние корзины
    cart_items = cart_state.get(chat_id, {}).get('items', {})

    total_price = 0.0
    # Итерируем только по элементам корзины, которые являются продуктами
    for product_id, item_data in cart_items.items():
        if item_data['quantity'] > 0: # Убедимся, что количество больше 0
            total_price += item_data['price'] * item_data['quantity']

    # Кнопки для общего сообщения корзины - кнопка "Назад в меню" удалена
    overall_cart_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="proceed_to_checkout")],
        [InlineKeyboardButton(text="🧹 Очистить корзину", callback_data="clear_cart")]
    ])

    summary_text = f"<b>💰 Общая сумма: {total_price:.2f} р.</b>"

    summary_message_id = cart_state[chat_id].get('summary_message_id')

    try:
        if summary_message_id:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=summary_message_id,
                text=summary_text,
                reply_markup=overall_cart_keyboard,
                parse_mode=ParseMode.HTML
            )
        else:
            sent_message = await bot.send_message(
                chat_id=chat_id,
                text=summary_text,
                reply_markup=overall_cart_keyboard,
                parse_mode=ParseMode.HTML
            )
            cart_state[chat_id]['summary_message_id'] = sent_message.message_id
            cart_state[chat_id]['message_ids'].append(sent_message.message_id) # Добавляем в общий список для удаления

    except Exception as e:
        logger.error(f"Ошибка при обновлении/отправке итогового сообщения корзины для {chat_id}: {e}")


@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_id = message.from_user.id
    # Инициализируем корзину для нового пользователя, если ее нет
    if user_id not in cart_state:
        cart_state[user_id] = {'items': {}, 'message_ids': [], 'summary_message_id': None}

    current_cart_count = get_current_cart_items_count(user_id)

    await message.answer(
        "👋 <b>Добро пожаловать в пекарню Дражина!</b>\n"
        "Выберите категорию или действие ниже 👇",
        reply_markup=generate_main_menu(current_cart_count),
        parse_mode=ParseMode.HTML
    )

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
    )
    await message.answer(text, reply_markup=back_to_menu, parse_mode=ParseMode.HTML)

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
        "🔗 <a href='http://maps.google.com/maps?q=53.9006,27.5670'>Google</a> | <a href='https://yandex.com/maps/-/CHTIMU9Q'>Yandex</a>\n"
    )
    await message.answer(text, reply_markup=back_to_menu, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

@dp.message(F.text == "⚡ О доставке")
async def show_delivery_info(message: Message):
    await clear_user_cart_messages(message.chat.id) # Очищаем корзину, если пользователь переходит в другой раздел
    text = (
        "<b>⚡ Информация о доставке</b>\n\n"
        "<b>Курьерская доставка:</b>\n"
        "Минимальная сумма заказа для доставки курьером - <b>70 рублей</b>.\n"
        "В праздничные и предпраздничные дни - <b>200 рублей</b>.\n"
        "Доставка осуществляется ежедневно во временном промежутке с <b>12:30 до 17:00</b>, за исключением праздничных дней.\n\n"
        "<b>Самовывоз:</b>\n"
        "Заказ на самовывоз оформляется в день покупки и формируется после произведения оплаты посредством системы ЕРИП.\n"
        "Время готовности заказа и его поступление в пункт самовывоза можно уточнить по телефону: "
        "<a href='tel:+375291172577'>+375 (29) 117-25-77</a>\n\n"
        "Подробнее о доставке: https://drazhin.by/delivery"
    )
    await message.answer(text, reply_markup=back_to_menu, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@dp.message(F.text == "⬅️ Назад в меню")
async def back_to_main(message: Message):
    user_id = message.from_user.id
    current_cart_count = get_current_cart_items_count(user_id)
    await clear_user_cart_messages(message.chat.id) # Очищаем старые сообщения корзины
    await message.answer(
        "Выберите категорию или действие 👇",
        reply_markup=generate_main_menu(current_cart_count)
    )

@dp.callback_query(F.data == "proceed_to_checkout")
async def handle_proceed_to_checkout(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in cart_state or not cart_state[user_id]['items']:
        await callback.answer("Ваша корзина пуста!", show_alert=True)
        return

    # Очищаем все предыдущие сообщения корзины перед открытием Web App для оформления
    await clear_user_cart_messages(callback.message.chat.id)

    await callback.answer() # Отвечаем на callbackQuery, чтобы убрать "часики"

    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="Переходим к оформлению заказа...",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Оформить заказ в Web App", web_app=WebAppInfo(url=f"{BASE_WEBAPP_URL}?view=checkout"))]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Нажмите 'Оформить заказ в Web App'"
        )
    )

@dp.callback_query(F.data == "clear_cart")
async def handle_clear_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    cart_state[user_id]['items'] = {} # Очищаем корзину в состоянии бота
    await clear_user_cart_messages(callback.message.chat.id) # Удаляем все сообщения корзины

    current_cart_count = get_current_cart_items_count(user_id)
    await callback.answer("Корзина очищена!", show_alert=True)
    # Обновляем главное меню с пустым счетчиком корзины
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="Ваша корзина пуста.",
        reply_markup=generate_main_menu(current_cart_count)
    )


@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    user_id = message.from_user.id
    # Ensure cart_state for the user is initialized
    if user_id not in cart_state:
        cart_state[user_id] = {'items': {}, 'message_ids': [], 'summary_message_id': None}

    try:
        web_app_data = json.loads(message.web_app_data.data)
        data_type = web_app_data.get('type')
        logger.info(f"Получены данные из Web App для пользователя {user_id}, тип: {data_type}")

        if data_type == 'order_submission':
            order_items = web_app_data.get('items', [])
            total_price = web_app_data.get('totalPrice', '0.00')
            delivery_method = web_app_data.get('deliveryMethod', 'Не указан')

            # Формируем сообщение о заказе
            order_summary = f"<b>Новый заказ от {web_app_data.get('firstName')} {web_app_data.get('lastName')}</b>\n"
            order_summary += f"Телефон: <code>{web_app_data.get('phoneNumber')}</code>\n"
            order_summary += f"Email: <code>{web_app_data.get('email')}</code>\n"
            order_summary += f"Дата доставки: {web_app_data.get('deliveryDate')}\n"
            order_summary += f"Способ доставки: {delivery_method}\n"

            if delivery_method == 'courier':
                order_summary += f"Город: {web_app_data.get('city')}\n"
                order_summary += f"Адрес: {web_app_data.get('addressLine')}\n"
            else: # pickup
                order_summary += f"Адрес самовывоза: {web_app_data.get('pickupAddress')}\n"

            if web_app_data.get('comment'):
                order_summary += f"Комментарий: {web_app_data.get('comment')}\n"

            order_summary += "\n<b>Состав заказа:</b>\n"
            for item in order_items:
                order_summary += f"- {item.get('name')} ({item.get('quantity')} шт.) - {item.get('lineTotal'):.2f} р.\n"
            order_summary += f"\n<b>Итого: {total_price} р.</b>"

            # Отправляем подтверждение пользователю
            await message.answer(
                "✅ Ваш заказ успешно оформлен! Мы свяжемся с вами в ближайшее время для подтверждения.\n\n"
                f"<b>Детали заказа:</b>\n{order_summary}",
                parse_mode=ParseMode.HTML
            )
            # Очищаем корзину пользователя в состоянии бота после успешного заказа
            cart_state[user_id]['items'] = {}
            await clear_user_cart_messages(user_id) # Удаляем сообщения корзины

            # Обновляем главное меню с пустым счетчиком корзины
            current_cart_count = get_current_cart_items_count(user_id)
            await message.answer(
                "Выберите категорию или действие �",
                reply_markup=generate_main_menu(current_cart_count)
            )

            logger.info(f"Заказ от пользователя {user_id} успешно обработан.")

        elif data_type == 'cart_sync':
            # NEW: Handle cart synchronization
            new_cart_items_list = web_app_data.get('items', [])

            # Преобразуем список элементов в словарь для удобства хранения
            # Убеждаемся, что price - это число
            updated_cart_items = {}
            for item in new_cart_items_list:
                item_id = item.get('id')
                if item_id:
                    # Попытка преобразовать цену в float, если она строка
                    try:
                        item_price = float(item.get('price', 0))
                    except (ValueError, TypeError):
                        item_price = 0.0 # Fallback
                        logger.warning(f"Не удалось распарсить цену для элемента {item_id}: {item.get('price')}")

                    updated_cart_items[item_id] = {
                        'id': item_id,
                        'name': item.get('name', 'Неизвестный товар'),
                        'price': item_price,
                        'quantity': item.get('quantity', 0),
                        'image_url': item.get('image_url'),
                        'url': item.get('url'),
                        'weight': item.get('weight'),
                        'availability_days': item.get('availability_days')
                    }

            cart_state[user_id]['items'] = updated_cart_items
            logger.info(f"Корзина синхронизирована для пользователя {user_id}. Количество товаров: {len(updated_cart_items)}")

            # Обновляем главное меню клавиатуры с новым счетчиком корзины
            current_cart_count = get_current_cart_items_count(user_id)
            # Отправляем сообщение с обновленной клавиатурой.
            # Это сообщение будет видно в чате, когда Web App закроется.
            await bot.send_message(
                chat_id=user_id,
                text="🛒 Ваша корзина обновлена.", # Можно сделать более нейтральное сообщение или не отправлять его
                reply_markup=generate_main_menu(current_cart_count),
                parse_mode=ParseMode.HTML
            )
            # Можно также удалить предыдущее сообщение с Web App кнопкой, если оно было
            # Но это может быть сложно, так как ID сообщения Web App не всегда доступен напрямую.

        else:
            logger.warning(f"Неизвестный тип данных из Web App: {data_type}")
            await message.answer("Получены неизвестные данные из Web App.")

    except json.JSONDecodeError:
        logger.error(f"Некорректные JSON данные из Web App: {message.web_app_data.data}")
        await message.answer("Произошла ошибка при обработке данных из Web App. Пожалуйста, попробуйте снова.")
    except Exception: # Changed to log the exception
        logger.exception("Непредвиденная ошибка в handle_web_app_data") # Log full traceback
        await message.answer(
            "Произошла непредвиденная ошибка при обработке вашего заказа. Пожалуйста, свяжитесь с поддержкой."
        )


# Словарь для маппинга названий категорий в боте на ключи в JSON-файле
# ПЕРЕМЕЩЕНО В ГЛОБАЛЬНУЮ ОБЛАСТЬ ВИДИМОСТИ
CATEGORY_MAP = {
    "🥨 Выпечка": "bakery",
    "🥐 Круассаны": "croissants",
    "🍞 Ремесленный хлеб": "artisan_bread",
    "🍰 Десерты": "desserts",
    "🛒 Корзина": "cart"
}

# Хендлер для блокировки любого текстового ввода, который не является командой или кнопкой
@dp.message(F.text)
async def block_text_input(message: Message):
    # Проверяем, является ли текст одной из известных категорий или команд
    # CATEGORY_MAP.keys() содержит строковые названия категорий, например "bakery"
    # generate_main_menu возвращает ReplyKeyboardMarkup, поэтому нужно проверять текст кнопок
    known_texts = set(CATEGORY_MAP.keys())
    known_texts.update(["ℹ️ О нас", "📍 Наши адреса", "⚡ О доставке", "⬅️ Назад в меню", "/start"])

    # Проверяем, соответствует ли текст формату кнопки корзины
    is_cart_button_text = re.match(r"🛒 Корзина(\s\(\d+\))?", message.text)

    if message.text not in known_texts and not is_cart_button_text:
        await message.answer("⚠️ Пожалуйста, используйте кнопки внизу для управления ботом 👇")


async def main():
    logger.info("Загрузка данных о продуктах при запуске бота...")
    await load_products_data()

    # Включение хендлера для Web App данных
    dp.message.register(handle_web_app_data, F.web_app_data)

    # Настраиваем API сервер
    runner = await setup_api_server()
    port = int(os.environ.get("PORT", 8080)) # Получаем порт из переменных окружения или используем 8080
    site = web.TCPSite(runner, '0.0.0.0', port) # Используем полученный порт
    await site.start()
    logger.info(f"API сервер запущен на http://0.0.0.0:{port}")

    # Запускаем бота и API сервер одновременно
    bot_polling_task = asyncio.create_task(dp.start_polling(bot))

    try:
        await bot_polling_task
    except asyncio.CancelledError:
        logger.info("Бот остановлен из-за отмены задачи.")
    finally:
        # Остановка API сервера при завершении работы бота
        await runner.cleanup()
        logger.info("API сервер остановлен.")

if __name__ == '__main__':
    asyncio.run(main())