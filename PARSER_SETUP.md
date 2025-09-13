# Настройка автоматического парсинга

## Варианты настройки

### Вариант 1: Heroku Scheduler (Рекомендуемый)

1. **Установите Heroku Scheduler:**
   ```bash
   heroku addons:create scheduler:standard
   ```

2. **Настройте задачу в веб-интерфейсе:**
   - Перейдите на https://dashboard.heroku.com/apps/bakery-mini-app-server/resources
   - Найдите "Heroku Scheduler" и нажмите "Open Dashboard"
   - Нажмите "Add Job"
   - Команда: `python run_parser.py`
   - Частота: "Every hour at 0 minutes past the hour"
   - Нажмите "Save Job"

### Вариант 2: Worker Process

1. **Запустите worker процесс:**
   ```bash
   heroku ps:scale worker=1
   ```

2. **Проверьте статус:**
   ```bash
   heroku ps
   ```

3. **Посмотрите логи worker:**
   ```bash
   heroku logs --tail --dyno worker
   ```

## Проверка работы парсера

### Проверка логов
```bash
# Все логи
heroku logs --tail

# Только логи парсера
heroku logs --tail | grep -i parser

# Логи worker процесса
heroku logs --tail --dyno worker
```

### Проверка файлов данных
```bash
# Проверить размер файла данных
heroku run "ls -la data/"

# Посмотреть содержимое файла
heroku run "head -20 data/products_scraped.json"
```

### Ручной запуск парсера
```bash
# Запустить парсер вручную
heroku run python run_parser.py

# Или через scheduler
heroku run python scheduler.py --once
```

## Мониторинг

### Проверка статуса процессов
```bash
heroku ps
```

### Проверка использования ресурсов
```bash
heroku logs --tail | grep -E "(parser|scheduler|worker)"
```

## Настройка интервала

### Изменение интервала в worker процессе
Отредактируйте `scheduler.py`:
```python
scheduler = ParserScheduler(interval_hours=2)  # Каждые 2 часа
```

### Изменение интервала в Heroku Scheduler
В веб-интерфейсе Heroku Scheduler измените частоту выполнения.

## Устранение неполадок

### Парсер не запускается
1. Проверьте логи: `heroku logs --tail`
2. Убедитесь, что все зависимости установлены
3. Проверьте доступность сайта drazhin.by

### Worker процесс падает
1. Проверьте логи worker: `heroku logs --tail --dyno worker`
2. Перезапустите worker: `heroku restart worker`

### Файл данных не обновляется
1. Проверьте права доступа к папке data
2. Убедитесь, что парсер завершается успешно
3. Проверьте размер файла: `heroku run "ls -la data/"`

## Рекомендации

1. **Используйте Heroku Scheduler** для продакшена - он более надежен
2. **Мониторьте логи** регулярно для выявления проблем
3. **Настройте уведомления** о сбоях парсера
4. **Делайте бэкапы** файла данных перед обновлением

## Команды для быстрой проверки

```bash
# Полный статус
heroku ps && echo "---" && heroku logs --tail -n 10

# Проверка файла данных
heroku run "wc -l data/products_scraped.json"

# Перезапуск всех процессов
heroku restart
``` 