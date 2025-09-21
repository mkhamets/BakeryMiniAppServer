#!/usr/bin/env python3
"""
Пример клиента для MODX API с обработкой ошибок и retry
"""

import time
import requests
from typing import Dict, Any, Optional, List
from functools import wraps

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Декоратор для повторных попыток"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        print(f"All {max_attempts} attempts failed. Last error: {e}")
            
            raise last_exception
        return wrapper
    return decorator

class MODXAPIClient:
    def __init__(self, base_url: str = "https://drazhin.by/api", timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        
        # Настройка сессии
        self.session.headers.update({
            'User-Agent': 'BakeryMiniApp/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
    
    @retry(max_attempts=3, delay=1.0)
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполняет HTTP запрос с retry логикой"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception(f"Timeout при запросе к {url}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Ошибка соединения с {url}")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP ошибка {e.response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка запроса: {e}")
        except ValueError as e:
            raise Exception(f"Ошибка парсинга JSON: {e}")
    
    def get_products(self, category_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Получает список товаров"""
        params = {}
        if category_id:
            params['category'] = category_id
        if limit:
            params['limit'] = limit
        
        try:
            data = self._make_request('products.php', params)
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Ошибка получения товаров: {e}")
            return []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Получает список категорий"""
        try:
            data = self._make_request('categories.php')
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Ошибка получения категорий: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Тестирует соединение с API"""
        try:
            data = self._make_request('test.php')
            return data.get('status') == 'success'
        except Exception as e:
            print(f"Ошибка тестирования соединения: {e}")
            return False
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Получает товар по ID"""
        products = self.get_products()
        for product in products:
            if str(product.get('id')) == str(product_id):
                return product
        return None
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Поиск товаров по названию"""
        products = self.get_products()
        query_lower = query.lower()
        
        return [
            product for product in products
            if query_lower in product.get('name', '').lower()
        ]

# Пример использования
if __name__ == "__main__":
    client = MODXAPIClient()
    
    # Тестируем соединение
    if client.test_connection():
        print("✅ Соединение с API установлено")
        
        # Получаем категории
        categories = client.get_categories()
        print(f"📁 Загружено {len(categories)} категорий")
        
        # Получаем товары
        products = client.get_products()
        print(f"🛍️ Загружено {len(products)} товаров")
        
        # Получаем товары по категории
        if categories:
            first_category = categories[0]
            category_products = client.get_products(first_category['id'])
            print(f"📦 В категории '{first_category['name']}': {len(category_products)} товаров")
        
        # Поиск товаров
        search_results = client.search_products("хлеб")
        print(f"🔍 Найдено товаров с 'хлеб': {len(search_results)}")
        
    else:
        print("❌ Не удалось подключиться к API")
