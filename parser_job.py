#!/usr/bin/env python3
"""
Автоматический парсер с возможностью включения/выключения
Запускается каждые 3 минуты и обновляет файл продуктов
"""

import asyncio
import logging
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.parser import main as parser_main

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Файл для управления состоянием job
JOB_CONTROL_FILE = "data/parser_job_control.json"
# Интервал между запусками (в секундах) - 3 минуты
PARSER_INTERVAL = 3 * 60  # 180 секунд

class ParserJobController:
    """Контроллер для управления автоматическим парсингом"""
    
    def __init__(self):
        self.control_file = Path(JOB_CONTROL_FILE)
        self.ensure_control_file()
    
    def ensure_control_file(self):
        """Создает файл управления если его нет"""
        if not self.control_file.exists():
            self.control_file.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                "enabled": False,  # По умолчанию выключен
                "last_run": None,
                "next_run": None,
                "run_count": 0,
                "last_success": None,
                "last_error": None,
                "created_at": datetime.now().isoformat()
            }
            with open(self.control_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            logger.info(f"Создан файл управления: {self.control_file}")
    
    def load_config(self):
        """Загружает конфигурацию из файла"""
        try:
            with open(self.control_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {"enabled": False}
    
    def save_config(self, config):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.control_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
    
    def is_enabled(self):
        """Проверяет включен ли автоматический парсинг"""
        config = self.load_config()
        return config.get("enabled", False)
    
    def enable(self):
        """Включает автоматический парсинг"""
        config = self.load_config()
        config["enabled"] = True
        config["next_run"] = datetime.now().isoformat()
        self.save_config(config)
        logger.info("✅ Автоматический парсинг включен")
    
    def disable(self):
        """Выключает автоматический парсинг"""
        config = self.load_config()
        config["enabled"] = False
        config["next_run"] = None
        self.save_config(config)
        logger.info("❌ Автоматический парсинг выключен")
    
    def update_last_run(self, success=True, error=None):
        """Обновляет информацию о последнем запуске"""
        config = self.load_config()
        config["last_run"] = datetime.now().isoformat()
        config["run_count"] = config.get("run_count", 0) + 1
        
        if success:
            config["last_success"] = config["last_run"]
            config["last_error"] = None
        else:
            config["last_error"] = config["last_run"]
        
        # Планируем следующий запуск если включен
        if config.get("enabled", False):
            next_run_time = datetime.now().timestamp() + PARSER_INTERVAL
            config["next_run"] = datetime.fromtimestamp(next_run_time).isoformat()
        
        self.save_config(config)
    
    def get_status(self):
        """Возвращает статус системы"""
        config = self.load_config()
        return {
            "enabled": config.get("enabled", False),
            "last_run": config.get("last_run"),
            "next_run": config.get("next_run"),
            "run_count": config.get("run_count", 0),
            "last_success": config.get("last_success"),
            "last_error": config.get("last_error"),
            "interval_minutes": PARSER_INTERVAL // 60
        }

async def run_parser():
    """Запускает парсер и обновляет файл продуктов"""
    try:
        logger.info("🔄 Запуск автоматического парсинга...")
        start_time = time.time()
        
        await parser_main()
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"✅ Парсинг завершен успешно за {duration:.2f} секунд")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}")
        return False

async def main_loop():
    """Основной цикл автоматического парсинга"""
    controller = ParserJobController()
    
    logger.info("🚀 Запуск системы автоматического парсинга")
    logger.info(f"📊 Интервал: {PARSER_INTERVAL // 60} минут")
    logger.info(f"📁 Файл управления: {JOB_CONTROL_FILE}")
    
    while True:
        try:
            if controller.is_enabled():
                logger.info("⏰ Время запуска парсера")
                success = await run_parser()
                controller.update_last_run(success=success)
            else:
                logger.debug("⏸️ Автоматический парсинг выключен")
            
            # Ждем до следующего запуска
            await asyncio.sleep(PARSER_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал остановки")
            break
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в основном цикле: {e}")
            controller.update_last_run(success=False, error=str(e))
            await asyncio.sleep(60)  # Ждем минуту перед повтором

def show_status():
    """Показывает статус системы"""
    controller = ParserJobController()
    status = controller.get_status()
    
    print("\n" + "="*50)
    print("📊 СТАТУС СИСТЕМЫ АВТОМАТИЧЕСКОГО ПАРСИНГА")
    print("="*50)
    print(f"🔄 Включен: {'✅ ДА' if status['enabled'] else '❌ НЕТ'}")
    print(f"⏱️  Интервал: {status['interval_minutes']} минут")
    print(f"🔢 Запусков: {status['run_count']}")
    
    if status['last_run']:
        print(f"🕐 Последний запуск: {status['last_run']}")
    
    if status['next_run']:
        print(f"⏭️  Следующий запуск: {status['next_run']}")
    
    if status['last_success']:
        print(f"✅ Последний успех: {status['last_success']}")
    
    if status['last_error']:
        print(f"❌ Последняя ошибка: {status['last_error']}")
    
    print("="*50)

def show_help():
    """Показывает справку по командам"""
    print("\n" + "="*50)
    print("📖 СПРАВКА ПО КОМАНДАМ")
    print("="*50)
    print("python parser_job.py start     - Запустить автоматический парсинг")
    print("python parser_job.py stop      - Остановить автоматический парсинг")
    print("python parser_job.py enable    - Включить автоматический парсинг")
    print("python parser_job.py disable   - Выключить автоматический парсинг")
    print("python parser_job.py status    - Показать статус системы")
    print("python parser_job.py run-once  - Запустить парсинг один раз")
    print("python parser_job.py help      - Показать эту справку")
    print("="*50)

async def run_once():
    """Запускает парсинг один раз"""
    controller = ParserJobController()
    logger.info("🔄 Запуск разового парсинга...")
    success = await run_parser()
    controller.update_last_run(success=success)
    return success

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        asyncio.run(main_loop())
    elif command == "enable":
        controller = ParserJobController()
        controller.enable()
        show_status()
    elif command == "disable":
        controller = ParserJobController()
        controller.disable()
        show_status()
    elif command == "status":
        show_status()
    elif command == "run-once":
        success = asyncio.run(run_once())
        sys.exit(0 if success else 1)
    elif command == "help":
        show_help()
    else:
        print(f"❌ Неизвестная команда: {command}")
        show_help()
        sys.exit(1)
