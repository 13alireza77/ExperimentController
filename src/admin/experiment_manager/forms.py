from django import forms

from src.experiment.experiment_manager import ExperimentManager
from .models import Experiment, Flag, LATEST_MODEL_VERSION


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(FlagForm, self).__init__(*args, **kwargs)
        # Set ai_model choices based on the instance's flag if the instance exists
        if self.instance.id:  # Checks if we're editing an existing instance
            flag_ai_models = ExperimentManager.get_flag_ai_models_specifications(self.instance.name)
            flag = ExperimentManager.get_flag(self.instance.name)
            if flag.ai_model:
                flag_ai_model = ExperimentManager.get_ai_model(flag_name=self.instance.name,
                                                               model_name=flag.ai_model.name,
                                                               model_version=flag.ai_model.version)
            else:
                flag_ai_model = None
            ai_models_in_str = [('', 'model | version')]
            for ai_model in flag_ai_models:
                model_string_format = ai_model.to_string_format()
                if (flag_ai_model and
                        ai_model.name == flag_ai_model.model_name
                        and ai_model.version == flag_ai_model.version):
                    ai_models_in_str.insert(1, (model_string_format, model_string_format + ' ✅'))
                else:
                    ai_models_in_str.append((model_string_format, model_string_format))

            if flag_ai_model is None:
                ai_models_in_str.insert(1, (LATEST_MODEL_VERSION, LATEST_MODEL_VERSION + ' ✅'))
            else:
                ai_models_in_str.append((LATEST_MODEL_VERSION, LATEST_MODEL_VERSION))

            if ai_models_in_str:
                self.fields['ai_model'] = forms.ChoiceField(
                    choices=ai_models_in_str, label='ai_model')


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            flag_ai_models = ExperimentManager.get_flag_ai_models_specifications(self.instance.flag.name)
            experiment = ExperimentManager.get_experiment_by_flag_name(self.instance.flag.name, self.instance.name)
            if experiment.ai_model:
                experiment_ai_model = ExperimentManager.get_ai_model(flag_name=self.instance.flag.name,
                                                                     experiment_name=self.instance.name,
                                                                     model_name=experiment.ai_model.name,
                                                                     model_version=experiment.ai_model.version)
            else:
                experiment_ai_model = None
            ai_models_in_str = [('', 'model | version')]
            for ai_model in flag_ai_models:
                model_string_format = ai_model.to_string_format()
                if (experiment_ai_model and
                        ai_model.name == experiment_ai_model.model_name
                        and ai_model.version == experiment_ai_model.version):
                    ai_models_in_str.insert(1, (model_string_format, model_string_format + ' ✅'))
                else:
                    ai_models_in_str.append((model_string_format, model_string_format))

            if experiment_ai_model is None:
                ai_models_in_str.insert(1, (LATEST_MODEL_VERSION, LATEST_MODEL_VERSION + ' ✅'))
            else:
                ai_models_in_str.append((LATEST_MODEL_VERSION, LATEST_MODEL_VERSION))

            if ai_models_in_str:
                self.fields['ai_model'] = forms.ChoiceField(
                    choices=ai_models_in_str, label='ai_model')
