import logging


def configure_logs():
    """Configure application logs."""
    LOG_FORMAT = "[%(asctime)s] - [%(process)d] - [%(levelname)s] - %(name)s.%(funcName)s - %(message)s"
    formatter = logging.Formatter(LOG_FORMAT)
