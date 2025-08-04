#!/usr/bin/env python3
"""
Скрипт для одноразового запуска парсера
Используется для Heroku Scheduler
"""

import asyncio
import logging
import os
import sys

# Добавляем корневую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.parser import main as parser_main

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция для запуска парсера"""
    try:
        logger.info("🚀 Запуск парсера через Heroku Scheduler")
        start_time = asyncio.get_event_loop().time()
        
        await parser_main()
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        logger.info(f"✅ Парсинг завершен успешно за {duration:.2f} секунд")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 