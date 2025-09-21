#!/usr/bin/env python3
"""Детальный тест продуктов в MODX"""

import asyncio
import aiohttp
import ssl
import json

async def test_debug_products():
    """Детальный тест всех продуктов"""
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        print("=== Детальный тест продуктов ===")
        
        # Тест 1: Все продукты без фильтра
        print("\n1. Все продукты (без фильтра по категории):")
        try:
            url = 'https://drazhin.by/api-products.json'
            async with session.get(url) as response:
                if response.status == 200:
                    data = json.loads(text := await response.text())
                    products = data.get('products', [])
                    print(f"   Количество: {len(products)}")
                    
                    # Показываем ID всех продуктов
                    ids = [p.get('id') for p in products]
                    print(f"   ID продуктов: {ids}")
                    
                    # Группируем по категориям
                    categories = {}
                    for p in products:
                        cat_id = p.get('parent_id')
                        if cat_id not in categories:
                            categories[cat_id] = []
                        categories[cat_id].append(f"{p.get('id')}: {p.get('pagetitle', 'N/A')}")
                    
                    for cat_id, prods in categories.items():
                        print(f"   Категория {cat_id}: {len(prods)} продуктов")
                        for prod in prods[:3]:  # Показываем первые 3
                            print(f"     - {prod}")
                        if len(prods) > 3:
                            print(f"     ... и еще {len(prods) - 3}")
                else:
                    print(f"   Ошибка: {response.status}")
        except Exception as e:
            print(f"   Ошибка: {e}")
        
        # Тест 2: Продукты по категориям
        categories_to_test = [16, 17, 18, 19]
        for cat_id in categories_to_test:
            print(f"\n2. Категория {cat_id}:")
            try:
                url = f'https://drazhin.by/api-products.json?category={cat_id}'
                async with session.get(url) as response:
                    if response.status == 200:
                        data = json.loads(text := await response.text())
                        products = data.get('products', [])
                        print(f"   Количество: {len(products)}")
                        
                        if products:
                            for p in products[:5]:  # Показываем первые 5
                                print(f"     - ID {p.get('id')}: {p.get('pagetitle', 'N/A')}")
                            if len(products) > 5:
                                print(f"     ... и еще {len(products) - 5}")
                        else:
                            print("   Продуктов нет")
                    else:
                        print(f"   Ошибка: {response.status}")
            except Exception as e:
                print(f"   Ошибка: {e}")
        
        # Тест 3: Проверяем разные лимиты
        print(f"\n3. Тест с разными лимитами:")
        limits_to_test = [5, 20, 50, 100]
        for limit in limits_to_test:
            try:
                url = f'https://drazhin.by/api-products.json?limit={limit}'
                async with session.get(url) as response:
                    if response.status == 200:
                        data = json.loads(text := await response.text())
                        products = data.get('products', [])
                        print(f"   Лимит {limit}: {len(products)} продуктов")
                    else:
                        print(f"   Лимит {limit}: Ошибка {response.status}")
            except Exception as e:
                print(f"   Лимит {limit}: Ошибка {e}")

if __name__ == "__main__":
    asyncio.run(test_debug_products())
