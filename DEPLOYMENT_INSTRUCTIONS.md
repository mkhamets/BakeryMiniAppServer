# 🚀 Инструкции по развертыванию Bakery Bot

## 📋 Подготовка

У вас есть все необходимые файлы:
- `setup_server.sh` - скрипт настройки сервера
- `deploy_app.sh` - скрипт развертывания приложения
- `env_template` - шаблон переменных окружения

## 🔧 Шаг 1: Настройка сервера

### Выполните на сервере:

```bash
# Скачайте скрипт настройки
wget https://raw.githubusercontent.com/your-repo/setup_server.sh
# ИЛИ скопируйте содержимое setup_server.sh в файл на сервере

# Сделайте исполняемым
chmod +x setup_server.sh

# Запустите настройку
./setup_server.sh
```

**Скрипт автоматически:**
- Обновит систему
- Установит Python 3.11, Docker, nginx
- Настроит firewall
- Создаст необходимые директории
- **Перезагрузит сервер**

## 📦 Шаг 2: Копирование кода приложения

### После перезагрузки сервера:

```bash
# Создайте директорию для приложения
sudo mkdir -p /opt/bakery-bot
sudo chown bot:bot /opt/bakery-bot

# Перейдите в директорию
cd /opt/bakery-bot

# Скопируйте код приложения (замените на ваш способ)
# Вариант 1: Git clone
git clone https://github.com/your-repo/BakeryMiniAppServer.git .

# Вариант 2: SCP с локальной машины
scp -r /path/to/BakeryMiniAppServer/* bot@192.168.100.5:/opt/bakery-bot/

# Вариант 3: Создание файлов вручную
# Скопируйте содержимое всех файлов из репозитория
```

## ⚙️ Шаг 3: Настройка переменных окружения

```bash
# Скопируйте шаблон
cp env_template .env

# Отредактируйте файл с реальными значениями
nano .env
```

### Заполните обязательные поля в .env:

```bash
# Токен бота от @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Ваш Telegram ID (получить от @userinfobot)
ADMIN_CHAT_ID=123456789

# Email для уведомлений
ADMIN_EMAIL=your-email@gmail.com

# Пароль приложения Gmail (НЕ обычный пароль!)
ADMIN_EMAIL_PASSWORD=your_app_password

# URL вашего домена (ЗАМЕНИТЕ!)
BASE_WEBAPP_URL=https://your-domain.com/bot-app/
```

## 🚀 Шаг 4: Развертывание приложения

```bash
# Скачайте скрипт развертывания
wget https://raw.githubusercontent.com/your-repo/deploy_app.sh
# ИЛИ скопируйте содержимое deploy_app.sh

# Сделайте исполняемым
chmod +x deploy_app.sh

# Запустите развертывание
./deploy_app.sh
```

## 🔒 Шаг 5: Настройка SSL

### Получите SSL сертификат:

```bash
# Замените your-domain.com на ваш домен
sudo certbot --nginx -d your-domain.com

# Или создайте самоподписанный сертификат для тестирования
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /opt/bakery-bot/ssl/key.pem \
    -out /opt/bakery-bot/ssl/cert.pem
```

## ▶️ Шаг 6: Запуск сервисов

```bash
# Запустите все сервисы
sudo systemctl start bakery-bot
sudo systemctl start bakery-parser
sudo systemctl start nginx

# Проверьте статус
sudo systemctl status bakery-bot
sudo systemctl status bakery-parser
sudo systemctl status nginx

# Включите автозапуск
sudo systemctl enable bakery-bot
sudo systemctl enable bakery-parser
sudo systemctl enable nginx
```

## ✅ Шаг 7: Проверка работы

### Проверьте логи:

```bash
# Логи бота
sudo journalctl -u bakery-bot -f

# Логи парсера
sudo journalctl -u bakery-parser -f

# Логи nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Проверьте доступность:

```bash
# Локально
curl http://localhost:80/bot-app/

# Внешне (замените на ваш домен)
curl https://your-domain.com/bot-app/
```

## 🔧 Управление сервисами

### Основные команды:

```bash
# Запуск
sudo systemctl start bakery-bot
sudo systemctl start bakery-parser

# Остановка
sudo systemctl stop bakery-bot
sudo systemctl stop bakery-parser

# Перезапуск
sudo systemctl restart bakery-bot
sudo systemctl restart bakery-parser

# Статус
sudo systemctl status bakery-bot
sudo systemctl status bakery-parser

# Логи
sudo journalctl -u bakery-bot -f
sudo journalctl -u bakery-parser -f
```

### Обновление приложения:

```bash
# Остановка сервисов
sudo systemctl stop bakery-bot
sudo systemctl stop bakery-parser

# Обновление кода
cd /opt/bakery-bot
git pull  # или скопируйте новые файлы

# Активация виртуального окружения
source venv/bin/activate

# Обновление зависимостей (если нужно)
pip install -r requirements.txt

# Запуск сервисов
sudo systemctl start bakery-bot
sudo systemctl start bakery-parser
```

## 💾 Бэкапы

### Автоматические бэкапы:
- Выполняются каждый день в 2:00 ночи
- Хранятся в `/opt/bakery-bot/backups/`
- Автоматически удаляются через 30 дней

### Ручной бэкап:
```bash
/opt/bakery-bot/scripts/backup.sh
```

### Восстановление:
```bash
# Остановка сервисов
sudo systemctl stop bakery-bot bakery-parser

# Восстановление данных
tar -xzf /opt/bakery-bot/backups/bakery-data-YYYYMMDD_HHMMSS.tar.gz

# Запуск сервисов
sudo systemctl start bakery-bot bakery-parser
```

## 🆘 Устранение неполадок

### Проверка портов:
```bash
sudo ss -tlnp | grep :80
sudo ss -tlnp | grep :80
sudo ss -tlnp | grep :443
```

### Проверка процессов:
```bash
ps aux | grep python
ps aux | grep nginx
```

### Проверка дискового пространства:
```bash
df -h
du -sh /opt/bakery-bot/*
```

### Проверка памяти:
```bash
free -h
top
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь, что все порты открыты
3. Проверьте права доступа к файлам
4. Убедитесь, что домен настроен правильно

**Удачи с развертыванием!** 🎉
