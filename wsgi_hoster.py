#!/usr/bin/env python3
"""
WSGI entry point для Hoster.by
Специально адаптированный для их системы
"""

import os
import sys
import asyncio
import threading
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Импортируем основное приложение
from bot.main import main as bot_main

# Глобальная переменная для хранения задачи бота
bot_task = None
bot_thread = None

def start_bot():
    """Запуск бота в отдельном потоке"""
    global bot_task, bot_thread
    
    if bot_task is None or bot_task.done():
        print("🚀 Starting Bakery Bot...")
        
        # Создаем новый event loop для потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Запускаем бота
            loop.run_until_complete(bot_main())
        except Exception as e:
            print(f"❌ Bot error: {e}")
            loop.close()

def application(environ, start_response):
    """
    WSGI application entry point для Hoster.by
    """
    global bot_thread
    
    try:
        # Запускаем бота в отдельном потоке, если еще не запущен
        if bot_thread is None or not bot_thread.is_alive():
            bot_thread = threading.Thread(target=start_bot, daemon=True)
            bot_thread.start()
            
            # Ждем немного, чтобы бот успел запуститься
            import time
            time.sleep(2)
        
        # Возвращаем простой ответ
        status = '200 OK'
        headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
        ]
        
        start_response(status, headers)
        
        # HTML ответ с информацией о статусе
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Bakery Bot - Hoster.by</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .status { color: #28a745; font-weight: bold; }
                .info { color: #6c757d; margin-top: 20px; }
                .link { color: #007bff; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🍞 Bakery Bot</h1>
                <p class="status">✅ Bot is running on Hoster.by</p>
                <p>Telegram bot for Дражина bakery is successfully deployed and running.</p>
                
                <div class="info">
                    <h3>📋 Deployment Info:</h3>
                    <ul>
                        <li><strong>URL:</strong> miniapp.drazhin.by/bot-app/</li>
                        <li><strong>Python:</strong> 3.11.13</li>
                        <li><strong>Status:</strong> Active</li>
                        <li><strong>Web App:</strong> <a href="/bot-app/" class="link">Open Web App</a></li>
                    </ul>
                </div>
                
                <div class="info">
                    <h3>🔧 Technical Details:</h3>
                    <ul>
                        <li><strong>WSGI Entry Point:</strong> application</li>
                        <li><strong>Bot Thread:</strong> Running</li>
                        <li><strong>Environment:</strong> Production</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        return [html_content.encode('utf-8')]
        
    except Exception as e:
        # Обработка ошибок
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        
        error_message = f"❌ WSGI Error: {str(e)}"
        return [error_message.encode('utf-8')]

# Альтернативная функция для отладки
def debug_application(environ, start_response):
    """Отладочная версия для тестирования"""
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    
    debug_info = f"""
🔧 Debug Info:
- Python: {sys.version}
- Path: {sys.path[:3]}
- Environment: {dict(list(environ.items())[:5])}
- Project Root: {project_root}
- Files in root: {list(project_root.glob('*'))[:5]}
"""
    return [debug_info.encode('utf-8')]
