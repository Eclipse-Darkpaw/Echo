import logging
import logging.handlers
import sys
import os

COLOURS = {
    logging.DEBUG: "\033[36;1m",  # Bold Cyan
    logging.INFO: "\033[32;1m",   # Bold Green
    logging.WARNING: "\033[33;1m",  # Bold Yellow
    logging.ERROR: "\033[31;1m",  # Bold Red
    logging.CRITICAL: "\033[41;1m",  # Bold Red background
}

ORANGE = "\033[38;5;214m"  # Orange from 256-colour palette
LIGHT_GREY = "\033[90m"  # Dark Grey
ITALIC_GREY = "\033[3;90m"  # Italic Dark Grey

RESET = "\033[0m"  # Reset all styles

class ColourFormatter(logging.Formatter):
    def format(self, record):
        colour = COLOURS.get(record.levelno, RESET)
        
        timestamp = f"{LIGHT_GREY}{self.formatTime(record, self.datefmt)}{RESET}"
        
        levelname = f"{colour}{record.levelname:<8}{RESET}"
        name = f"{ORANGE}{record.name}{RESET}"
        message = record.getMessage()
        
        return f"{timestamp} [{levelname}] {name}: {message}"

def setup_logger(log_file = None, ignore_discord_logs_in_log_file=False,
                 file_log_level=logging.INFO, console_logging=True, console_log_level=logging.INFO):
    script_name = os.path.basename(sys.argv[0])
    logger = logging.getLogger(script_name)
    logger.setLevel(min(file_log_level, console_log_level))

    if logger.hasHandlers():
        logger.handlers.clear()

    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=5,  # Rotate through 5 files
        )
        file_formatter = logging.Formatter(
            '[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        file_handler.setLevel(file_log_level)

    if console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColourFormatter(
            '[{asctime}] [{levelname:<8}] {name}: {message}', 
            datefmt='%Y-%m-%d %H:%M:%S', 
            style='{'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        console_handler.setLevel(console_log_level)

    if ignore_discord_logs_in_log_file:
        null_handler = logging.NullHandler()
        logging.getLogger('discord').addHandler(null_handler)
        logging.getLogger('discord.http').addHandler(null_handler)

    # Capture logs for discord.py (and other libraries)
    logging.getLogger('discord').setLevel(min(file_log_level, console_log_level))
    logging.getLogger('discord').addHandler(console_handler)

    logging.getLogger('discord.http').setLevel(min(file_log_level, console_log_level))
    logging.getLogger('discord.http').addHandler(console_handler)

    return logger
