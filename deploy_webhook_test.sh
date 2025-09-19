#!/bin/bash

echo "🚀 Деплой webhook теста на сервер..."

# 1. Подключение к серверу и обновление кода
echo "1️⃣ Подключение к серверу..."
ssh drazhinb@drazhin.by << 'EOF'
cd /home/drazhinb/miniapp

echo "2️⃣ Обновление кода из GitHub..."
git fetch origin
git checkout WebApp_cacheFixing190925
git pull origin WebApp_cacheFixing190925

echo "3️⃣ Копирование обновленных файлов..."
cp wsgi.py /home/drazhinb/miniapp/
cp test_webhook.py /home/drazhinb/miniapp/

echo "4️⃣ Перезапуск приложения..."
touch tmp/restart.txt

echo "5️⃣ Проверка статуса..."
sleep 5
curl -I http://miniapp.drazhin.by/bot-app/api/webhook/test

echo "✅ Деплой завершен!"
EOF

echo "🏁 Локальный деплой завершен!"
