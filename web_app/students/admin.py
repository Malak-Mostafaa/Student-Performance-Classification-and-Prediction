from django.contrib import admin
from .models import PredictionRecord
# register prediction model in Django admin panel
admin.site.register(PredictionRecord)
