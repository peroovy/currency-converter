import logging
from sys import stdout

from loguru import logger


LOG_FORMAT = "[{time:YYYY-MM-DD HH:mm:ss}][{name}:{function}][{level}] {message}"


def setup_logging(debug: bool) -> None:
    logger.remove()

    logger.add(
        sink=stdout,
        format=LOG_FORMAT,
        level=logging.DEBUG if debug else logging.INFO,
        enqueue=True,
    )
