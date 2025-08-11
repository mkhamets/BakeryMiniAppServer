import os

# Получаем токен бота из переменных окружения Heroku
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8127391261:AAHCgjsz5co4REog4Tmgn6MY-WBdltuASjs")

# Получаем URL веб-приложения из переменных окружения
BASE_WEBAPP_URL = os.environ.get("BASE_WEBAPP_URL", "https://bakery-mini-app-server-440955f475ad.herokuapp.com/bot-app/")

# Добавлены переменные для администратора
# ВАЖНО: Замените 'ВАШ_ID_АДМИНИСТРАТОРА_ТЕЛЕГРАМ' на числовой ID чата вашего администратора.
# Вы можете узнать свой ID, написав боту @userinfobot в Telegram.
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "707294339"))  # Пример: 123456789
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "maxvindsvalr@gmail.com")  # Email администратора
ADMIN_EMAIL_PASSWORD = os.environ.get("ADMIN_EMAIL_PASSWORD")  # Пароль для SMTP (если используется)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")  # SMTP сервер (например, smtp.gmail.com)