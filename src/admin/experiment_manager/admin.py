from django.contrib import admin

from .forms import ExperimentForm, FlagForm
from .models import Flag, Experiment, Layer


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'base_value')
    search_fields = ('name',)
    list_filter = ('type',)
    form = FlagForm


@admin.register(Layer)
class LayerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'flag', 'flag_value', 'share', 'layer')
    list_filter = ('flag__type',)
    search_fields = ('name', 'flag__name', 'layer')
    fieldsets = (
        (None, {
            'fields': ('name', 'flag', 'layer')
        }),
        ('Details', {
            'fields': ('flag_value', 'share', 'ai_model')
        }),
    )
    form = ExperimentForm

    def get_queryset(self, request):
        # Optimize queries with select_related
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('flag')
        return queryset

    # def save_model(self, request, obj, form, change):
    #     obj.save()
    #     if not change:  # Additional actions for new objects
    #         # Custom action for new objects can be included here
    #         pass
    #
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "flag":
    #         # Custom querysets or conditions for foreignkey fields can be handled here
    #         pass
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)
