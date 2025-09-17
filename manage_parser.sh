#!/bin/bash
# Скрипт для управления автоматическим парсингом

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="bakery-parser"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PYTHON_SCRIPT="${SCRIPT_DIR}/parser_job.py"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}📊 СТАТУС СИСТЕМЫ ПАРСИНГА${NC}"
    echo "=================================="
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "🔄 Сервис: ${GREEN}АКТИВЕН${NC}"
    else
        echo -e "🔄 Сервис: ${RED}НЕ АКТИВЕН${NC}"
    fi
    
    if systemctl is-enabled --quiet $SERVICE_NAME; then
        echo -e "⚡ Автозапуск: ${GREEN}ВКЛЮЧЕН${NC}"
    else
        echo -e "⚡ Автозапуск: ${RED}ВЫКЛЮЧЕН${NC}"
    fi
    
    echo ""
    python3 $PYTHON_SCRIPT status
}

install_service() {
    echo -e "${YELLOW}🔧 Установка сервиса...${NC}"
    
    # Обновляем пути в service файле
    sed "s|/path/to/BakeryMiniAppServer|$SCRIPT_DIR|g" "${SCRIPT_DIR}/bakery-parser.service" > /tmp/${SERVICE_NAME}.service
    
    # Копируем service файл
    sudo cp /tmp/${SERVICE_NAME}.service $SERVICE_FILE
    sudo systemctl daemon-reload
    
    echo -e "${GREEN}✅ Сервис установлен${NC}"
    echo "Файл сервиса: $SERVICE_FILE"
}

uninstall_service() {
    echo -e "${YELLOW}🗑️ Удаление сервиса...${NC}"
    
    sudo systemctl stop $SERVICE_NAME 2>/dev/null
    sudo systemctl disable $SERVICE_NAME 2>/dev/null
    sudo rm -f $SERVICE_FILE
    sudo systemctl daemon-reload
    
    echo -e "${GREEN}✅ Сервис удален${NC}"
}

start_service() {
    echo -e "${YELLOW}🚀 Запуск сервиса...${NC}"
    sudo systemctl start $SERVICE_NAME
    sleep 2
    print_status
}

stop_service() {
    echo -e "${YELLOW}🛑 Остановка сервиса...${NC}"
    sudo systemctl stop $SERVICE_NAME
    print_status
}

enable_service() {
    echo -e "${YELLOW}⚡ Включение автозапуска...${NC}"
    sudo systemctl enable $SERVICE_NAME
    print_status
}

disable_service() {
    echo -e "${YELLOW}⚡ Выключение автозапуска...${NC}"
    sudo systemctl disable $SERVICE_NAME
    print_status
}

enable_parsing() {
    echo -e "${YELLOW}🔄 Включение автоматического парсинга...${NC}"
    python3 $PYTHON_SCRIPT enable
}

disable_parsing() {
    echo -e "${YELLOW}🔄 Выключение автоматического парсинга...${NC}"
    python3 $PYTHON_SCRIPT disable
}

run_once() {
    echo -e "${YELLOW}🔄 Запуск разового парсинга...${NC}"
    python3 $PYTHON_SCRIPT run-once
}

show_logs() {
    echo -e "${YELLOW}📋 Показ логов сервиса...${NC}"
    sudo journalctl -u $SERVICE_NAME -f --lines=50
}

show_help() {
    echo -e "${BLUE}📖 СПРАВКА ПО УПРАВЛЕНИЮ ПАРСЕРОМ${NC}"
    echo "=========================================="
    echo ""
    echo "Установка и настройка:"
    echo "  $0 install     - Установить systemd сервис"
    echo "  $0 uninstall   - Удалить systemd сервис"
    echo ""
    echo "Управление сервисом:"
    echo "  $0 start       - Запустить сервис"
    echo "  $0 stop        - Остановить сервис"
    echo "  $0 enable      - Включить автозапуск"
    echo "  $0 disable     - Выключить автозапуск"
    echo "  $0 restart     - Перезапустить сервис"
    echo ""
    echo "Управление парсингом:"
    echo "  $0 parsing-on  - Включить автоматический парсинг"
    echo "  $0 parsing-off - Выключить автоматический парсинг"
    echo "  $0 run-once    - Запустить парсинг один раз"
    echo ""
    echo "Мониторинг:"
    echo "  $0 status      - Показать статус"
    echo "  $0 logs        - Показать логи"
    echo "  $0 help        - Показать эту справку"
    echo ""
}

# Проверяем аргументы
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

case "$1" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    restart)
        stop_service
        sleep 2
        start_service
        ;;
    parsing-on)
        enable_parsing
        ;;
    parsing-off)
        disable_parsing
        ;;
    run-once)
        run_once
        ;;
    status)
        print_status
        ;;
    logs)
        show_logs
        ;;
    help)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Неизвестная команда: $1${NC}"
        show_help
        exit 1
        ;;
esac

