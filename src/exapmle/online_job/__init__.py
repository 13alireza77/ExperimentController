from confluent_kafka.admin import AdminClient, NewTopic

from src.experiment.config import REDIS_CLIENT
from src.experiment.experiment_manager import ExperimentManager
from src.experiment.redis_connector import RedisConnector
from src.registry.data.kafka.connector import KafkaRegistry
from src.registry.model.mongoDB.connector import MongoDBConnector
from src.registry.model.mongoDB.model import MongoDBModelRegistry

# Configure your Kafka Broker
admin_client = AdminClient({
    "bootstrap.servers": "localhost:9092"
})

topic_name = "experiment_controller"
num_partitions = 2
replication_factor = 1

topic = NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)

fs = admin_client.create_topics([topic])

redis_connector = RedisConnector.initialise(REDIS_CLIENT)
model_reg = MongoDBModelRegistry(MongoDBConnector('localhost', 27017, 'mongoadmin', 'secret'))
data_reg = KafkaRegistry(topic=topic_name)
ExperimentManager.initialise(model_reg, redis_connector, data_reg)
