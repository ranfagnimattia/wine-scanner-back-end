from django.contrib import admin

from .models import Sensor, PredictionMethod, PredictionParams


class PredictionMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'reset', 'defaultParams')
    list_editable = ('reset',)


class PredictionParamsAdmin(admin.ModelAdmin):
    list_display = ('method', 'sensor', 'params')


admin.site.register(Sensor)
admin.site.register(PredictionMethod, PredictionMethodAdmin)
admin.site.register(PredictionParams, PredictionParamsAdmin)
