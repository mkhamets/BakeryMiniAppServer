#!/bin/bash
# Скрипт для настройки сервера Bakery Bot

echo "🚀 Начинаем настройку сервера Bakery Bot..."

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
echo "📦 Установка базовых пакетов..."
sudo apt install -y curl wget git vim htop unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Установка Python 3.11
echo "🐍 Установка Python 3.11..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Установка pip для Python 3.11
echo "📦 Установка pip для Python 3.11..."
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Установка Docker
echo "🐳 Установка Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
echo "🐳 Установка Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка nginx
echo "🌐 Установка nginx..."
sudo apt install -y nginx

# Установка certbot для SSL
echo "🔒 Установка certbot для SSL..."
sudo apt install -y certbot python3-certbot-nginx

# Создание директории для приложения
echo "📁 Создание директорий..."
sudo mkdir -p /opt/bakery-bot/{data,logs,ssl,scripts,backups}
sudo chown -R $USER:$USER /opt/bakery-bot

# Настройка firewall
echo "🔥 Настройка firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

# Создание пользователя для приложения
echo "👤 Настройка пользователя..."
sudo useradd -r -s /bin/false -d /opt/bakery-bot bakery-app 2>/dev/null || true
sudo usermod -aG docker bakery-app 2>/dev/null || true

echo "✅ Базовая настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Перезайдите в систему для применения прав Docker"
echo "2. Скопируйте код приложения в /opt/bakery-bot/"
echo "3. Настройте переменные окружения"
echo "4. Запустите приложение"
echo ""
echo "🔄 Перезагрузка системы через 10 секунд..."
sleep 10
sudo reboot
