#!/usr/bin/env python3
"""
Тест для отладки MODX API
"""
import asyncio
import aiohttp
import ssl
import json

async def test_modx_api():
    """Тестируем MODX API"""
    
    # Настройка SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        
        print("🔍 Тестируем MODX API...")
        
        # Тест категорий
        print("\n1. Тестируем категории:")
        try:
            async with session.get("https://drazhin.by/api/categories.php") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Данные: {json.dumps(data[:2], ensure_ascii=False, indent=2)}")
                else:
                    text = await response.text()
                    print(f"   Ошибка: {text}")
        except Exception as e:
            print(f"   Исключение: {e}")
        
        # Тест продуктов
        print("\n2. Тестируем продукты:")
        try:
            async with session.get("https://drazhin.by/api/products.php") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Данные: {json.dumps(data[:1], ensure_ascii=False, indent=2)}")
                else:
                    text = await response.text()
                    print(f"   Ошибка: {text}")
        except Exception as e:
            print(f"   Исключение: {e}")
        
        # Тест продуктов с категорией
        print("\n3. Тестируем продукты с категорией 17:")
        try:
            async with session.get("https://drazhin.by/api/products.php?category=17") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Данные: {json.dumps(data[:1], ensure_ascii=False, indent=2)}")
                else:
                    text = await response.text()
                    print(f"   Ошибка: {text}")
        except Exception as e:
            print(f"   Исключение: {e}")

if __name__ == "__main__":
    asyncio.run(test_modx_api())

