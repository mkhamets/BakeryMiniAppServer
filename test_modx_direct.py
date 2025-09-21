#!/usr/bin/env python3
"""Тест MODX API напрямую"""

import asyncio
import aiohttp
import ssl
import json

async def test_modx_api():
    """Тестируем MODX API напрямую"""
    
    # Настройка SSL для Heroku
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        # Тест категорий
        print("=== Тест категорий ===")
        try:
            async with session.get('https://drazhin.by/api-categories.json') as response:
                print(f"Статус: {response.status}")
                text = await response.text()
                print(f"Ответ: {text[:200]}...")
                if response.status == 200:
                    data = json.loads(text)
                    print(f"Количество категорий: {len(data.get('categories', []))}")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        print("\n=== Тест продуктов ===")
        try:
            async with session.get('https://drazhin.by/api-products.json') as response:
                print(f"Статус: {response.status}")
                text = await response.text()
                print(f"Ответ: {text[:200]}...")
                if response.status == 200:
                    data = json.loads(text)
                    print(f"Количество продуктов: {len(data.get('products', []))}")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_modx_api())
