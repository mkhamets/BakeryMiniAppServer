# Альтернативные способы деплоя на Heroku

## Способ 1: Деплой через веб-интерфейс Heroku

### 1. Подготовка репозитория

Убедитесь, что ваш код находится в GitHub репозитории:

```bash
# Добавьте удаленный репозиторий (если еще не добавлен)
git remote add origin https://github.com/yourusername/BakeryMiniAppServer.git

# Отправьте код на GitHub
git push -u origin WebApp_To_Heroku
```

### 2. Создание приложения на Heroku

1. Перейдите на [dashboard.heroku.com](https://dashboard.heroku.com)
2. Нажмите "New" → "Create new app"
3. Введите имя приложения
4. Выберите регион
5. Нажмите "Create app"

### 3. Подключение к GitHub

1. В настройках приложения перейдите на вкладку "Deploy"
2. В разделе "Deployment method" выберите "GitHub"
3. Подключите ваш GitHub аккаунт
4. Выберите репозиторий `BakeryMiniAppServer`
5. Выберите ветку `WebApp_To_Heroku`

### 4. Настройка переменных окружения

1. Перейдите на вкладку "Settings"
2. Нажмите "Reveal Config Vars"
3. Добавьте следующие переменные:

```
BOT_TOKEN = ваш_токен_бота
BASE_WEBAPP_URL = https://your-app-name.herokuapp.com/bot-app/
ADMIN_CHAT_ID = ваш_id_администратора
ADMIN_EMAIL = ваш_email@example.com
ADMIN_EMAIL_PASSWORD = пароль_для_smtp (опционально)
SMTP_SERVER = smtp.gmail.com (опционально)
```

### 5. Деплой

1. Вернитесь на вкладку "Deploy"
2. Нажмите "Deploy Branch"
3. Дождитесь завершения сборки

## Способ 2: Деплой через GitHub Actions

### 1. Создайте файл .github/workflows/deploy.yml

```yaml
name: Deploy to Heroku

on:
  push:
    branches: [ WebApp_To_Heroku ]

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
        heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

### 2. Настройте секреты в GitHub

1. Перейдите в настройки репозитория → Secrets and variables → Actions
2. Добавьте следующие секреты:
   - `HEROKU_API_KEY` - ваш API ключ Heroku
   - `HEROKU_APP_NAME` - имя вашего приложения
   - `HEROKU_EMAIL` - ваш email для Heroku

### 3. Получите API ключ Heroku

1. Перейдите на [dashboard.heroku.com/account](https://dashboard.heroku.com/account)
2. Прокрутите вниз до "API Key"
3. Скопируйте ключ

## Способ 3: Установка Heroku CLI без sudo

### 1. Установка через conda (если у вас есть Anaconda)

```bash
conda install -c conda-forge heroku
```

### 2. Установка через pip

```bash
pip install heroku
```

### 3. Ручная установка

```bash
# Скачайте установщик
curl -O https://cli-assets.heroku.com/heroku-darwin-x64.tar.gz

# Распакуйте в домашнюю директорию
tar -xzf heroku-darwin-x64.tar.gz -C ~/

# Добавьте в PATH
echo 'export PATH="$HOME/heroku/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Проверка деплоя

После любого способа деплоя:

1. Откройте приложение: `https://your-app-name.herokuapp.com`
2. Проверьте логи в веб-интерфейсе Heroku
3. Убедитесь, что веб-процесс запущен

## Возможные проблемы

### 1. "No web processes running"

В веб-интерфейсе Heroku:
1. Перейдите на вкладку "Resources"
2. Нажмите "Edit" рядом с "web"
3. Установите количество dynos в 1
4. Нажмите "Confirm"

### 2. Ошибки сборки

Проверьте логи в веб-интерфейсе Heroku на вкладке "Activity".

### 3. Проблемы с переменными окружения

Убедитесь, что все переменные окружения установлены правильно в настройках приложения. 