import logging
import os
from logging.handlers import RotatingFileHandler


def logger_setup():
    logFileName = "logs/BirthdayBot.log"
    doRollOver = os.path.isfile(logFileName)

    os.makedirs(os.path.dirname(logFileName), exist_ok=True)

    streamHandler = logging.StreamHandler()
    rotatingFileHandler = RotatingFileHandler(
        filename=logFileName,
        encoding="utf-8",
        mode="w",
        maxBytes=1024 * 1024 * 10,
        backupCount=5,
    )

    logging.basicConfig(
        level=logging.INFO,
        style="{",
        datefmt="%d.%m.%Y %H:%M:%S",
        format="[{asctime}] [{levelname:^6s}] {name}: {message}",
        handlers=[streamHandler, rotatingFileHandler],
    )

    if doRollOver:
        rotatingFileHandler.doRollover()
