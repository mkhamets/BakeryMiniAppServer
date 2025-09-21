#!/usr/bin/env python3
"""Тест количества продуктов в MODX API"""

import asyncio
import aiohttp
import ssl
import json

async def test_modx_count():
    """Тестируем количество продуктов в MODX API"""
    
    # Настройка SSL для Heroku
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        # Тест продуктов
        print("=== Тест количества продуктов ===")
        try:
            url = 'https://drazhin.by/api-products.json'
            print(f"URL: {url}")
            async with session.get(url) as response:
                print(f"Статус: {response.status}")
                text = await response.text()
                if response.status == 200:
                    data = json.loads(text)
                    print(f"Количество продуктов: {data.get('count', 0)}")
                    print(f"Статус: {data.get('status', 'unknown')}")
                    
                    # Показываем первые несколько продуктов
                    products = data.get('products', [])
                    print(f"\nПервые 5 продуктов:")
                    for i, product in enumerate(products[:5]):
                        print(f"  {i+1}. {product.get('pagetitle', 'N/A')} (ID: {product.get('id', 'N/A')})")
                    
                    # Показываем категории продуктов
                    categories = set()
                    for product in products:
                        parent_id = product.get('parent_id')
                        if parent_id:
                            categories.add(f"category_{parent_id}")
                    
                    print(f"\nКатегории в результатах: {sorted(categories)}")
                    
                else:
                    print(f"Ошибка HTTP: {response.status}")
                    print(f"Ответ: {text[:200]}...")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_modx_count())
