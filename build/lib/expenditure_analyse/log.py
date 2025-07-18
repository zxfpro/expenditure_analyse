import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def setup_logging(level='info', log_file_name="app.log"):
    """
    Configures and returns a logger instance.

    Args:
        level (str): Logging level ('debug', 'info', 'warning', 'error', 'critical').
        log_file_name (str): Name of the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    LOG_DIR = "logs"
    LOG_FILE_PATH = os.path.join(LOG_DIR, log_file_name)

    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(__name__) # Use __name__ for module-specific logger
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not logger.handlers:
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(lineno)d - %(message)s'
        )

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO) # Console shows INFO and above
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler (RotatingFileHandler)
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=10 * 1024 * 1024, # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level) # File shows all specified level logs
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
