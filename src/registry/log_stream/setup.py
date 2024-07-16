import logging

from registry.config import LOG_FORMAT
from registry.log_stream.handler import KafkaLoggingHandler


def setup_logger(name, topic, level=logging.INFO, experiment=None):
    """Setup a logger that streams to Kafka with a specific label."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Format including the experiment label if provided
    formatter = logging.Formatter(LOG_FORMAT.format(experiment))

    # Kafka logging handler
    handler = KafkaLoggingHandler(topic=topic)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
