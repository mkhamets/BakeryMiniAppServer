#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
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

# Импортируем необходимые модули
from bot.config import config

# ===== SECURITY CONFIGURATION =====
# HMAC secret key for request signing
HMAC_SECRET = os.environ.get('HMAC_SECRET', 'default-secret-key-change-in-production')

# Rate limiting configuration
RATE_LIMIT_REQUESTS_PER_HOUR = 100
RATE_LIMIT_BLOCK_DURATION = 3600
rate_limit_storage = defaultdict(list)

# Путь к файлу с данными о продуктах
PRODUCTS_DATA_FILE = project_root / 'data' / 'products_scraped.json'

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
            print(f"Данные о продуктах успешно загружены из {PRODUCTS_DATA_FILE}")
        except json.JSONDecodeError as e:
            print(f"Ошибка при чтении JSON-файла '{PRODUCTS_DATA_FILE}': {e}")
            products_data = {}
        except Exception as e:
            print(f"Неизвестная ошибка при загрузке данных о продуктах: {e}")
            products_data = {}
    else:
        print(f"Файл '{PRODUCTS_DATA_FILE}' не найден")
        products_data = {}

# Загружаем данные о продуктах при инициализации
load_products_data()

# ===== API HANDLERS =====
def get_auth_token_handler(environ, start_response):
    """Handle auth token requests"""
    client_ip = environ.get('REMOTE_ADDR', '127.0.0.1')
    
    # Basic rate limiting for token requests
    if not check_rate_limit(f"{client_ip}:token"):
        status = '429 Too Many Requests'
        headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [b'{"error": "Token rate limit exceeded"}']
    
    token_data = generate_auth_token()
    response_data = json.dumps(token_data)
    
    status = '200 OK'
    headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ('Pragma', 'no-cache'),
        ('Expires', '0'),
        ('Access-Control-Allow-Origin', '*'),
    ]
    start_response(status, headers)
    return [response_data.encode('utf-8')]

def get_products_handler(environ, start_response):
    """Handle products requests with full API functionality"""
    try:
        client_ip = environ.get('REMOTE_ADDR', '127.0.0.1')
        
        # Rate limiting
        if not check_rate_limit(client_ip):
            status = '429 Too Many Requests'
            headers = [('Content-Type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [b'{"error": "Rate limit exceeded"}']
        
        # HMAC signature verification (simplified for wsgi)
        signature = environ.get('HTTP_X_SIGNATURE')
        timestamp = environ.get('HTTP_X_TIMESTAMP')
        init_data = environ.get('HTTP_X_TELEGRAM_INIT_DATA', '')
        
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
        
        if not products_data:
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
            ('Access-Control-Allow-Origin', '*'),
        ]
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
        if not check_rate_limit(client_ip):
            status = '429 Too Many Requests'
            headers = [('Content-Type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [b'{"error": "Rate limit exceeded"}']
        
        if not products_data:
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
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response(status, headers)
        return [response_data.encode('utf-8')]
        
    except Exception as e:
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [f'{{"error": "Failed to load categories: {str(e)}"}}'.encode('utf-8')]

def application(environ, start_response):
    # Получаем путь запроса
    path = environ.get('PATH_INFO', '/')
    
    # Убираем /bot-app/ из пути
    if path.startswith('/bot-app/'):
        path = path[8:]
    if not path.startswith('/'):
        path = '/' + path
    
    webapp_path = project_root / 'bot' / 'web_app'
    
    # Обрабатываем API запросы
    if path == '/api/auth/token':
        return get_auth_token_handler(environ, start_response)
    elif path == '/api/products':
        return get_products_handler(environ, start_response)
    elif path == '/api/categories':
        return get_categories_handler(environ, start_response)
    
    # Обрабатываем статические файлы
    if path.endswith(('.css', '.js', '.svg', '.png', '.jpg', '.jpeg')):
        file_path = webapp_path / path.lstrip('/')
        
        if file_path.exists() and file_path.is_file():
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Определяем тип содержимого
                if path.endswith('.css'):
                    content_type = 'text/css'
                elif path.endswith('.js'):
                    content_type = 'application/javascript'
                elif path.endswith('.svg'):
                    content_type = 'image/svg+xml'
                elif path.endswith('.png'):
                    content_type = 'image/png'
                elif path.endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                else:
                    content_type = 'application/octet-stream'
                
                # Проверяем версию файла для кеширования
                query_string = environ.get('QUERY_STRING', '')
                has_version = 'v=' in query_string
                
                if has_version:
                    # Versioned files should be cached for a long time
                    headers = [
                        ('Content-Type', content_type),
                        ('Content-Length', str(len(content))),
                        ('Cache-Control', 'public, max-age=31536000'),  # 1 year
                        ('Access-Control-Allow-Origin', '*'),
                    ]
                else:
                    # Non-versioned files should not be cached
                    headers = [
                        ('Content-Type', content_type),
                        ('Content-Length', str(len(content))),
                        ('Cache-Control', 'no-cache, no-store, must-revalidate, private'),
                        ('Pragma', 'no-cache'),
                        ('Expires', '0'),
                        ('Access-Control-Allow-Origin', '*'),
                        # Уникальные заголовки для принудительного обновления
                        ('X-File-Version', str(int(time.time()))),
                        ('X-Cache-Bust', str(int(time.time() * 1000))),
                    ]
                
                status = '200 OK'
                start_response(status, headers)
                return [content]
                
            except Exception as e:
                status = '500 Internal Server Error'
                headers = [('Content-Type', 'text/plain; charset=utf-8')]
                start_response(status, headers)
                return [f"Error: {str(e)}".encode('utf-8')]
    
    # Обрабатываем HTML файлы
    if path == '/' or path == '' or path.endswith('.html'):
        if path == '/' or path == '':
            index_file = webapp_path / 'index.html'
        else:
            index_file = webapp_path / path.lstrip('/')
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                status = '200 OK'
                # Агрессивные заголовки для принудительного обновления кеша Telegram WebApp (особенно мобильные клиенты)
                current_timestamp = int(time.time())
                headers = [
                    ('Content-Type', 'text/html; charset=utf-8'),
                    # Агрессивные заголовки кеширования
                    ('Cache-Control', 'no-cache, no-store, must-revalidate, private, max-age=0'),
                    ('Pragma', 'no-cache'),
                    ('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT'),
                    ('Last-Modified', time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(current_timestamp))),
                    ('ETag', f'"{current_timestamp}-{hash(content) % 10000}"'),
                    # Безопасность
                    ('X-Frame-Options', 'SAMEORIGIN'),
                    ('X-Content-Type-Options', 'nosniff'),
                    ('X-XSS-Protection', '1; mode=block'),
                    # CORS
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
                    # Специальные заголовки для Telegram WebApp
                    ('X-Telegram-Bot-Api-Secret-Token', f'tg-webapp-{current_timestamp}'),
                    ('X-WebApp-Version', f'2.0.{current_timestamp}'),
                    ('X-Cache-Buster', str(current_timestamp)),
                    ('X-App-Timestamp', str(current_timestamp)),
                    # Дополнительные заголовки для мобильных клиентов
                    ('Vary', 'User-Agent, Accept-Encoding'),
                    ('X-Mobile-Cache-Control', 'no-cache, no-store, must-revalidate'),
                ]
                start_response(status, headers)
                return [content.encode('utf-8')]
            except Exception as e:
                status = '500 Internal Server Error'
                headers = [('Content-Type', 'text/plain; charset=utf-8')]
                start_response(status, headers)
                return [f"Error: {str(e)}".encode('utf-8')]
    
    # 404 для неизвестных путей
    status = '404 Not Found'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [f"Not found: {path}".encode('utf-8')]
