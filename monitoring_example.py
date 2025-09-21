#!/usr/bin/env python3
"""
Пример мониторинга MODX API
"""

import time
import requests
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

class APIMonitor:
    def __init__(self):
        self.logger = logging.getLogger('api_monitor')
        self.logger.setLevel(logging.INFO)
        
        # Настройка логирования
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'last_successful_request': None,
            'last_failed_request': None,
            'errors': []
        }
    
    def log_request(self, endpoint: str, success: bool, response_time: float, error: str = None):
        """Логирует запрос к API"""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
            self.stats['last_successful_request'] = datetime.now()
            self.logger.info(f"✅ {endpoint} - {response_time:.2f}s")
        else:
            self.stats['failed_requests'] += 1
            self.stats['last_failed_request'] = datetime.now()
            if error:
                self.stats['errors'].append({
                    'timestamp': datetime.now(),
                    'endpoint': endpoint,
                    'error': error
                })
            self.logger.error(f"❌ {endpoint} - {response_time:.2f}s - {error}")
        
        # Обновляем среднее время ответа
        total_time = self.stats['average_response_time'] * (self.stats['total_requests'] - 1)
        self.stats['average_response_time'] = (total_time + response_time) / self.stats['total_requests']
    
    def get_health_status(self) -> Dict[str, Any]:
        """Возвращает статус здоровья API"""
        now = datetime.now()
        
        # Проверяем, был ли успешный запрос за последние 5 минут
        last_success = self.stats['last_successful_request']
        if last_success and (now - last_success).total_seconds() < 300:
            health_status = "healthy"
        elif last_success and (now - last_success).total_seconds() < 1800:  # 30 минут
            health_status = "degraded"
        else:
            health_status = "unhealthy"
        
        # Рассчитываем процент успешности
        success_rate = 0
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
        
        return {
            'status': health_status,
            'success_rate': round(success_rate, 2),
            'total_requests': self.stats['total_requests'],
            'average_response_time': round(self.stats['average_response_time'], 2),
            'last_successful_request': last_success.isoformat() if last_success else None,
            'recent_errors': len([
                e for e in self.stats['errors']
                if (now - e['timestamp']).total_seconds() < 3600  # Последний час
            ])
        }
    
    def get_recent_errors(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Возвращает ошибки за последние N часов"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            e for e in self.stats['errors']
            if e['timestamp'] > cutoff_time
        ]

class MonitoredMODXClient:
    def __init__(self, base_url: str = "https://drazhin.by/api"):
        self.base_url = base_url
        self.monitor = APIMonitor()
    
    def _make_monitored_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Выполняет запрос с мониторингом"""
        start_time = time.time()
        error = None
        success = False
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            success = True
            return data
        except Exception as e:
            error = str(e)
            raise
        finally:
            response_time = time.time() - start_time
            self.monitor.log_request(endpoint, success, response_time, error)
    
    def get_products(self, category_id: str = None) -> List[Dict[str, Any]]:
        """Получает товары с мониторингом"""
        try:
            params = {'category': category_id} if category_id else {}
            data = self._make_monitored_request('products.php', params)
            return data if isinstance(data, list) else []
        except Exception as e:
            self.monitor.logger.error(f"Ошибка получения товаров: {e}")
            return []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Получает категории с мониторингом"""
        try:
            data = self._make_monitored_request('categories.php')
            return data if isinstance(data, list) else []
        except Exception as e:
            self.monitor.logger.error(f"Ошибка получения категорий: {e}")
            return []
    
    def get_health_status(self) -> Dict[str, Any]:
        """Возвращает статус здоровья"""
        return self.monitor.get_health_status()

# Пример использования
if __name__ == "__main__":
    client = MonitoredMODXClient()
    
    # Выполняем несколько запросов
    print("🔄 Выполняем тестовые запросы...")
    
    categories = client.get_categories()
    print(f"📁 Категории: {len(categories)}")
    
    products = client.get_products()
    print(f"🛍️ Товары: {len(products)}")
    
    # Показываем статистику
    health = client.get_health_status()
    print(f"\n📊 Статус здоровья:")
    print(f"   Статус: {health['status']}")
    print(f"   Успешность: {health['success_rate']}%")
    print(f"   Всего запросов: {health['total_requests']}")
    print(f"   Среднее время ответа: {health['average_response_time']}s")
    print(f"   Ошибок за час: {health['recent_errors']}")
