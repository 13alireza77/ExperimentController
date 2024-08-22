from abc import abstractmethod

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from src.exapmle.config import mock_data_generator
from src.experiment.experiment_manager import ExperimentManager


class ModelFlagPackageSuggestion:
    flag_name: str = "package-suggestion"
    experiments = ExperimentManager.get_experiments_by_flag_name(flag_name)

    @classmethod
    def _get_data(cls, model_name: str, experiment_name: str, partition: int) -> pd.DataFrame:
        data = ExperimentManager.load_ai_model_data(data_name=model_name,
                                                    flag_name=cls.flag_name,
                                                    experiment_name=experiment_name, partition=partition)
        print(len(data))
        return pd.DataFrame(data)

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def train(self):
        pass


class ModelFlagPackageSuggestion1(ModelFlagPackageSuggestion):
    experiment_name = "exp-suggestion1"
    model_name = "model-suggestion1"

    def __init__(self):
        self.experiment = ExperimentManager.get_experiment_by_flag_name(ModelFlagPackageSuggestion1.flag_name,
                                                                        self.experiment_name)

    def validate(self):
        return self.experiment_name in [e.name for e in super().experiments]

    def train(self):
        if not self.validate():
            return

        sales = self._get_data(self.model_name, self.experiment.name, partition=0)
        users = mock_data_generator.get_users()
        packages = mock_data_generator.get_packages()
        # Combining datasets
        data_combined = pd.merge(sales, users, on='phone_number')
        data_combined = pd.merge(data_combined, packages, left_on='package_id', right_index=True)

        # Encoding categorical data
        encoder = LabelEncoder()
        data_combined['gender'] = encoder.fit_transform(data_combined['gender'])
        data_combined['type'] = encoder.fit_transform(data_combined['type'])

        # Data for model
        X = data_combined[['gender', 'age']]
        y = data_combined['package_id']

        model = RandomForestClassifier(random_state=42)
        model.fit(X, y)

        ExperimentManager.register_ai_model(model=model,
                                            experiment_name=self.experiment.name,
                                            flag_name=self.experiment.flag_name,
                                            model_name=self.model_name)


class ModelFlagPackageSuggestion2(ModelFlagPackageSuggestion):
    experiment_name = "exp-suggestion2"
    model_name = "model-suggestion2"

    def __init__(self):
        self.experiment = ExperimentManager.get_experiment_by_flag_name(ModelFlagPackageSuggestion1.flag_name,
                                                                        self.experiment_name)

    def validate(self):
        return self.experiment_name in [e.name for e in super().experiments]

    def train(self):
        if not self.validate():
            return

        sales = self._get_data(self.model_name, self.experiment.name, partition=1)
        users = mock_data_generator.get_users()
        packages = mock_data_generator.get_packages()
        # Combining datasets
        data_combined = pd.merge(sales, users, on='phone_number')
        data_combined = pd.merge(data_combined, packages, left_on='package_id', right_index=True)

        # Encoding categorical data
        encoder = LabelEncoder()
        data_combined['gender'] = encoder.fit_transform(data_combined['gender'])
        data_combined['type'] = encoder.fit_transform(data_combined['type'])

        # Data for model
        X = data_combined[['gender', 'age', 'is_student']]
        y = data_combined['package_id']

        model = RandomForestClassifier(random_state=42)
        model.fit(X, y)

        ExperimentManager.register_ai_model(model=model,
                                            experiment_name=self.experiment.name,
                                            flag_name=self.experiment.flag_name,
                                            model_name=self.model_name)


# ModelFlagPackageSuggestion1().train()
ModelFlagPackageSuggestion2().train()
