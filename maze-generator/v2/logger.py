import logging

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',   # Blue
        'INFO': '\033[92m',    # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',   # Red
        'CRITICAL': '\033[91m' # Red
    }
    RESET = '\033[0m'

    def format(self, record):
        log_message = super().format(record)
        log_level = record.levelname
        color_code = self.COLORS.get(log_level, '')
        return f"{color_code}{log_message}{self.RESET}"

def create(name, level=logging.INFO) -> logging.Logger:

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a console handler and set the formatter
    console_handler = logging.StreamHandler()
    formatter = ColoredFormatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    return logger

if __name__ == 'logger':
    console = create('CONSOLE', INFO)