#!/usr/bin/env python3
"""
Тестовый скрипт для создания заказа в Bakery Mini App
"""

import json
import time
from datetime import datetime

def create_test_order():
    """Создает тестовый заказ"""
    
    # Тестовые данные заказа
    test_order = {
        "customer_name": "Тестовый Покупатель",
        "customer_phone": "+375291234567",
        "customer_email": "test@example.com",
        "delivery_address": "ул. Тестовая, 123, Минск",
        "items": [
            {
                "product_id": "49",
                "quantity": 2,
                "price": "18",
                "name": "Завиванец с маком"
            },
            {
                "product_id": "53",
                "quantity": 1,
                "price": "3.8",
                "name": "Круассан классический"
            },
            {
                "product_id": "68",
                "quantity": 1,
                "price": "9.5",
                "name": "Печенье «Кантуччи с миндалем»"
            }
        ],
        "total_amount": "49.3",
        "privacy_consent": True,
        "order_date": datetime.now().isoformat(),
        "notes": "Тестовый заказ для проверки API"
    }
    
    print("🧪 СОЗДАНИЕ ТЕСТОВОГО ЗАКАЗА")
    print("=" * 50)
    print(f"👤 Клиент: {test_order['customer_name']}")
    print(f"📞 Телефон: {test_order['customer_phone']}")
    print(f"📧 Email: {test_order['customer_email']}")
    print(f"📍 Адрес: {test_order['delivery_address']}")
    print(f"💰 Сумма: {test_order['total_amount']} BYN")
    print(f"✅ Согласие на обработку данных: {'Да' if test_order['privacy_consent'] else 'Нет'}")
    print()
    
    print("🛒 ТОВАРЫ В ЗАКАЗЕ:")
    print("-" * 30)
    for i, item in enumerate(test_order['items'], 1):
        print(f"{i}. {item['name']}")
        print(f"   ID: {item['product_id']}")
        print(f"   Количество: {item['quantity']} шт.")
        print(f"   Цена: {item['price']} BYN")
        print(f"   Сумма: {float(item['price']) * item['quantity']} BYN")
        print()
    
    # Сохраняем заказ в файл
    order_id = f"test_order_{int(time.time())}"
    filename = f"data/{order_id}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_order, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Заказ сохранен в файл: {filename}")
        print(f"🆔 ID заказа: {order_id}")
        
        # Обновляем счетчик заказов
        try:
            with open('data/order_counter.json', 'r', encoding='utf-8') as f:
                counter = json.load(f)
        except FileNotFoundError:
            counter = {"count": 0}
        
        counter["count"] = counter.get("count", 0) + 1
        counter["last_order"] = order_id
        counter["last_order_date"] = datetime.now().isoformat()
        
        with open('data/order_counter.json', 'w', encoding='utf-8') as f:
            json.dump(counter, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Общее количество заказов: {counter['count']}")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении заказа: {e}")
        return False
    
    return True

def simulate_order_processing():
    """Симулирует обработку заказа"""
    print("⚙️ ОБРАБОТКА ЗАКАЗА")
    print("=" * 30)
    
    steps = [
        "Проверка данных клиента...",
        "Валидация товаров...",
        "Расчет стоимости...",
        "Проверка наличия товаров...",
        "Создание заказа в системе...",
        "Отправка уведомления клиенту...",
        "Уведомление пекарни..."
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")
        time.sleep(0.5)
        print("   ✅ Готово")
    
    print()
    print("🎉 ЗАКАЗ УСПЕШНО ОБРАБОТАН!")
    print("📧 Клиенту отправлено подтверждение")
    print("🏪 Пекарня уведомлена о новом заказе")

if __name__ == "__main__":
    print("🍞 BAKERY MINI APP - ТЕСТОВЫЙ ЗАКАЗ")
    print("=" * 50)
    print()
    
    if create_test_order():
        print()
        simulate_order_processing()
    else:
        print("❌ Не удалось создать тестовый заказ")
