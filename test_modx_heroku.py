#!/usr/bin/env python3
import asyncio
import aiohttp
import ssl

async def test_modx_api():
    """Тестируем MODX API из Heroku"""
    
    # Настройка SSL для Heroku
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        
        # Тестируем категории
        print("Тестируем категории...")
        url = "https://drazhin.by/api-categories"
        async with session.get(url) as response:
            print(f"Статус: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"Данные: {data}")
            else:
                text = await response.text()
                print(f"Ошибка: {text}")
        
        print("\nТестируем продукты...")
        url = "https://drazhin.by/api-products"
        async with session.get(url) as response:
            print(f"Статус: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"Количество продуктов: {data.get('count', 0)}")
                if data.get('products'):
                    print(f"Первый продукт: {data['products'][0]}")
            else:
                text = await response.text()
                print(f"Ошибка: {text}")

if __name__ == "__main__":
    asyncio.run(test_modx_api())
