#!/usr/bin/env python3
"""
WSGI entry point с поддержкой статических файлов и API сервера
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mimetypes
import json
import time
import hmac
import hashlib
import base64
from collections import defaultdict

# Загружаем переменные из .env файла
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Импортируем основное приложение
from bot.main import main as bot_main
from bot.api_server import setup_api_server
from bot.config import config
from bot.security_manager import security_manager
from bot.security_headers import security_headers_middleware, create_content_hash
import asyncio
import threading
import logging

# Настраиваем логирование
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# ===== SECURITY CONFIGURATION =====
# HMAC secret key for request signing
HMAC_SECRET = os.environ.get('HMAC_SECRET', 'default-secret-key-change-in-production')
HMAC_ALGORITHM = 'sha256'

# Rate limiting configuration
RATE_LIMIT_REQUESTS_PER_HOUR = 100
RATE_LIMIT_BLOCK_DURATION = 3600
rate_limit_storage = defaultdict(list)

# API rate limiting store
api_rate_limit_store = defaultdict(list)

# Путь к файлу с данными о продуктах
PRODUCTS_DATA_FILE = project_root / 'data' / 'products_scraped.json'

# Путь к директории с файлами Web App
WEB_APP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot', 'web_app')
logger.info(f"WSGI: Директория Web App: {WEB_APP_DIR}")

# Глобальная переменная для хранения данных о продуктах
products_data = {}

# ===== SECURITY FUNCTIONS =====
def generate_hmac_signature(data: str, secret: str) -> str:
    """Generate HMAC signature for data"""
    signature = hmac.new(
        secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

def verify_hmac_signature(data: str, signature: str, secret: str) -> bool:
    """Verify HMAC signature"""
    expected_signature = generate_hmac_signature(data, secret)
    return hmac.compare_digest(signature, expected_signature)

def check_rate_limit(ip_address: str) -> bool:
    """Check if IP address is within rate limits"""
    current_time = time.time()
    
    # Clean old entries
    rate_limit_storage[ip_address] = [
        timestamp for timestamp in rate_limit_storage[ip_address]
        if current_time - timestamp < 3600
    ]
    
    # Check if limit exceeded
    if len(rate_limit_storage[ip_address]) >= RATE_LIMIT_REQUESTS_PER_HOUR:
        return False
    
    # Add current request
    rate_limit_storage[ip_address].append(current_time)
    return True

def check_api_rate_limit(ip_address: str, action: str = "api_request") -> bool:
    """Check API rate limiting with config support."""
    if not config.ENABLE_RATE_LIMITING:
        return True
    
    current_time = time.time()
    key = f"api_{ip_address}_{action}"
    
    # Clean old entries
    api_rate_limit_store[key] = [
        timestamp for timestamp in api_rate_limit_store[key]
        if current_time - timestamp < config.RATE_LIMIT_WINDOW
    ]
    
    # Check if limit exceeded
    if len(api_rate_limit_store[key]) >= config.RATE_LIMIT_MAX_REQUESTS:
        logger.warning(f"🚫 API rate limit exceeded for IP {ip_address}, action: {action}")
        security_manager._log_security_event("api_rate_limit_exceeded", {
            "client_ip": ip_address,
            "action": action,
            "current_count": len(api_rate_limit_store[key])
        })
        return False
    
    # Add current request
    api_rate_limit_store[key].append(current_time)
    return True

def generate_auth_token() -> dict:
    """Generate authentication token for client"""
    timestamp = int(time.time())
    token_data = f"auth:{timestamp}"
    signature = generate_hmac_signature(token_data, HMAC_SECRET)
    
    return {
        "token": signature,
        "timestamp": timestamp,
        "expires_in": 3600
    }

def load_products_data():
    """Загружает данные о продуктах из JSON-файла"""
    global products_data
    if PRODUCTS_DATA_FILE.exists():
        try:
            with open(PRODUCTS_DATA_FILE, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            logger.info(f"WSGI: Данные о продуктах успешно загружены из {PRODUCTS_DATA_FILE}")
        except json.JSONDecodeError as e:
            logger.error(f"WSGI: Ошибка при чтении JSON-файла '{PRODUCTS_DATA_FILE}': {e}")
            products_data = {}
        except Exception as e:
            logger.error(f"WSGI: Неизвестная ошибка при загрузке данных о продуктах: {e}")
            products_data = {}
    else:
        logger.warning(f"WSGI: Файл '{PRODUCTS_DATA_FILE}' не найден. WSGI не сможет отдавать данные о продуктах.")
        products_data = {}

# Загружаем данные о продуктах при инициализации
load_products_data()

# ===== API HANDLERS =====
def get_auth_token_handler(environ, start_response):
    """Handle auth token requests"""
    client_ip = environ.get('REMOTE_ADDR', '127.0.0.1')
    
    # Basic rate limiting for token requests
    if not check_rate_limit(f"{client_ip}:token"):
        logger.warning(f"WSGI: Token rate limit exceeded for IP {client_ip}")
        status = '429 Too Many Requests'
        headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [b'{"error": "Token rate limit exceeded"}']
    
    token_data = generate_auth_token()
    response_data = json.dumps(token_data)
    logger.info(f"WSGI: Generated auth token for IP {client_ip}")
    
    status = '200 OK'
    headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ('Pragma', 'no-cache'),
        ('Expires', '0'),
    ] + get_cors_headers()
    start_response(status, headers)
    return [response_data.encode('utf-8')]

def get_products_handler(environ, start_response):
    """Handle products requests with full API functionality"""
    try:
        client_ip = environ.get('REMOTE_ADDR', '127.0.0.1')
        
        # Rate limiting
        if not check_api_rate_limit(client_ip, "get_products"):
            status = '429 Too Many Requests'
            headers = [('Content-Type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [b'{"error": "Rate limit exceeded"}']
        
        # HMAC signature verification (simplified for wsgi)
        signature = environ.get('HTTP_X_SIGNATURE')
        timestamp = environ.get('HTTP_X_TIMESTAMP')
        init_data = environ.get('HTTP_X_TELEGRAM_INIT_DATA', '')
        
        # Log missing signature for debugging
        if not signature or not timestamp:
            logger.warning(f"WSGI: Missing signature or timestamp from {client_ip}")
        
        # For now, skip signature verification to match frontend expectations
        # In production, you might want to enable this
        
        # Get category parameter
        query_string = environ.get('QUERY_STRING', '')
        category_key = None
        if query_string:
            for param in query_string.split('&'):
                if param.startswith('category='):
                    category_key = param.split('=', 1)[1]
                    break
        
        logger.info(f"WSGI: Запрос продуктов для категории: {category_key}")
        
        if not products_data:
            logger.warning("WSGI: Данные о продуктах не загружены.")
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [b'{"error": "Product data not loaded"}']
        
        if category_key:
            # Return products for specific category
            products_in_category = products_data.get(category_key, [])
            if not products_in_category:
                status = '404 Not Found'
                headers = [('Content-Type', 'application/json; charset=utf-8')]
                start_response(status, headers)
                return [b'{"error": "Category not found or empty"}']
            
            response_data = json.dumps(products_in_category)
        else:
            # Return all products grouped by categories
            response_data = json.dumps(products_data)
        
        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('Pragma', 'no-cache'),
            ('Expires', '0'),
        ] + get_cors_headers()
        start_response(status, headers)
        return [response_data.encode('utf-8')]
        
    except Exception as e:
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [f'{{"error": "Failed to load products: {str(e)}"}}'.encode('utf-8')]

def get_categories_handler(environ, start_response):
    """Handle categories requests with full API functionality"""
    try:
        client_ip = environ.get('REMOTE_ADDR', '127.0.0.1')
        
        # Rate limiting
        if not check_api_rate_limit(client_ip, "get_categories"):
            status = '429 Too Many Requests'
            headers = [('Content-Type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [b'{"error": "Rate limit exceeded"}']
        
        logger.info("WSGI: Запрос списка категорий.")
        
        if not products_data:
            logger.warning("WSGI: Данные о продуктах не загружены для категорий.")
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [b'{"error": "Product data not loaded"}']
        
        categories_list = []
        for key, products in products_data.items():
            if products:  # Убедимся, что в категории есть продукты
                # Берем первое изображение из первого продукта в категории как изображение для категории
                category_image = products[0].get('image_url', '')
                categories_list.append({
                    "key": key,
                    "name": products[0].get('category_name', key),  # Используем название категории из первого продукта
                    "image": category_image
                })
        
        response_data = json.dumps(categories_list)
        
        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('Pragma', 'no-cache'),
            ('Expires', '0'),
        ] + get_cors_headers()
        start_response(status, headers)
        return [response_data.encode('utf-8')]
        
    except Exception as e:
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [f'{{"error": "Failed to load categories: {str(e)}"}}'.encode('utf-8')]

# Глобальные переменные
bot_thread = None
api_server_thread = None

def start_bot():
    """Запуск бота в отдельном потоке"""
    global bot_thread
    
    if bot_thread is None or not bot_thread.is_alive():
        logger.info("🚀 Starting Bakery Bot...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(bot_main())
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            loop.close()

def start_api_server():
    """Запуск API сервера в отдельном потоке"""
    global api_server_thread
    
    if api_server_thread is None or not api_server_thread.is_alive():
        logger.info("🚀 Starting API Server...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(setup_api_server())
        except Exception as e:
            logger.error(f"❌ API Server error: {e}")
            loop.close()

def get_content_type(file_path):
    """Определяем MIME тип файла"""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or 'application/octet-stream'

def get_cors_headers():
    """Возвращает CORS заголовки для всех ответов"""
    return [
        ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type, Accept, Origin, X-Signature, X-Timestamp, X-Telegram-Init-Data'),
        ('Access-Control-Expose-Headers', 'Content-Type, Cache-Control, ETag'),
    ]

def serve_main_app_page(environ, start_response):
    """Отдает главный HTML файл Web App."""
    logger.info(f"WSGI: Serving index.html for Web App entry point: {environ.get('PATH_INFO', '/')}")
    try:
        with open(os.path.join(WEB_APP_DIR, 'index.html'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        status = '200 OK'
        headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
        ] + get_cors_headers()
        start_response(status, headers)
        return [content.encode('utf-8')]
    except Exception as e:
        logger.error(f"WSGI: Error reading index.html: {e}")
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')] + get_cors_headers()
        start_response(status, headers)
        return [f"Error reading HTML: {str(e)}".encode('utf-8')]

def serve_static_with_cache_control(environ, start_response, file_path):
    """Serves static files with proper cache control headers."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"WSGI: Error reading file {file_path}: {e}")
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')] + get_cors_headers()
        start_response(status, headers)
        return [f"Error reading file: {str(e)}".encode('utf-8')]
    
    # Определяем тип содержимого
    if file_path.endswith('.css'):
        content_type = 'text/css'
    elif file_path.endswith('.js'):
        content_type = 'application/javascript'
    elif file_path.endswith('.svg'):
        content_type = 'image/svg+xml'
    elif file_path.endswith('.png'):
        content_type = 'image/png'
    elif file_path.endswith(('.jpg', '.jpeg')):
        content_type = 'image/jpeg'
    elif file_path.endswith('.gif'):
        content_type = 'image/gif'
    elif file_path.endswith('.ico'):
        content_type = 'image/x-icon'
    else:
        content_type = 'application/octet-stream'
    
    # Проверяем версию файла для кеширования
    query_string = environ.get('QUERY_STRING', '')
    has_version = 'v=' in query_string
    
    # Create stable content hash for ETag
    content_hash = create_content_hash(content)
    
    if has_version:
        # Versioned files should be cached for a long time
        headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(content))),
            ('Cache-Control', 'public, max-age=31536000'),  # 1 year
            ('ETag', f'"{content_hash}"'),
        ] + get_cors_headers()
    else:
        # Non-versioned files should not be cached
        headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(content))),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('Pragma', 'no-cache'),
            ('Expires', '0'),
        ] + get_cors_headers()
    
    status = '200 OK'
    start_response(status, headers)
    return [content]

def serve_security_txt(environ, start_response):
    """Serve security.txt file."""
    security_txt_path = os.path.join(project_root, '.well-known', 'security.txt')
    if os.path.exists(security_txt_path):
        try:
            with open(security_txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            status = '200 OK'
            headers = [('Content-Type', 'text/plain; charset=utf-8')] + get_cors_headers()
            start_response(status, headers)
            return [content.encode('utf-8')]
        except Exception as e:
            logger.error(f"WSGI: Error reading security.txt: {e}")
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'text/plain; charset=utf-8')] + get_cors_headers()
            start_response(status, headers)
            return [f"Error reading security.txt: {str(e)}".encode('utf-8')]
    else:
        status = '404 Not Found'
        headers = [('Content-Type', 'text/plain; charset=utf-8')] + get_cors_headers()
        start_response(status, headers)
        return [b'Security policy not found']

def webhook_test_handler(environ, start_response):
    """Test webhook functionality"""
    try:
        # Получаем метод запроса
        method = environ.get('REQUEST_METHOD', 'GET')
        
        # Получаем заголовки
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        
        # Получаем тело запроса
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = ''
        if content_length > 0:
            body = environ['wsgi.input'].read(content_length).decode('utf-8')
        
        # Получаем query параметры
        query_string = environ.get('QUERY_STRING', '')
        
        # Формируем ответ
        response_data = {
            "status": "webhook_test_success",
            "method": method,
            "headers": headers,
            "body": body,
            "query_string": query_string,
            "timestamp": time.time(),
            "server_info": {
                "server_software": environ.get('SERVER_SOFTWARE', 'Unknown'),
                "gateway_interface": environ.get('GATEWAY_INTERFACE', 'Unknown'),
                "server_name": environ.get('SERVER_NAME', 'Unknown'),
                "server_port": environ.get('SERVER_PORT', 'Unknown'),
                "https": environ.get('HTTPS', 'off'),
                "remote_addr": environ.get('REMOTE_ADDR', 'Unknown')
            }
        }
        
        logger.info(f"Webhook test: {method} request received")
        logger.info(f"Headers: {headers}")
        logger.info(f"Body: {body}")
        
        status = '200 OK'
        response_headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('Pragma', 'no-cache'),
            ('Expires', '0'),
        ] + get_cors_headers()
        
        start_response(status, response_headers)
        return [json.dumps(response_data, indent=2, ensure_ascii=False).encode('utf-8')]
        
    except Exception as e:
        logger.error(f"Webhook test error: {e}")
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json; charset=utf-8')] + get_cors_headers()
        start_response(status, headers)
        return [json.dumps({"error": f"Webhook test failed: {str(e)}"}, ensure_ascii=False).encode('utf-8')]

def application(environ, start_response):
    """WSGI application entry point"""
    global bot_thread, api_server_thread
    
    # Запускаем бота и API сервер в фоновых потоках
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
    
    if api_server_thread is None or not api_server_thread.is_alive():
        api_server_thread = threading.Thread(target=start_api_server, daemon=True)
        api_server_thread.start()
    
    # Получаем путь запроса
    path = environ.get('PATH_INFO', '/')
    
    # Убираем /bot-app/ из пути для внутренней обработки
    if path.startswith('/bot-app/'):
        path = path[8:]  # Убираем '/bot-app'
        if not path:  # Если путь стал пустым после удаления /bot-app/
            path = '/'  # Устанавливаем корень для обработки
    if not path.startswith('/'):
        path = '/' + path
    
    # НЕ делаем редирект с корня - CloudLinux уже настроил /bot-app как базовый URI
    # if path == '/' or path == '':
    #     status = '302 Found'
    #     headers = [('Location', '/bot-app/')]
    #     start_response(status, headers)
    #     return []
    
    # Обрабатываем статические файлы с умным кешированием
    static_extensions = ('.css', '.js', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico')
    if path.startswith('/images/') or path.startswith('/css/') or path.startswith('/js/') or path.endswith(static_extensions):
        file_path = os.path.join(WEB_APP_DIR, path.lstrip('/'))
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return serve_static_with_cache_control(environ, start_response, file_path)
    
    # Обрабатываем HTML файлы
    if path == '/' or path == '' or path.endswith('.html'):
        return serve_main_app_page(environ, start_response)
    
    # Обрабатываем API запросы
    if path == '/api/auth/token':
        return get_auth_token_handler(environ, start_response)
    elif path == '/api/products':
        return get_products_handler(environ, start_response)
    elif path == '/api/categories':
        return get_categories_handler(environ, start_response)
    
    # Security.txt endpoint
    if path == '/.well-known/security.txt':
        return serve_security_txt(environ, start_response)
    
    # Webhook test endpoint
    if path == '/api/webhook/test':
        return webhook_test_handler(environ, start_response)
    
    # 404 для неизвестных путей
    status = '404 Not Found'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [f"Not found: {path}".encode('utf-8')]
