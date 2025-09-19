#!/usr/bin/env python3
"""
Скрипт для тестирования webhook функциональности
"""

import requests
import json
import time

def test_webhook():
    """Тестирует webhook endpoint"""
    
    # URL для тестирования
    webhook_url = "https://miniapp.drazhin.by/bot-app/api/webhook/test"
    
    print("🔍 Тестирование webhook функциональности...")
    print(f"URL: {webhook_url}")
    print("-" * 50)
    
    # Тест 1: GET запрос
    print("1️⃣ Тест GET запроса...")
    try:
        response = requests.get(webhook_url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ GET запрос успешен!")
            print(f"Server: {data.get('server_info', {}).get('server_software', 'Unknown')}")
            print(f"HTTPS: {data.get('server_info', {}).get('https', 'off')}")
        else:
            print("❌ GET запрос неуспешен")
            
    except Exception as e:
        print(f"❌ Ошибка GET запроса: {e}")
    
    print("-" * 50)
    
    # Тест 2: POST запрос с данными
    print("2️⃣ Тест POST запроса с данными...")
    try:
        test_data = {
            "test": "webhook_data",
            "timestamp": time.time(),
            "message": "Тестовое сообщение для webhook"
        }
        
        response = requests.post(
            webhook_url, 
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ POST запрос успешен!")
            print(f"Полученные данные: {data.get('body', 'N/A')}")
        else:
            print("❌ POST запрос неуспешен")
            
    except Exception as e:
        print(f"❌ Ошибка POST запроса: {e}")
    
    print("-" * 50)
    
    # Тест 3: POST запрос с Telegram-подобными данными
    print("3️⃣ Тест POST запроса с Telegram данными...")
    try:
        telegram_data = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private"
                },
                "date": int(time.time()),
                "text": "/start"
            }
        }
        
        response = requests.post(
            webhook_url, 
            json=telegram_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Telegram POST запрос успешен!")
        else:
            print("❌ Telegram POST запрос неуспешен")
            
    except Exception as e:
        print(f"❌ Ошибка Telegram POST запроса: {e}")
    
    print("-" * 50)
    print("🏁 Тестирование завершено!")

if __name__ == "__main__":
    test_webhook()
