# config/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler


# === НАСТРОЙКИ ЛОГИРОВАНИЯ ===
class LogConfig:
    # Путь к логам
    LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
    LOG_FILE = os.path.join(LOG_DIR, "whale_watcher.log")

    # Уровни
    CONSOLE_LEVEL = logging.INFO   # logging.DEBUG  logging.INFO
    FILE_LEVEL = logging.DEBUG

    # Включение/отключение
    ENABLE_CONSOLE = True
    ENABLE_FILE = True

    # Ротация: 5 файлов по 10 МБ
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5


# === ГЛОБАЛЬНЫЙ ЛОГГЕР ===
def setup_global_logger():
    os.makedirs(LogConfig.LOG_DIR, exist_ok=True)

    # Очистка старых хендлеров
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s',
        datefmt='%Y-%m-%d %H:%m:%S'
    )

    # --- Консоль ---
    if LogConfig.ENABLE_CONSOLE:
        console = logging.StreamHandler()
        console.setLevel(LogConfig.CONSOLE_LEVEL)
        console.setFormatter(formatter)
        logging.root.addHandler(console)

    # --- Файл с ротацией ---
    if LogConfig.ENABLE_FILE:
        file_handler = RotatingFileHandler(
            LogConfig.LOG_FILE,
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(LogConfig.FILE_LEVEL)
        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)

    logging.info("Логирование инициализировано")
    logging.info(f"Лог-файл: {LogConfig.LOG_FILE}")