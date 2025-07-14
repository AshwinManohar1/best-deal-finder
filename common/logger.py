import logging

logging.basicConfig(level=logging.INFO)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def info(message: str) -> None:
    logging.info(message)

def error(message: str) -> None:
    logging.error(message)

def debug(message: str) -> None:
    logging.debug(message)
    