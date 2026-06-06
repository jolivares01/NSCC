import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler # <-- Cambiamos el Handler
from contextvars import ContextVar

user_context: ContextVar[str] = ContextVar("user_context", default="SYSTEM")

class UserContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'user'):
            record.user = user_context.get()
        return True

def setup_logger(service_name: str):
    logger = logging.getLogger(service_name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file_path = os.path.join(log_dir, f"{service_name}.log")

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(user)-12s | %(name)-15s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        logger.addFilter(UserContextFilter())

        # Handler para Consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # --- CAMBIO A ROTACIÓN POR TIEMPO ---
        file_handler = TimedRotatingFileHandler(
            log_file_path,
            when="midnight",    # Rota cada medianoche
            interval=1,         # Cada 1 día
            backupCount=30,      # Guarda los últimos 30 días de historial
            encoding="utf-8"
        )
        
        # Este sufijo hace que el archivo viejo se vea como: ROL-SERVICE.log.2026-04-05
        file_handler.suffix = "%Y-%m-%d" 
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger