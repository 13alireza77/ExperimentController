from time import sleep

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from exapmle.config import mock_data_generator
from registry.model.base import ExperimentModelSingleton
from src.experiment.experiment_manager import ExperimentManager
from src.registry.model.model_loader.scheduler import ModelLoader
from src.registry.model.mongoDB.connector import MongoDBConnector
from src.registry.model.mongoDB.model import MongoDBModelRegistry

reg = MongoDBModelRegistry(MongoDBConnector('localhost', 27017, 'mongoadmin', 'secret'))

# q = reg.get_last_version('model-suggestion1', 'exp-suggestion1')
# print(q)
# m = reg.load('modelx', 'exp1', q)
# print(m)

ml = ModelLoader(reg, 10)
ml.add_scheduler('model-suggestion1', "package-suggestion", 'exp-suggestion1')
ml.add_scheduler('model-suggestion2', "package-suggestion", 'exp-suggestion2')
ml.add_scheduler('model-suggestion1', "package-suggestion")
ml.start_scheduler()

# while True:
#     sleep(2)
#     x = ExperimentModelSingleton.get_instance('exp-suggestion1')
#     x1 = ExperimentModelSingleton.get_instance('exp-suggestion2')
#     x2 = ExperimentModelSingleton.get_instance('package-suggestion')
#     if x:
#         print("x", x.version)
#     if x1:
#         print("x1", x1.version)
#     if x2:
#         print("x2", x2.version)
# exit()

sleep(20)


class GetPackageSuggestionAiModelData:
    users = mock_data_generator.get_users()
    flag_name: str = "package-suggestion"
    flag_layer: str = "phone-number"

    def __init__(self):
        evaluated_users = [ExperimentManager.evaluate(self.flag_name, self.flag_layer, user['phone_number']) for user
                           in
                           self.users.to_dict()]
        print(evaluated_users)

    @classmethod
    def get_suggestion(cls):
        for user in cls.users.to_dict('records'):
            flag_value, experiment_name = ExperimentManager.evaluate(cls.flag_name, cls.flag_layer,
                                                                     user['phone_number'])
            print(user['phone_number'], flag_value, experiment_name)
            test_ai_model = ExperimentManager.get_ai_model(flag_name=cls.flag_name, experiment_name=experiment_name)
            ai_model = ExperimentModelSingleton.get_instance(experiment_name or cls.flag_name)
            print(test_ai_model.model_name, test_ai_model.version)
            print(ai_model.model_name, ai_model.version)
            if experiment_name == "model-suggestion2":
                sample_data = pd.DataFrame(
                    {'gender': [user['gender']], 'age': [user['age']], 'is_student': [user['is_student']]})
                encoder = LabelEncoder()
                sample_data['gender'] = encoder.fit_transform(sample_data['gender'])

            else:
                sample_data = pd.DataFrame(
                    {'gender': [user['gender']], 'age': [user['age']]})
                encoder = LabelEncoder()
                sample_data['gender'] = encoder.fit_transform(sample_data['gender'])

            # Get probabilities for each class
            probabilities = ai_model.model.predict_proba(sample_data)

            # Get the indices of the top 3 predictions (N can be changed as needed)
            top_n_idx = np.argsort(probabilities, axis=1)[:, -3:]
            predicted_packages = ai_model.model.classes_[top_n_idx]
            print(f"suggestions for user: {user['phone_number']} are\n{predicted_packages}")


GetPackageSuggestionAiModelData().get_suggestion()
