import json
import logging
import os
import time
from aiohttp import web
import aiohttp_cors
from collections import defaultdict

from bot.config import config
from bot.security_manager import security_manager

# Настраиваем логирование для API сервера
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Путь к файлу с данными о продуктах
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_DATA_FILE = os.path.join(BASE_DIR, 'data', 'products_scraped.json')

# Путь к директории с файлами Web App
WEB_APP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_app')
logger.info(f"API: Директория Web App: {WEB_APP_DIR}")

# Глобальная переменная для хранения данных о продуктах
products_data = {}

# API rate limiting store
api_rate_limit_store = defaultdict(list)

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
            products_data = {} # Сброс данных, если файл поврежден
        except Exception as e:
            logger.error(f"API: Неизвестная ошибка при загрузке данных о продуктах: {e}")
            products_data = {}
    else:
        logger.warning(f"API: Файл '{PRODUCTS_DATA_FILE}' не найден. API не сможет отдавать данные о продуктах.")
        products_data = {}

async def check_api_rate_limit(request, action: str = "api_request") -> bool:
    """Check API rate limiting."""
    if not config.ENABLE_RATE_LIMITING:
        return True
    
    # Get client IP
    client_ip = request.headers.get('X-Forwarded-For', request.remote)
    if not client_ip:
        client_ip = "unknown"
    
    current_time = time.time()
    key = f"api_{client_ip}_{action}"
    
    # Clean old entries
    api_rate_limit_store[key] = [
        timestamp for timestamp in api_rate_limit_store[key]
        if current_time - timestamp < config.RATE_LIMIT_WINDOW
    ]
    
    # Check if limit exceeded
    if len(api_rate_limit_store[key]) >= config.RATE_LIMIT_MAX_REQUESTS:
        logger.warning(f"🚫 API rate limit exceeded for IP {client_ip}, action: {action}")
        security_manager._log_security_event("api_rate_limit_exceeded", {
            "client_ip": client_ip,
            "action": action,
            "current_count": len(api_rate_limit_store[key])
        })
        return False
    
    # Add current request
    api_rate_limit_store[key].append(current_time)
    return True

async def get_products_for_webapp(request):
    """Отдает данные о продуктах для Web App, с возможностью фильтрации по категории."""
    # Check rate limiting
    if not await check_api_rate_limit(request, "get_products"):
        return web.json_response({"error": "Rate limit exceeded"}, status=429, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })
    
    category_key = request.query.get('category')
    logger.info(f"API: Запрос продуктов для категории: {category_key}")

    if not products_data:
        logger.warning("API: Данные о продуктах не загружены.")
        return web.json_response({"error": "Product data not loaded"}, status=500, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })

    if category_key:
        products_in_category = products_data.get(category_key, [])
        if not products_in_category:
            logger.warning(f"API: Категория '{category_key}' не найдена или пуста.")
            return web.json_response({"error": "Category not found or empty"}, status=404, headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            })
        return web.json_response(products_in_category, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })
    else:
        # Если категория не указана, отдаем все продукты, сгруппированные по категориям
        return web.json_response(products_data, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })

async def get_categories_for_webapp(request):
    """Отдает список категорий для Web App."""
    # Check rate limiting
    if not await check_api_rate_limit(request, "get_categories"):
        return web.json_response({"error": "Rate limit exceeded"}, status=429, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })
    
    logger.info("API: Запрос списка категорий.")
    if not products_data:
        logger.warning("API: Данные о продуктах не загружены для категорий.")
        return web.json_response({"error": "Product data not loaded"}, status=500, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })

    categories_list = []
    for key, products in products_data.items():
        if products: # Убедимся, что в категории есть продукты
            # Берем первое изображение из первого продукта в категории как изображение для категории
            category_image = products[0].get('image_url', '')
            categories_list.append({
                "key": key,
                "name": products[0].get('category_name', key), # Используем название категории из первого продукта
                "image": category_image
            })
    return web.json_response(categories_list, headers={
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    })

async def serve_main_app_page(request):
    """Отдает главный HTML файл Web App."""
    logger.info(f"API: Serving index.html for Web App entry point: {request.path}")
    return web.FileResponse(os.path.join(WEB_APP_DIR, 'index.html'))

async def setup_api_server():
    """Настраивает и возвращает AioHTTP Web Application Runner."""
    app = web.Application()

    # Загружаем данные о продуктах при настройке сервера
    await load_products_data_for_api()

    # ДОБАВЛЕНО: Перенаправление с корневого пути на '/bot-app/'
    app.router.add_get('/', lambda r: web.HTTPFound('/bot-app/'))

    # 1. Маршрут для получения всех продуктов (или по категории)
    # ИЗМЕНЕНО: Добавлен префикс '/bot-app'
    app.router.add_get('/bot-app/api/products', get_products_for_webapp)

    # 2. Маршрут для получения категорий
    # ИЗМЕНЕНО: Добавлен префикс '/bot-app'
    app.router.add_get('/bot-app/api/categories', get_categories_for_webapp)

    # 3. Маршрут для главной страницы Web App
    app.router.add_get('/bot-app/', serve_main_app_page)

    # 4. Маршрут для статических файлов Web App (CSS, JS, images) внутри /bot-app/
    # Добавляем обработчик для статических файлов с контролем кеширования
    async def serve_static_with_cache_control(request):
        """Serves static files with proper cache control headers."""
        file_path = request.match_info.get('filename', '')
        full_path = os.path.join(WEB_APP_DIR, file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            # Определяем тип содержимого на основе расширения файла
            content_type = 'text/html'
            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_path.endswith('.svg'):
                content_type = 'image/svg+xml'
            
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Check if file has version query parameter (e.g., ?v=1.2.0)
            query_string = request.query_string
            has_version = 'v=' in query_string
            
            if has_version:
                # Versioned files should be cached for a long time
                headers = {
                    'Content-Type': content_type,
                    'Cache-Control': 'public, max-age=31536000',  # 1 year
                    'ETag': f'"v{hash(full_path)}"'
                }
            else:
                # Non-versioned files should not be cached
                headers = {
                    'Content-Type': content_type,
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            
            return web.Response(body=content, headers=headers)
        else:
            return web.Response(status=404, text="File not found")
    
    # Маршрут для статических файлов с умным контролем кеширования
    app.router.add_get('/bot-app/{filename:.+\.(css|js|png|jpg|jpeg|svg|ico)}', serve_static_with_cache_control)

    # 5. Маршрут-заглушка для любых других путей внутри /bot-app/, которые не являются статическими файлами
    app.router.add_get('/bot-app/{tail:.*}', serve_main_app_page)


    # Настройка CORS для разрешения запросов с вашего домена Web App
    cors = aiohttp_cors.setup(app, defaults={
        "*" : aiohttp_cors.ResourceOptions(
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
        # Keep the server running indefinitely
        await asyncio.Event().wait() 

    asyncio.run(main_api())
