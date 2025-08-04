#!/bin/bash

# Скрипт для деплоя на Heroku

echo "🚀 Начинаем деплой на Heroku..."

# Проверяем, что мы в git репозитории
if [ ! -d ".git" ]; then
    echo "❌ Ошибка: Не найден git репозиторий"
    echo "Выполните: git init"
    exit 1
fi

# Проверяем, что Heroku CLI установлен
if ! command -v heroku &> /dev/null; then
    echo "❌ Ошибка: Heroku CLI не установлен"
    echo "Установите: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Проверяем, что пользователь залогинен в Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Войдите в Heroku..."
    heroku login
fi

# Спрашиваем имя приложения
read -p "Введите имя вашего Heroku приложения (или нажмите Enter для создания нового): " app_name

if [ -z "$app_name" ]; then
    echo "📝 Создаем новое приложение..."
    heroku create
    app_name=$(heroku apps:info --json | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
else
    echo "🔗 Подключаемся к существующему приложению..."
    heroku git:remote -a $app_name
fi

echo "📦 Добавляем файлы в git..."
git add .

echo "💾 Делаем коммит..."
git commit -m "Deploy to Heroku"

echo "🚀 Отправляем на Heroku..."
git push heroku main

echo "⚙️ Настраиваем переменные окружения..."
echo "⚠️ ВАЖНО: Установите переменные окружения вручную:"
echo "heroku config:set BOT_TOKEN=\"ваш_токен_бота\""
echo "heroku config:set BASE_WEBAPP_URL=\"https://$app_name.herokuapp.com/bot-app/\""
echo "heroku config:set ADMIN_CHAT_ID=\"ваш_id_администратора\""
echo "heroku config:set ADMIN_EMAIL=\"ваш_email@example.com\""

echo "🔍 Проверяем статус..."
heroku ps:scale web=1

echo "✅ Деплой завершен!"
echo "🌐 Откройте приложение: heroku open"
echo "📋 Проверьте логи: heroku logs --tail" 