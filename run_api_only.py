#!/usr/bin/env python3
"""
Простой скрипт для запуска только API сервера без бота
"""
import asyncio
import logging
import os
from aiohttp import web
from bot.api_server import setup_api_server

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Запускаем только API сервер"""
    logger.info("Запуск API сервера...")
    
    # Настраиваем API сервер
    runner = await setup_api_server()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    # Запускаем сервер
    await site.start()
    logger.info(f"API сервер запущен на http://0.0.0.0:{port}")
    logger.info(f"Web App доступно по адресу: http://localhost:{port}/bot-app/")
    
    try:
        # Держим сервер запущенным
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Остановка сервера...")
    finally:
        await runner.cleanup()
        logger.info("API сервер остановлен.")

if __name__ == "__main__":
    asyncio.run(main())
