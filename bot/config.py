import os

BOT_TOKEN = "8127391261:AAHzeHTdXoOLt-4j98dm_41WWd8bZT53G3o"
BASE_WEBAPP_URL = "https://e653d5e4-945b-4845-b210-c8e4436510d8-00-1qk0jfa7quz7y.kirk.replit.dev/bot-app/"

# Добавлены переменные для администратора
# ВАЖНО: Замените 'ВАШ_ID_АДМИНИСТРАТОРА_ТЕЛЕГРАМ' на числовой ID чата вашего администратора.
# Вы можете узнать свой ID, написав боту @userinfobot в Telegram.
ADMIN_CHAT_ID = 707294339 # Пример: 123456789
ADMIN_EMAIL = "maxvindsvalr@gmail.com" # Email администратора
ADMIN_EMAIL_PASSWORD = os.environ.get("ADMIN_EMAIL_PASSWORD") # Пароль для SMTP (если используется)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com") # SMTP сервер (например, smtp.gmail.com)