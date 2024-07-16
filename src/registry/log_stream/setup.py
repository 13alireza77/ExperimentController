import logging

from experiment.config import LOG_FORMAT
from registry.log_stream.handler import KafkaLoggingHandler


def setup_logger(name, topic, level=logging.INFO, label=None):
    """Setup a logger that streams to Kafka with a specific label."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Format including the experiment label if provided
    formatter = logging.Formatter(LOG_FORMAT.format(label))

    # Kafka logging handler
    handler = KafkaLoggingHandler(topic=topic)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
