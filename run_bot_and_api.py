#!/usr/bin/env python3
"""
Запуск бота и API сервера вместе для VPS
Использует MODX API для получения данных о продуктах и категориях
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot.main import main as bot_main
from bot.api_server import setup_api_server
from bot.config import config
from aiohttp import web

# Настраиваем логирование
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def run_bot():
    """Запуск Telegram бота"""
    logger.info("🤖 Запуск Telegram бота...")
    try:
        await bot_main()
    except Exception as e:
        logger.error(f"❌ Ошибка в боте: {e}")

async def run_api():
    """Запуск API сервера"""
    logger.info("🚀 Запуск API сервера...")
    
    # Получаем конфигурацию из переменных окружения
    host = os.environ.get('API_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', os.environ.get('API_PORT', '8080')))
    
    try:
        # Настраиваем API сервер (setup_api_server возвращает AppRunner)
        runner = await setup_api_server()
        
        # Запускаем сервер
        site = web.TCPSite(runner.app, host, port)
        await site.start()
        
        logger.info(f"✅ API сервер запущен на http://{host}:{port}")
        
        # Ждем завершения
        try:
            await asyncio.Future()  # Запускаем бесконечный цикл
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал остановки...")
        finally:
            await runner.cleanup()
            logger.info("✅ API сервер остановлен")
            
    except Exception as e:
        logger.error(f"❌ Ошибка запуска API сервера: {e}")
        raise

async def main():
    """Основная функция запуска бота и API"""
    logger.info("🚀 Запуск бота и API сервера с MODX интеграцией...")
    logger.info(f"🔗 MODX API: {os.environ.get('MODX_API_BASE_URL', 'https://drazhin.by/api')}")
    
    # Создаем задачи для параллельного запуска
    bot_task = asyncio.create_task(run_bot())
    api_task = asyncio.create_task(run_api())
    
    try:
        # Запускаем обе задачи параллельно
        await asyncio.gather(bot_task, api_task)
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки...")
        
        # Отменяем задачи
        bot_task.cancel()
        api_task.cancel()
        
        # Ждем завершения задач
        try:
            await asyncio.gather(bot_task, api_task, return_exceptions=True)
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке: {e}")
        
        logger.info("✅ Бот и API сервер остановлены")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Принудительная остановка...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
