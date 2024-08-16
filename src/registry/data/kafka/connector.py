import json
from typing import Optional

from kafka import KafkaProducer, KafkaConsumer

from registry.data.base import DataConnectorInterface


class KafkaDataConnector(DataConnectorInterface):
    _topic: str = "experiment_controller"

    def __init__(self, **configs):
        self.bootstrap_servers = configs.get("bootstrap_servers", "localhost")
        self.producer = KafkaProducer(
            **configs,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

    def publish(self, data, data_name: str, experiment: str, version: Optional[int]):
        key = f"{data_name}_{experiment}_{version}"
        self.producer.send(topic=self._topic, key=key, value=data)
        self.producer.flush()

    def load(self, data_name: str, experiment: str, version: Optional[int]):
        consumer = KafkaConsumer(
            self._topic,
            key=f"{data_name}_{experiment}_{version}",
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('ascii'))
        )
        return consumer
