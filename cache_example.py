#!/usr/bin/env python3
"""
Пример кэширования для MODX API
"""

import time
import json
import requests
from typing import Dict, Any, Optional

class MODXAPICache:
    def __init__(self, cache_duration: int = 300):  # 5 минут по умолчанию
        self.cache_duration = cache_duration
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.base_url = "https://drazhin.by/api"
    
    def _is_cache_valid(self, key: str) -> bool:
        """Проверяет, действителен ли кэш"""
        if key not in self.cache:
            return False
        
        cache_time = self.cache[key].get('timestamp', 0)
        return time.time() - cache_time < self.cache_duration
    
    def get_products(self, category_id: Optional[str] = None) -> list:
        """Получает товары с кэшированием"""
        cache_key = f"products_{category_id or 'all'}"
        
        if self._is_cache_valid(cache_key):
            print(f"Cache hit for {cache_key}")
            return self.cache[cache_key]['data']
        
        # Загружаем данные из API
        url = f"{self.base_url}/products.php"
        if category_id:
            url += f"?category={category_id}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Сохраняем в кэш
                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': time.time()
                }
                
                print(f"Cache miss for {cache_key}, loaded {len(data)} items")
                return data
            else:
                print(f"API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Request error: {e}")
            return []
    
    def get_categories(self) -> list:
        """Получает категории с кэшированием"""
        cache_key = "categories"
        
        if self._is_cache_valid(cache_key):
            print(f"Cache hit for {cache_key}")
            return self.cache[cache_key]['data']
        
        try:
            response = requests.get(f"{self.base_url}/categories.php", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Сохраняем в кэш
                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': time.time()
                }
                
                print(f"Cache miss for {cache_key}, loaded {len(data)} items")
                return data
            else:
                print(f"API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Request error: {e}")
            return []
    
    def clear_cache(self):
        """Очищает весь кэш"""
        self.cache.clear()
        print("Cache cleared")

# Пример использования
if __name__ == "__main__":
    cache = MODXAPICache(cache_duration=300)  # 5 минут
    
    # Первый запрос - загрузит из API
    products = cache.get_products()
    print(f"Loaded {len(products)} products")
    
    # Второй запрос - возьмет из кэша
    products_cached = cache.get_products()
    print(f"Loaded {len(products_cached)} products from cache")
    
    # Запрос по категории
    bread_products = cache.get_products("16")
    print(f"Loaded {len(bread_products)} bread products")
