import json
import logging
import os
from aiohttp import web
import aiohttp_cors

# Настраиваем логирование для API сервера
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Путь к файлу с данными о продуктах
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_DATA_FILE = os.path.join(BASE_DIR, 'data', 'products_scraped.json')

# Путь к директории с файлами Web App
WEB_APP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_app')
logger.info(f"API: Директория Web App: {WEB_APP_DIR}")

# Глобальная переменная для хранения данных о продуктах
products_data = {}

async def load_products_data_for_api():
    """Загружает данные о продуктах из JSON-файла для API."""
    global products_data
    if os.path.exists(PRODUCTS_DATA_FILE):
        try:
            with open(PRODUCTS_DATA_FILE, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            logger.info(f"API: Данные о продуктах успешно загружены из {PRODUCTS_DATA_FILE}.")
        except json.JSONDecodeError as e:
            logger.error(f"API: Ошибка при чтении JSON-файла '{PRODUCTS_DATA_FILE}': {e}")
            products_data = {}
        except Exception as e:
            logger.error(f"API: Неизвестная ошибка при загрузке данных о продуктах: {e}")
            products_data = {}
    else:
        logger.warning(f"API: Файл '{PRODUCTS_DATA_FILE}' не найден. API не сможет отдавать данные о продуктах.")
        products_data = {}

async def products_handler(request):
    """
    Обработчик HTTP-запросов для получения данных о продуктах.
    Принимает параметр `category` из URL.
    """
    category = request.query.get('category')
    logger.info(f"API: Получен запрос на продукты для категории: {category}")

    if not products_data:
        await load_products_data_for_api()
        if not products_data:
            logger.error("API: Данные о продуктах не загружены, не могу отдать.")
            return web.json_response({"error": "Product data not available"}, status=500)

    if category:
        if category.startswith('category_'):
            category_key = category
        else:
            category_key = f"category_{category}"

        products = products_data.get(category_key, [])
        if not products:
            logger.warning(f"API: Продукты для категории '{category_key}' не найдены.")
            return web.json_response({"error": "Category not found or empty"}, status=404)

        logger.info(f"API: Отдаю {len(products)} продуктов для категории '{category_key}'.")
        return web.json_response(products)
    else:
        logger.warning("API: Запрос продуктов без указания категории.")
        return web.json_response({"error": "Category parameter is required"}, status=400)

async def serve_main_app_page(request):
    """
    Обработчик для основного Web App (index.html).
    """
    logger.info(f"API: Serving index.html for Web App entry point: {request.path}")
    return web.FileResponse(os.path.join(WEB_APP_DIR, 'index.html'))


async def setup_api_server():
    """
    Настраивает и возвращает AppRunner для API сервера и статических файлов Web App.
    Не запускает сервер самостоятельно.
    """
    await load_products_data_for_api()

    app = web.Application()

    # 1. API маршрут
    app.router.add_get('/api/products', products_handler)

    # 2. Маршруты для основного Web App (index.html)
    # Корневой URL Replit Preview теперь ведет на index.html
    app.router.add_get('/', serve_main_app_page)
    app.router.add_get('/bot-app', serve_main_app_page)
    app.router.add_get('/bot-app/', serve_main_app_page)

    # 3. Маршрут для статических файлов Web App (CSS, JS, images) внутри /bot-app/
    app.router.add_static('/bot-app/', path=WEB_APP_DIR, name='web_app_static')

    # 4. Маршрут-заглушка для любых других путей внутри /bot-app/, которые не являются статическими файлами
    app.router.add_get('/bot-app/{tail:.*}', serve_main_app_page)


    # Настройка CORS для разрешения запросов с вашего домена Web App
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "PUT", "DELETE"]
        )
    })

    # Применяем CORS ко всем маршрутам
    for route in list(app.router.routes()):
        cors.add(route)

    runner = web.AppRunner(app)
    await runner.setup()

    logger.info("API сервер настроен.")
    return runner

if __name__ == '__main__':
    import asyncio
    async def main_api():
        runner = await setup_api_server()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        logger.info("API сервер запущен в автономном режиме на http://0.0.0.0:8080")
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass
        finally:
            await runner.cleanup()
            logger.info("API сервер остановлен.")

    asyncio.run(main_api())
