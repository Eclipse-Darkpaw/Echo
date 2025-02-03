import logging
import logging.handlers
import os
import sys

class ANSI:
    _ESCAPE_CHAR = '\033'
    _CSI = '['  # Control Sequence Introducer
    _DELIMITER = ';'
    _TERMINATOR = 'm'

    CODES = {
        'transform': {
            'reset': 0,
            'bold': 1,
            'italic': 3,
            'underline': 4,
            'reversed': 7
        },
        'foreground': {
            'black': 30,
            'red': 31,
            'green': 32,
            'yellow': 33,
            'blue': 34,
            'magenta': 35,
            'cyan': 36,
            'white': 37,
            'bright_black': 90,
            'bright_red': 91,
            'bright_green': 92,
            'bright_yellow': 93,
            'bright_blue': 94,
            'bright_magenta': 95,
            'bright_cyan': 96,
            'bright_white': 97
        },
        'background': {
            'red': 49,
            'green': 50,
            'yellow': 51,
            'blue': 52,
            'magenta': 53,
            'cyan': 54,
            'white': 55
        }
    }

    @classmethod
    def get_log_level_codes(cls, level):
        log_level_colors = {
            logging.DEBUG: cls.CODES['foreground']['cyan'],
            logging.INFO: cls.CODES['foreground']['green'],
            logging.WARNING: cls.CODES['foreground']['yellow'],
            logging.ERROR: cls.CODES['foreground']['red'],
            logging.CRITICAL: cls.CODES['foreground']['bright_red']
        }

        return [cls.CODES['transform']['bold'], log_level_colors.get(level, cls.CODES['foreground']['white'])]
    
    @classmethod
    def _build_sequence(cls, *codes):
        return f'{cls._ESCAPE_CHAR}{cls._CSI}{cls._DELIMITER.join(map(str, codes))}{cls._TERMINATOR}'

    @classmethod
    def set_on_text(cls, text, *codes):
        return f'{cls._build_sequence(*codes)}{text}{cls._build_sequence(cls.CODES['transform']['reset'])}'

class FancyFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', **kwargs):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, **kwargs)

    def formatTime(self, record, datefmt=None):
        base_time = super().formatTime(record, datefmt)
        return ANSI.set_on_text(base_time, ANSI.CODES['foreground']['bright_black'], ANSI.CODES['transform']['italic'])

    def format(self, record):
        record.levelname = ANSI.set_on_text(f'{record.levelname:<8}', *ANSI.get_log_level_codes(record.levelno))
        record.name = ANSI.set_on_text(record.filename, ANSI.CODES['foreground']['blue'])

        return super().format(record)

def setup_logger(console_logging=True, console_log_level=logging.INFO, ignore_discord_logs=False,
                 log_file=None, file_log_level=logging.INFO, max_file_size=2048, file_log_rotation_count=10):
    """
    Configures a logger that captures log messages, formats them, and outputs them to specified destinations, such as console and log files.

    Last docstring edit: -FoxyHunter V4.3.0
    Last method edit: -FoxyHunter V4.3.0
    :param console_logging: (default=True) Whether or not to log to the console.
    :param console_log_level: (default=logging.INFO) The log level of the console output.
    :param ignore_discord_logs: (default=False) Whether or not to include logs from discord.py (discord & discord.http) in the logs.

    :param log_file: (default=None) If you want to enable file logging; the path to the file location, the file does not need to exist yet.
    :param file_log_level: (default=logging.INFO) Log level of the log file
    :param max_file_size: (default=2048) Maximum log file size in KiB
    :param file_log_rotation_count: (default=5) When the maximum log file is exceeded, a "backup is created, this number defines the maxiumum to rotate through.
    
    :return: logger
    """
    script_name = os.path.basename(sys.argv[0])

    logger = logging.getLogger(script_name)
    modules_logger = logging.getLogger('modules')
    utils_logger = logging.getLogger('utils')

    logger.setLevel(min(file_log_level, console_log_level))
    modules_logger.setLevel(min(file_log_level, console_log_level))
    utils_logger.setLevel(min(file_log_level, console_log_level))

    if logger.hasHandlers():
        logger.handlers.clear()

    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            encoding='utf-8',
            maxBytes=max_file_size*1024,
            backupCount=file_log_rotation_count
        )
        
        file_formatter = logging.Formatter(
            '[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'
        )

        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(file_log_level)

        logger.addHandler(file_handler)
        modules_logger.addHandler(file_handler)
        utils_logger.addHandler(file_handler)

    if console_logging:
        console_handler = logging.StreamHandler(sys.stdout)

        console_formatter = FancyFormatter(
            '{asctime}   [{levelname:<8} ]  {name}: {message}', 
            datefmt='%Y-%m-%d %H:%M:%S', 
            style='{'
        )

        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(console_log_level)

        logger.addHandler(console_handler)
        modules_logger.addHandler(console_handler)
        utils_logger.addHandler(console_handler)

    if ignore_discord_logs:
        null_handler = logging.NullHandler()
        logging.getLogger('discord').addHandler(null_handler)
        logging.getLogger('discord.http').addHandler(null_handler)
    else:
        discord_logger = logging.getLogger('discord')
        discord_http_logger = logging.getLogger('discord.http')

        discord_logger.setLevel(min(file_log_level, console_log_level))
        discord_logger.addHandler(console_handler)
        discord_logger.addHandler(file_handler)

        discord_http_logger.setLevel(min(file_log_level, console_log_level))
        discord_http_logger.addHandler(console_handler)
        discord_http_logger.addHandler(file_handler)

    return logger
