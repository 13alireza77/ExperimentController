from django.contrib import admin

from .models import Flag, Experiment


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'base_value')
    search_fields = ('name',)
    list_filter = ('type',)


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'flag', 'flag_value', 'share', 'layer')
    list_filter = ('flag__type',)
    search_fields = ('name', 'flag__name', 'layer')
    fieldsets = (
        (None, {
            'fields': ('name', 'flag')
        }),
        ('Details', {
            'fields': ('flag_value', 'share')
        }),
    )

    def get_queryset(self, request):
        # Optimize queries with select_related
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('flag')
        return queryset

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:  # Additional actions for new objects
            # Custom action for new objects can be included here
            pass

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "flag":
            # Custom querysets or conditions for foreignkey fields can be handled here
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
