#!/usr/bin/env python3
"""
Планировщик задач для автоматического запуска парсера
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
import time

# Добавляем корневую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.parser import main as parser_main

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

class ParserScheduler:
    def __init__(self, interval_hours=1):
        self.interval_hours = interval_hours
        self.running = False
        
    async def run_parser(self):
        """Запускает парсер и логирует результат"""
        try:
            logger.info("🔄 Запуск автоматического парсинга...")
            start_time = datetime.now()
            
            await parser_main()
            
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"✅ Парсинг завершен успешно за {duration}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге: {e}")
    
    async def schedule_parser(self):
        """Планирует запуск парсера каждый час"""
        logger.info(f"📅 Планировщик запущен. Парсинг будет выполняться каждые {self.interval_hours} час(ов)")
        
        while self.running:
            try:
                # Запускаем парсер
                await self.run_parser()
                
                # Ждем до следующего запуска
                next_run = datetime.now() + timedelta(hours=self.interval_hours)
                logger.info(f"⏰ Следующий запуск парсера: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Ждем указанное количество часов
                await asyncio.sleep(self.interval_hours * 3600)
                
            except asyncio.CancelledError:
                logger.info("🛑 Планировщик остановлен")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в планировщике: {e}")
                # Ждем 5 минут перед повторной попыткой
                await asyncio.sleep(300)
    
    def start(self):
        """Запускает планировщик"""
        self.running = True
        asyncio.run(self.schedule_parser())
    
    def stop(self):
        """Останавливает планировщик"""
        self.running = False

async def run_once():
    """Запускает парсер один раз (для Heroku Scheduler)"""
    try:
        logger.info("🚀 Запуск парсера (одноразовый режим)")
        await parser_main()
        logger.info("✅ Парсинг завершен")
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}")
        sys.exit(1)

def main():
    """Главная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Одноразовый запуск (для Heroku Scheduler)
        asyncio.run(run_once())
    else:
        # Непрерывный режим (для worker процесса)
        scheduler = ParserScheduler()
        try:
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал остановки")
            scheduler.stop()

if __name__ == "__main__":
    main() 