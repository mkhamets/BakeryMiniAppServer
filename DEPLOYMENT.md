# 🚀 Deployment Guide - Bakery Mini App Server

## 🎯 Методы развертывания

### Heroku Deployment (Рекомендуется)

#### 1. Создание Heroku приложения
```bash
heroku create your-app-name
```

#### 2. Настройка переменных окружения
```bash
heroku config:set BOT_TOKEN="your_token"
heroku config:set ADMIN_CHAT_ID="your_id"
heroku config:set ADMIN_EMAIL="your_email"
heroku config:set BASE_WEBAPP_URL="https://your-app.herokuapp.com/bot-app/"
heroku config:set HMAC_SECRET="your_hmac_secret"
```

#### 3. Развертывание
```bash
git push heroku main
```

### Альтернативные методы развертывания

#### GitHub Actions
```yaml
name: Deploy to Heroku
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.14
      with:
        heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
        heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
```

#### Web Interface
1. Подключите GitHub репозиторий к Heroku
2. Включите автоматические развертывания
3. Настройте переменные окружения в панели управления

## 🔧 Конфигурационные файлы

### app.json
```json
{
  "name": "bakery-mini-app-server",
  "description": "Telegram WebApp for Bakery",
  "repository": "https://github.com/your-username/BakeryMiniAppServer",
  "logo": "https://your-app.herokuapp.com/logo.png",
  "keywords": ["telegram", "bot", "webapp", "bakery"],
  "env": {
    "BOT_TOKEN": {
      "description": "Telegram Bot Token",
      "required": true
    },
    "ADMIN_CHAT_ID": {
      "description": "Admin Telegram Chat ID",
      "required": true
    },
    "ADMIN_EMAIL": {
      "description": "Admin Email Address",
      "required": true
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "basic"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

### Procfile
```
web: python bot/main.py
worker: python scheduler.py
```

### requirements.txt
```
aiogram==3.4.1
aiosqlite==0.19.0
aiohttp==3.9.1
aiohttp-cors==0.7.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

## 📋 Переменные окружения

### Обязательные переменные
```bash
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_CHAT_ID=123456789
ADMIN_EMAIL=admin@example.com
BASE_WEBAPP_URL=https://your-app.herokuapp.com/bot-app/
```

### Дополнительные переменные
```bash
ADMIN_EMAIL_PASSWORD=your_smtp_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
HMAC_SECRET=your_hmac_secret_key
ENABLE_RATE_LIMITING=true
RATE_LIMIT_MAX_REQUESTS=100
LOG_LEVEL=INFO
```

## 🔄 Процесс развертывания

### 1. Подготовка
```bash
# Клонирование репозитория
git clone https://github.com/your-username/BakeryMiniAppServer.git
cd BakeryMiniAppServer

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Локальное тестирование
```bash
# Настройка переменных окружения
cp env.example .env
# Отредактируйте .env файл

# Запуск локально
python bot/main.py
```

### 3. Развертывание на Heroku
```bash
# Создание приложения
heroku create your-app-name

# Настройка переменных
heroku config:set BOT_TOKEN="your_token"
heroku config:set ADMIN_CHAT_ID="your_id"
heroku config:set ADMIN_EMAIL="your_email"

# Развертывание
git push heroku main
```

### 4. Проверка развертывания
```bash
# Проверка статуса
heroku ps

# Просмотр логов
heroku logs --tail

# Проверка конфигурации
heroku config
```

## 🛠️ Скрипты развертывания

### build.sh
```bash
#!/bin/bash
# Скрипт сборки и обновления кеша

echo "Building application..."
python -c "
import time
timestamp = int(time.time())
print(f'Cache busting timestamp: {timestamp}')
"

echo "Build completed successfully!"
```

### deploy.sh
```bash
#!/bin/bash
# Скрипт автоматизации развертывания

echo "Starting deployment..."

# Проверка статуса git
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Working directory not clean"
    exit 1
fi

# Развертывание на Heroku
git push heroku main

echo "Deployment completed!"
```

## 📊 Мониторинг развертывания

### Проверка здоровья приложения
```bash
# Проверка статуса
curl https://your-app.herokuapp.com/health

# Проверка API
curl https://your-app.herokuapp.com/bot-app/api/categories
```

### Логи и мониторинг
```bash
# Просмотр логов в реальном времени
heroku logs --tail

# Просмотр логов за последний час
heroku logs --since=1h

# Мониторинг метрик
heroku ps:scale web=1
```

## 🚨 Устранение неполадок развертывания

### Распространенные проблемы

#### 1. Ошибки сборки
```bash
# Проверка логов сборки
heroku logs --tail

# Проверка зависимостей
pip check
```

#### 2. Ошибки конфигурации
```bash
# Проверка переменных окружения
heroku config

# Проверка токена бота
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

#### 3. Проблемы с производительностью
```bash
# Масштабирование
heroku ps:scale web=2

# Проверка использования ресурсов
heroku ps
```

### Команды отладки
```bash
# Подключение к приложению
heroku run bash

# Проверка файловой системы
heroku run ls -la

# Тестирование подключения к базе данных
heroku run python -c "import sqlite3; print('DB OK')"
```

## 🔄 Обновления и откаты

### Обновление приложения
```bash
# Развертывание новой версии
git push heroku main

# Проверка статуса
heroku ps
```

### Откат к предыдущей версии
```bash
# Просмотр релизов
heroku releases

# Откат к предыдущему релизу
heroku rollback

# Откат к конкретному релизу
heroku rollback v123
```

---

**Последнее обновление:** 2025-09-03  
**Поддерживается:** Команда разработки
