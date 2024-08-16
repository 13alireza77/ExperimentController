from django import forms

from src.experiment.base import AiModel
from src.experiment.experiment_manager import ExperimentManager
from .models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)
        # Set ai_model choices based on the instance's flag if the instance exists
        if self.instance.id:  # Checks if we're editing an existing instance
            flag_ai_models = ExperimentManager.get_flag_ai_models(self.instance.flag.name)
            experiment_ai_model = ExperimentManager.get_experiment_ai_model(self.instance.name)
            ai_models_in_str = [('', 'model | version')]
            for ai_model in flag_ai_models:
                model_string_format = ai_model.to_string_format()
                if (experiment_ai_model and
                        ai_model.name == experiment_ai_model.model_name
                        and ai_model.version == experiment_ai_model.version):
                    ai_models_in_str = [(model_string_format, model_string_format)]
                    break
                else:
                    ai_models_in_str.append((model_string_format, model_string_format))
            if ai_models_in_str:
                self.fields['ai_model'] = forms.ChoiceField(
                    choices=ai_models_in_str, label='ai_model')
        # else:
        #     category_choices.extend([])
        #     self.fields['ai_model'] = forms.ChoiceField(
        #         choices=category_choices, label='ai_model')

    # def save(self, commit=True):
    # if not self.errors:
    #     flag = getattr(self.instance, 'flag', None)
    #     if flag:
    #         flag_name = flag.name
    #     else:
    #         flag_name = self.cleaned_data.get('flag').name
    #     print("experiments******")
    #     experiments = ExperimentManager.load_experiments_by_flag_name(flag_name)
    #     print(experiments)
    #     if experiments and self.instance.ai_model:
    #         for experiment in experiments:
    #             ai_model = AiModel.from_string_format(self.instance.ai_model)
    #             if experiment.name == ai_model.experiment_name:
    #                 experiment.ai_model = AiModel.from_string_format(experiment.ai_model)
    #                 ExperimentManager.save_experiment(experiment)
    #                 break

    # return super(ExperimentForm, self).save(commit=commit)
