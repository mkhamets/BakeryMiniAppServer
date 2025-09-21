#!/usr/bin/env python3
"""Тест общего количества продуктов в MODX"""

import asyncio
import aiohttp
import ssl
import json

async def test_total_products():
    """Тестируем общее количество продуктов"""
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        # Тест всех продуктов без фильтра по категории
        print("=== Тест общего количества продуктов ===")
        try:
            url = 'https://drazhin.by/api-products.json'
            print(f"URL: {url}")
            async with session.get(url) as response:
                print(f"Статус: {response.status}")
                text = await response.text()
                if response.status == 200:
                    data = json.loads(text)
                    print(f"Общее количество продуктов: {data.get('count', 0)}")
                    
                    # Группируем по категориям
                    products = data.get('products', [])
                    categories = {}
                    for product in products:
                        parent_id = product.get('parent_id')
                        if parent_id not in categories:
                            categories[parent_id] = []
                        categories[parent_id].append(product.get('pagetitle', 'N/A'))
                    
                    print(f"\nПродукты по категориям:")
                    for cat_id, prods in categories.items():
                        print(f"  Категория {cat_id}: {len(prods)} продуктов")
                        for prod in prods[:3]:  # Показываем первые 3
                            print(f"    - {prod}")
                        if len(prods) > 3:
                            print(f"    ... и еще {len(prods) - 3}")
                    
                else:
                    print(f"Ошибка HTTP: {response.status}")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_total_products())
