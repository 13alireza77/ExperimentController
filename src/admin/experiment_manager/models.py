from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.db.utils import IntegrityError

from experiment.base import Experiment as RedisExperiment
# from experiment.base import ExperimentFlag as RedisExperimentFlag
# from experiment.base import ExperimentFlagType as RedisExperimentFlagType
from experiment.experiment_manager import ExperimentManager


class ExperimentFlagType(models.IntegerChoices):
    INTEGER = 1, 'Integer'
    BOOLEAN = 2, 'Boolean'
    STRING = 3, 'String'


class Flag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.IntegerField(choices=ExperimentFlagType.choices)
    base_value = models.CharField(max_length=255)

    def clean(self):
        super().clean()

        if self.type == ExperimentFlagType.INTEGER and (not self.base_value.isdigit() or int(self.base_value) < 0):
            raise ValidationError("For INTEGER type flags, base_value must be a positive integer.")
        if self.type == ExperimentFlagType.BOOLEAN and self.base_value not in ["True", "False"]:
            raise ValidationError("For BOOLEAN type flags, base_value must be either 'True' or 'False'.")

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)  # Save to the Django DB
    #     try:
    #         # Create Redis object representation
    #         redis_object = RedisExperimentFlag(
    #             name=self.name.__str__(),
    #             type=RedisExperimentFlagType(ExperimentFlagType(self.type).name),
    #             base_value=self.base_value
    #         )
    #         # Save to Redis via ExperimentManager
    #         ExperimentManager.save_flag(redis_object)
    #     except Exception as ex:  # General exception catching to simplify rollback demonstration
    #         self.delete()  # Rollback if Redis save fails
    #         raise ex

    def __str__(self):
        return self.name


class Layer(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Experiment(models.Model):
    name = models.CharField(max_length=255)
    flag = models.ForeignKey(Flag, on_delete=models.CASCADE, related_name='experiments')
    flag_value = models.CharField(max_length=255)
    share = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE, related_name='experiments')

    def clean(self):
        super().clean()
        if not 0 <= self.share <= 1:
            raise ValidationError("Share value must be a float between 0 and 1, inclusive.")

        # Check other Experiments' share sum does not exceed 1
        existing_share_sum = Experiment.objects.filter(
            flag=self.flag
        ).exclude(id=self.id).aggregate(Sum('share'))['share__sum'] or 0

        if existing_share_sum + self.share > 1:
            raise ValidationError(
                "Adding this share would exceed the total allowable share of 1 for the related ExperimentFlag.")

        if self.flag.type == ExperimentFlagType.INTEGER and (not self.flag_value.isdigit() or int(self.flag_value) < 0):
            raise ValidationError("For INTEGER type flags, flag_value must be a positive integer.")
        if self.flag.type == ExperimentFlagType.BOOLEAN and self.flag_value not in ["True", "False"]:
            raise ValidationError("For BOOLEAN type flags, flag_value must be either 'True' or 'False'.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)  # Save to the Django DB
        try:
            # Create Redis object representation
            redis_object = RedisExperiment(
                name=self.name,
                flag_name=self.flag.name,
                flag_value=self.flag_value,
                layer=self.layer,
                share=self.share
            )
            # Save to Redis via ExperimentManager
            ExperimentManager.save_experiment(redis_object)
        except Exception as ex:
            self.delete()  # Rollback if Redis save fails
            raise IntegrityError(f"Failed to save to Redis: {ex}")

    def __str__(self):
        return self.name
