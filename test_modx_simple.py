#!/usr/bin/env python3
"""
Простой тест MODX API для отладки
"""
import asyncio
import aiohttp
import ssl
import json
import os

# Настройки как в api_server.py
MODX_API_BASE_URL = os.environ.get('MODX_API_BASE_URL', 'https://drazhin.by/api')
MODX_API_TIMEOUT = int(os.environ.get('MODX_API_TIMEOUT', '10'))

async def load_categories_from_modx_api():
    """Загружает категории через MODX API - копия из api_server.py"""
    try:
        url = f"{MODX_API_BASE_URL}/categories.php"
        
        # Настройка SSL для Heroku
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=MODX_API_TIMEOUT)
        ) as session:
            print(f"API: Загружаем категории из MODX API: {url}")
            async with session.get(url) as response:
                print(f"API: MODX API ответ: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"API: Загружено {len(data)} категорий из MODX API")
                    print(f"API: Первая категория: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
                    return data
                else:
                    text = await response.text()
                    print(f"API: Ошибка MODX API: {response.status} - {text}")
                    return []
    except Exception as e:
        print(f"API: Ошибка загрузки из MODX API: {e}")
        import traceback
        traceback.print_exc()
        return []

async def test_categories_processing():
    """Тестируем обработку категорий как в api_server.py"""
    try:
        categories = await load_categories_from_modx_api()
        
        if categories:
            print(f"\n✅ Получено {len(categories)} категорий")
            
            # Преобразуем формат для фронтенда
            categories_list = []
            for category in categories:
                print(f"Обрабатываем категорию: {category}")
                
                # Создаем ключ категории в формате парсера
                category_key = f"category_{category['id']}"
                
                categories_list.append({
                    "key": category_key,
                    "name": category['name'],
                    "image": ""  # Пока без изображения
                })
            
            print(f"\n✅ Результат обработки:")
            for cat in categories_list:
                print(f"  {cat}")
            
            return categories_list
        else:
            print("❌ Категории не получены")
            return []
        
    except Exception as e:
        print(f"❌ Ошибка обработки категорий: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    asyncio.run(test_categories_processing())

