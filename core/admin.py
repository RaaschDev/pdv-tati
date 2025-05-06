from django.contrib import admin
from .models import FinishedOrder, FinishedOrderItem

# Register your models here.
admin.site.register(FinishedOrder)
admin.site.register(FinishedOrderItem)
