# utils/logger.py
import logging
from config.logging_config import setup_global_logger

# Инициализация при импорте
setup_global_logger()

def get_logger(name: str = None):
    """
    Возвращает логгер с именем модуля
    """
    if name is None:
        import inspect
        frame = inspect.stack()[1]
        module = frame[0].f_globals.get('__name__', 'unknown')
        name = module
    return logging.getLogger(name)