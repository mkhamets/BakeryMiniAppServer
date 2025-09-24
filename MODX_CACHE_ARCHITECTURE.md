# MODX Cache Architecture

## 📋 Overview

Новая архитектура кэширования данных из MODX API с использованием JSON файла как прослойки между MODX API и приложением.

## 🏗️ Architecture

```
MODX API → scheduler_modx.py → modx_cache.json → api_server.py → Frontend
```

## 📁 File Structure

```
├── scheduler_modx.py          # Новый планировщик для MODX API
├── data/
│   └── modx_cache.json        # Кэш всех данных (products + categories)
├── bot/
│   ├── api_server.py         # Модифицирован для чтения из кэша
│   └── web_app/
│       └── script.js         # Модифицирован для загрузки всех данных
└── bot/parser.py              # СОХРАНЕН (в комментариях)
```

## 🔄 Data Flow

### 1. **scheduler_modx.py** (каждые 60 секунд)
```python
# Загружает ВСЕ данные из MODX API
products = await load_products_from_modx_api()  # Без category_id
categories = await load_categories_from_modx_api()

# Сохраняет в один JSON файл
data = {
    "products": products,
    "categories": categories,
    "metadata": {
        "last_updated": "2024-01-15T10:30:00Z",
        "version": "1.0"
    }
}
```

### 2. **modx_cache.json** (структура)
```json
{
  "products": {
    "category_16": [
      { "id": "57", "name": "Хлеб", "price": "100", ... },
      { "id": "58", "name": "Булочка", "price": "50", ... }
    ],
    "category_17": [
      { "id": "59", "name": "Пирог", "price": "200", ... }
    ]
  },
  "categories": [
    { "id": "16", "name": "Хлеб", "key": "category_16", ... },
    { "id": "17", "name": "Десерты", "key": "category_17", ... }
  ],
  "metadata": {
    "last_updated": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

### 3. **api_server.py** (модификации)
```python
# Новый endpoint для всех данных
async def get_all_data_for_webapp(request):
    with open("data/modx_cache.json", "r") as f:
        data = json.load(f)
    return web.json_response(data)

# Сохраняем старые endpoint'ы для совместимости
async def get_products_for_webapp(request):
    with open("data/modx_cache.json", "r") as f:
        data = json.load(f)
    return web.json_response(data["products"])

async def get_categories_for_webapp(request):
    with open("data/modx_cache.json", "r") as f:
        data = json.load(f)
    return web.json_response(data["categories"])
```

### 4. **script.js** (модификации)
```javascript
// Загружаем ВСЕ данные сразу при старте
async function loadAllData() {
    try {
        const response = await fetch('/bot-app/api/all');
        const data = await response.json();
        
        // Кэшируем все данные в памяти
        productsData = data.products;
        categoriesData = data.categories;
        
        console.log('All data loaded:', data);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}
```

## ✅ Advantages

- **Простота**: Один JSON файл, атомарная запись
- **Производительность**: Все данные в памяти, быстрая навигация
- **Надежность**: Нет проблем с синхронностью
- **Совместимость**: Сохраняем старые endpoint'ы
- **Fallback**: При ошибке кэша - загрузка из MODX API

## 🔧 Implementation Steps

1. **Создать scheduler_modx.py** - новый планировщик
2. **Создать modx_cache.json** - структура данных
3. **Модифицировать api_server.py** - чтение из кэша
4. **Добавить /api/all endpoint** - возврат всех данных
5. **Модифицировать script.js** - загрузка всех данных
6. **Сохранить старые endpoint'ы** - для совместимости
7. **Протестировать** - новая архитектура

## 📊 Monitoring

- Логирование обновлений кэша
- Проверка целостности данных
- Fallback на MODX API при ошибках
- Мониторинг производительности

## 🚨 Important Notes

- **Парсер сохранен** в комментариях для возможного возврата
- **Старые endpoint'ы сохранены** для совместимости
- **Атомарная запись** предотвращает повреждение данных
- **Fallback стратегия** обеспечивает надежность
