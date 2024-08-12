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
        category_choices = [('', 'experiment | model | version')]
        if self.instance.id:  # Checks if we're editing an existing instance
            flag = self.instance.flag
            experiments = flag.experiments.all()
            experiment_names = [experiment.name for experiment in experiments]
            ai_models = ExperimentManager.get_experiments_ai_models(experiment_names)
            ai_models = [model.to_string_format() for model in ai_models]
            if ai_models:
                category_choices.extend([(v, v) for v in ai_models])
                self.fields['ai_model'] = forms.ChoiceField(
                    choices=category_choices, label='ai_model')
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
