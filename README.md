# Bakery Mini App Server

Telegram бот с веб-приложением для заказов в пекарне.

## Деплой на Heroku

### 1. Подготовка

Убедитесь, что у вас установлены:
- Git
- Heroku CLI
- Python 3.11+

### 2. Создание приложения на Heroku

```bash
# Войдите в Heroku CLI
heroku login

# Создайте новое приложение
heroku create your-app-name

# Или подключитесь к существующему
heroku git:remote -a your-app-name
```

### 3. Настройка переменных окружения

```bash
# Установите переменные окружения
heroku config:set BOT_TOKEN="ваш_токен_бота"
heroku config:set BASE_WEBAPP_URL="https://your-app-name.herokuapp.com/bot-app/"
heroku config:set ADMIN_CHAT_ID="ваш_id_администратора"
heroku config:set ADMIN_EMAIL="ваш_email@example.com"
heroku config:set ADMIN_EMAIL_PASSWORD="пароль_для_smtp"  # опционально
heroku config:set SMTP_SERVER="smtp.gmail.com"  # опционально
```

### 4. Деплой

```bash
# Добавьте все файлы в git
git add .

# Сделайте коммит
git commit -m "Initial deployment"

# Отправьте на Heroku
git push heroku main
```

### 5. Проверка статуса

```bash
# Проверьте логи
heroku logs --tail

# Откройте приложение
heroku open
```

## Структура проекта

```
BakeryMiniAppServer/
├── bot/
│   ├── __init__.py
│   ├── api_server.py      # API сервер для веб-приложения
│   ├── config.py          # Конфигурация
│   ├── handlers.py        # Обработчики команд бота
│   ├── keyboards.py       # Клавиатуры
│   ├── main.py           # Главный файл бота
│   ├── parser.py         # Парсер данных
│   └── web_app/          # Веб-приложение
│       ├── index.html
│       ├── style.css
│       ├── script.js
│       └── Hleb.jpg
├── data/
│   ├── order_counter.json
│   └── products_scraped.json
├── Procfile              # Конфигурация для Heroku
├── requirements.txt      # Зависимости Python
├── runtime.txt          # Версия Python
└── app.json             # Описание приложения для Heroku
```

## Переменные окружения

- `BOT_TOKEN` - Токен вашего Telegram бота
- `BASE_WEBAPP_URL` - Базовый URL для веб-приложения
- `ADMIN_CHAT_ID` - ID чата администратора в Telegram
- `ADMIN_EMAIL` - Email администратора для уведомлений
- `ADMIN_EMAIL_PASSWORD` - Пароль для SMTP (опционально)
- `SMTP_SERVER` - SMTP сервер (по умолчанию: smtp.gmail.com)

## Возможные проблемы

### 1. Ошибка "No web processes running"

```bash
# Запустите веб-процесс
heroku ps:scale web=1
```

### 2. Ошибка с портом

Приложение автоматически использует переменную `PORT` от Heroku.

### 3. Проблемы с зависимостями

Убедитесь, что все зависимости указаны в `requirements.txt` с точными версиями.

### 4. Проблемы с файлами данных

Файлы в папке `data/` должны быть включены в репозиторий для работы приложения.

## Поддержка

При возникновении проблем проверьте логи:

```bash
heroku logs --tail
```
