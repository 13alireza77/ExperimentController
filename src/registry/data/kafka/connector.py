import json
from typing import Optional

from kafka import KafkaProducer, KafkaConsumer, TopicPartition

from src.registry.data.base import DataRegisteryInterface


class KafkaRegistry(DataRegisteryInterface):
    _topic: str = "experiment_controller"

    def __init__(self, topic=None, **configs):
        if topic is not None:
            self._topic = topic
        self.bootstrap_servers = configs.get("bootstrap_servers", "localhost:9092")
        self.producer = KafkaProducer(
            **configs,
        )

    def publish(self, data, data_name: str, experiment: str, version: Optional[int] = None, **kwargs):
        self.producer.send(topic=self._topic, value=data.encode('utf-8'), partition=kwargs.pop('partition', None))
        self.producer.flush()

    def load(self, data_name: str, experiment: str, version: Optional[int] = None, **kwargs):

        consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=1000,
            enable_auto_commit=True
        )

        topic_partition = TopicPartition(self._topic, kwargs.pop('partition', None))

        consumer.assign([topic_partition])

        all_data = []
        try:
            for message in consumer:
                all_data.append(message.value)
        finally:
            consumer.close()

        return all_data
