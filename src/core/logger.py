import logging

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("lu_estilo")


def get_logger(name=None):
    return logger if name is None else logging.getLogger(f"lu_estilo.{name}")


logger = get_logger()
