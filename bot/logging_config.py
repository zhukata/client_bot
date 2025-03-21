import logging

# Настройка логирования
LOG_FILE = "project.log"

logging.basicConfig(
    level=logging.INFO,  # Уровень логов: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат логов
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль (можно убрать, если не нужно)
    ]
)

logger = logging.getLogger(__name__)