#!/usr/bin/env python3
"""Тест всех продуктов в MODX - проверяем разные ID"""

import asyncio
import aiohttp
import ssl
import json

async def test_all_products():
    """Тестируем все продукты с разными ID"""
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        print("=== Тест всех продуктов ===")
        try:
            url = 'https://drazhin.by/api-products.json'
            print(f"URL: {url}")
            async with session.get(url) as response:
                print(f"Статус: {response.status}")
                text = await response.text()
                if response.status == 200:
                    data = json.loads(text)
                    products = data.get('products', [])
                    print(f"Общее количество продуктов: {len(products)}")
                    
                    # Показываем все ID продуктов
                    print(f"\nВсе ID продуктов:")
                    for i, product in enumerate(products):
                        print(f"  {i+1:2d}. ID: {product.get('id', 'N/A'):3s} - {product.get('pagetitle', 'N/A')}")
                    
                    # Проверяем диапазон ID
                    ids = [int(p.get('id', 0)) for p in products if p.get('id', '').isdigit()]
                    if ids:
                        print(f"\nДиапазон ID: {min(ids)} - {max(ids)}")
                        print(f"Пропущенные ID в диапазоне:")
                        for i in range(min(ids), max(ids) + 1):
                            if i not in ids:
                                print(f"  - {i}")
                    
                    # Группируем по категориям
                    categories = {}
                    for product in products:
                        parent_id = product.get('parent_id')
                        if parent_id not in categories:
                            categories[parent_id] = []
                        categories[parent_id].append(product.get('pagetitle', 'N/A'))
                    
                    print(f"\nПродукты по категориям:")
                    for cat_id, prods in categories.items():
                        print(f"  Категория {cat_id}: {len(prods)} продуктов")
                        for prod in prods:
                            print(f"    - {prod}")
                    
                else:
                    print(f"Ошибка HTTP: {response.status}")
                    print(f"Ответ: {text[:200]}...")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_products())
