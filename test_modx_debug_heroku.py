#!/usr/bin/env python3
"""
Тест MODX API для отладки на Heroku
"""
import asyncio
import aiohttp
import ssl
import json
import os

# Настройки как в api_server.py
MODX_API_BASE_URL = os.environ.get('MODX_API_BASE_URL', 'https://drazhin.by/api')
MODX_API_TIMEOUT = int(os.environ.get('MODX_API_TIMEOUT', '10'))

async def test_modx_categories():
    """Тестируем загрузку категорий как в api_server.py"""
    try:
        url = f"{MODX_API_BASE_URL}/categories.php"
        print(f"🔍 Тестируем URL: {url}")
        
        # Настройка SSL для Heroku
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=MODX_API_TIMEOUT)
        ) as session:
            print(f"📡 Отправляем запрос к MODX API...")
            async with session.get(url) as response:
                print(f"📊 Статус ответа: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Получено {len(data)} категорий")
                    print(f"📋 Первая категория: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
                    return data
                else:
                    text = await response.text()
                    print(f"❌ Ошибка MODX API: {response.status} - {text}")
                    return []
    except Exception as e:
        print(f"💥 Исключение: {e}")
        import traceback
        print(f"📜 Traceback: {traceback.format_exc()}")
        return []

async def test_modx_products():
    """Тестируем загрузку продуктов как в api_server.py"""
    try:
        url = f"{MODX_API_BASE_URL}/products.php"
        params = {'category': '17'}  # Выпечка
        print(f"🔍 Тестируем URL: {url} с параметрами: {params}")
        
        # Настройка SSL для Heroku
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=MODX_API_TIMEOUT)
        ) as session:
            print(f"📡 Отправляем запрос к MODX API...")
            async with session.get(url, params=params) as response:
                print(f"📊 Статус ответа: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Получено {len(data)} продуктов")
                    if data:
                        print(f"📋 Первый продукт: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
                    return data
                else:
                    text = await response.text()
                    print(f"❌ Ошибка MODX API: {response.status} - {text}")
                    return []
    except Exception as e:
        print(f"💥 Исключение: {e}")
        import traceback
        print(f"📜 Traceback: {traceback.format_exc()}")
        return []

async def main():
    print("🚀 Тестируем MODX API на Heroku...")
    print(f"🌐 MODX_API_BASE_URL: {MODX_API_BASE_URL}")
    print(f"⏱️ MODX_API_TIMEOUT: {MODX_API_TIMEOUT}")
    print()
    
    print("1️⃣ Тестируем категории:")
    categories = await test_modx_categories()
    print()
    
    print("2️⃣ Тестируем продукты:")
    products = await test_modx_products()
    print()
    
    print("✅ Тест завершен")

if __name__ == "__main__":
    asyncio.run(main())

