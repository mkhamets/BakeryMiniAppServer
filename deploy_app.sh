#!/bin/bash
# Скрипт для развертывания Bakery Bot приложения

echo "🚀 Развертывание Bakery Bot приложения..."

# Переход в директорию приложения
cd /opt/bakery-bot

# Создание виртуального окружения Python
echo "🐍 Создание виртуального окружения..."
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📦 Установка зависимостей Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание systemd сервиса для бота
echo "⚙️ Создание systemd сервиса для бота..."
sudo tee /etc/systemd/system/bakery-bot.service > /dev/null <<EOF
[Unit]
Description=Bakery Bot Service
After=network.target

[Service]
Type=simple
User=bot
Group=bot
WorkingDirectory=/opt/bakery-bot
Environment=PATH=/opt/bakery-bot/venv/bin
EnvironmentFile=/opt/bakery-bot/.env
ExecStart=/opt/bakery-bot/venv/bin/python bot/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Создание systemd сервиса для парсера
echo "⚙️ Создание systemd сервиса для парсера..."
sudo tee /etc/systemd/system/bakery-parser.service > /dev/null <<EOF
[Unit]
Description=Bakery Parser Service
After=network.target

[Service]
Type=simple
User=bot
Group=bot
WorkingDirectory=/opt/bakery-bot
Environment=PATH=/opt/bakery-bot/venv/bin
EnvironmentFile=/opt/bakery-bot/.env
ExecStart=/opt/bakery-bot/venv/bin/python parser_job.py start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Создание nginx конфигурации
echo "🌐 Создание nginx конфигурации..."
sudo tee /etc/nginx/sites-available/bakery-bot > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    # Перенаправление на HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name _;
    
    # SSL сертификаты (будут настроены позже)
    ssl_certificate /opt/bakery-bot/ssl/cert.pem;
    ssl_certificate_key /opt/bakery-bot/ssl/key.pem;
    
    # Проксирование на приложение
    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Активация сайта nginx
sudo ln -sf /etc/nginx/sites-available/bakery-bot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Создание скрипта бэкапа
echo "💾 Создание скрипта бэкапа..."
tee scripts/backup.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/opt/bakery-bot/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

# Создание бэкапа данных
tar -czf \$BACKUP_DIR/bakery-data-\$DATE.tar.gz data/ logs/ .env

# Удаление старых бэкапов (старше 30 дней)
find \$BACKUP_DIR -name "bakery-data-*" -mtime +30 -delete

echo "Backup completed: \$DATE"
EOF

chmod +x scripts/backup.sh

# Настройка cron для бэкапов
echo "⏰ Настройка автоматических бэкапов..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/bakery-bot/scripts/backup.sh >> /var/log/bakery-backup.log 2>&1") | crontab -

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
sudo chown -R bot:bot /opt/bakery-bot
chmod +x scripts/*.sh

# Перезагрузка systemd
echo "🔄 Перезагрузка systemd..."
sudo systemctl daemon-reload

# Включение сервисов
echo "🚀 Включение сервисов..."
sudo systemctl enable bakery-bot.service
sudo systemctl enable bakery-parser.service
sudo systemctl enable nginx

echo "✅ Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Настройте переменные окружения в .env файле"
echo "2. Получите SSL сертификат: sudo certbot --nginx"
echo "3. Запустите сервисы: sudo systemctl start bakery-bot bakery-parser nginx"
echo "4. Проверьте статус: sudo systemctl status bakery-bot bakery-parser"
EOF
