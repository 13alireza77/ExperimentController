import json
import logging

from kafka import KafkaProducer


class KafkaLoggingHandler(logging.Handler):
    def __init__(self, topic, **configs):
        super().__init__()
        self.producer = KafkaProducer(**configs,
                                      value_serializer=lambda m: json.dumps(m).encode('ascii'))
        self.topic = topic

    def emit(self, record):
        # Create a message with the record information
        message = self.format(record)
        # Send the message to Kafka
        self.producer.send(self.topic, message)
        self.producer.flush()
