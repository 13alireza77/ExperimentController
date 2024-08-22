import json

from src.exapmle.config import mock_data_generator
from src.experiment.experiment_manager import ExperimentManager
from kafka import KafkaAdminClient
from kafka.admin.new_partitions import NewPartitions


class PublishPackageSuggestionAiModelData:
    sales = mock_data_generator.get_sales()
    flag_name: str = "package-suggestion"

    @classmethod
    def publish_exp_suggestion1_data(cls):
        experiment_name = "exp-suggestion1"
        model_name = "model-suggestion1"
        for sale in cls.sales.to_dict('records'):
            print("publish_exp_suggestion1_data")
            ExperimentManager.publish_ai_model_data(data=json.dumps(sale), data_name=model_name,
                                                    flag_name=cls.flag_name,
                                                    experiment_name=experiment_name,
                                                    partition=0)

    @classmethod
    def publish_exp_suggestion2_data(cls):
        experiment_name = "exp-suggestion2"
        model_name = "model-suggestion2"

        for sale in cls.sales.to_dict('records'):
            print("publish_exp_suggestion2_data")
            ExperimentManager.publish_ai_model_data(data=json.dumps(sale), data_name=model_name,
                                                    flag_name=cls.flag_name,
                                                    experiment_name=experiment_name,
                                                    partition=1)


PublishPackageSuggestionAiModelData.publish_exp_suggestion1_data()
PublishPackageSuggestionAiModelData.publish_exp_suggestion2_data()
