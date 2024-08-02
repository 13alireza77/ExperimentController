import logging

from registry.config import LOG_FORMAT
from registry.log_stream.handler import KafkaLoggingHandler


def setup_logger(name, logging_handler, level=logging.INFO, experiment=None):
    """Setup a logger that streams to Kafka with a specific label."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Format including the experiment label if provided
    formatter = logging.Formatter(LOG_FORMAT.format(experiment))

    # Kafka logging handler
    logging_handler.setFormatter(formatter)
    logger.addHandler(logging_handler)

    return logger
