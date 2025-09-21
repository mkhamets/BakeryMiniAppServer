# Развертывание на VPS с MODX API интеграцией

## 🏗️ Архитектура

```
VPS Server                    MODX Server (drazhin.by)
├── bot/                      ├── api/
│   ├── main.py              │   ├── products.php
│   ├── api_server.py        │   ├── categories.php
│   ├── config.py            │   └── test.php
│   └── web_app/             └── MODX CMS
├── run_api_only.py
├── run_bot_and_api.py
└── .env
```

## 🚀 Быстрый старт

### 1. Подготовка VPS сервера

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python 3.11+
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Устанавливаем зависимости системы
sudo apt install build-essential libssl-dev libffi-dev -y

# Создаем пользователя для приложения
sudo useradd -m -s /bin/bash bakery
sudo usermod -aG sudo bakery
```

### 2. Клонирование и настройка

```bash
# Переключаемся на пользователя bakery
sudo su - bakery

# Клонируем репозиторий
git clone https://github.com/mkhamets/BakeryMiniAppServer.git
cd BakeryMiniAppServer

# Переключаемся на нужную ветку
git checkout WebApp_MODXgetProducts

# Создаем виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 3. Настройка конфигурации

```bash
# Копируем пример конфигурации
cp env.vps.example .env

# Редактируем конфигурацию
nano .env
```

**Обязательные параметры в .env:**
```bash
# MODX API (уже настроен)
MODX_API_BASE_URL=https://drazhin.by/api

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# API Server
API_HOST=0.0.0.0
API_PORT=8080

# Security
HMAC_SECRET=your-secure-secret-key

# Web App URL
BASE_WEBAPP_URL=https://your-domain.com/bot-app
```

### 4. Запуск приложения

#### Вариант 1: Только API сервер (рекомендуется для начала)

```bash
# Запуск только API сервера
python run_api_only.py
```

#### Вариант 2: Бот + API сервер

```bash
# Запуск бота и API сервера вместе
python run_bot_and_api.py
```

### 5. Настройка systemd (автозапуск)

#### Создаем сервис для API:

```bash
sudo nano /etc/systemd/system/bakery-api.service
```

```ini
[Unit]
Description=Bakery API Server
After=network.target

[Service]
Type=simple
User=bakery
WorkingDirectory=/home/bakery/BakeryMiniAppServer
Environment=PATH=/home/bakery/BakeryMiniAppServer/venv/bin
ExecStart=/home/bakery/BakeryMiniAppServer/venv/bin/python run_api_only.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Создаем сервис для бота:

```bash
sudo nano /etc/systemd/system/bakery-bot.service
```

```ini
[Unit]
Description=Bakery Telegram Bot
After=network.target

[Service]
Type=simple
User=bakery
WorkingDirectory=/home/bakery/BakeryMiniAppServer
Environment=PATH=/home/bakery/BakeryMiniAppServer/venv/bin
ExecStart=/home/bakery/BakeryMiniAppServer/venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Активируем сервисы:

```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable bakery-api
sudo systemctl enable bakery-bot

# Запускаем сервисы
sudo systemctl start bakery-api
sudo systemctl start bakery-bot

# Проверяем статус
sudo systemctl status bakery-api
sudo systemctl status bakery-bot
```

### 6. Настройка Nginx (опционально)

```bash
# Устанавливаем Nginx
sudo apt install nginx -y

# Создаем конфигурацию
sudo nano /etc/nginx/sites-available/bakery
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /bot-app/ {
        proxy_pass http://127.0.0.1:8080/bot-app/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8080/bot-app/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Активируем конфигурацию
sudo ln -s /etc/nginx/sites-available/bakery /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔄 Включение парсера как fallback

Если MODX API недоступен, можно включить парсер как резервный источник данных:

1. **Раскомментировать** в `bot/api_server.py`:
   - `await load_products_data_for_api()` в `setup_api_server()`
   - Блоки FALLBACK в `get_products_for_webapp()` и `get_categories_for_webapp()`

2. **Создать файл** `data/products_scraped.json`:
   ```bash
   python parser_job.py
   ```

3. **Подробная инструкция** в файле `PARSER_FALLBACK_GUIDE.md`

## 🔧 Управление сервисами

```bash
# Запуск
sudo systemctl start bakery-api
sudo systemctl start bakery-bot

# Остановка
sudo systemctl stop bakery-api
sudo systemctl stop bakery-bot

# Перезапуск
sudo systemctl restart bakery-api
sudo systemctl restart bakery-bot

# Просмотр логов
sudo journalctl -u bakery-api -f
sudo journalctl -u bakery-bot -f

# Статус
sudo systemctl status bakery-api
sudo systemctl status bakery-bot
```

## 📊 Мониторинг

### Проверка API:

```bash
# Проверка доступности API
curl http://localhost:8080/bot-app/api/products

# Проверка категорий
curl http://localhost:8080/bot-app/api/categories

# Проверка Web App
curl http://localhost:8080/bot-app/
```

### Логи:

```bash
# Логи API сервера
tail -f /var/log/syslog | grep bakery-api

# Логи бота
tail -f /var/log/syslog | grep bakery-bot

# Все логи приложения
journalctl -u bakery-api -u bakery-bot -f
```

## 🔄 Обновление

```bash
# Переходим в директорию проекта
cd /home/bakery/BakeryMiniAppServer

# Останавливаем сервисы
sudo systemctl stop bakery-api bakery-bot

# Обновляем код
git pull origin WebApp_MODXgetProducts

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем зависимости (если нужно)
pip install -r requirements.txt

# Запускаем сервисы
sudo systemctl start bakery-api bakery-bot
```

## 🛠️ Отладка

### Проблемы с MODX API:

```bash
# Проверяем доступность MODX API
curl https://drazhin.by/api/test.php

# Проверяем товары
curl https://drazhin.by/api/products.php

# Проверяем категории
curl https://drazhin.by/api/categories.php
```

### Проблемы с приложением:

```bash
# Запуск в режиме отладки
cd /home/bakery/BakeryMiniAppServer
source venv/bin/activate
python run_api_only.py

# Проверка конфигурации
python -c "from bot.config import config; print(config.__dict__)"
```

## 📈 Производительность

### Рекомендации:

1. **Кэширование**: Добавить Redis для кэширования API ответов
2. **Мониторинг**: Настроить Prometheus + Grafana
3. **Логирование**: Настроить централизованное логирование
4. **SSL**: Настроить HTTPS через Let's Encrypt
5. **Балансировка**: Настроить несколько экземпляров API

### Мониторинг ресурсов:

```bash
# Использование CPU и памяти
htop

# Использование диска
df -h

# Сетевые соединения
netstat -tulpn | grep :8080
```

## 🔒 Безопасность

1. **Firewall**: Настроить UFW
2. **SSL**: Использовать Let's Encrypt
3. **Обновления**: Регулярно обновлять систему
4. **Мониторинг**: Настроить алерты
5. **Бэкапы**: Регулярно делать бэкапы конфигурации
