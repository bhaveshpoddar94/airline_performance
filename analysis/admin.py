from django.contrib import admin
import models
# Register your models here.

admin.site.register(models.Trip)
admin.site.register(models.Airline)
admin.site.register(models.AirlineFlight)
admin.site.register(models.Airport)
admin.site.register(models.Performance)
admin.site.register(models.Delayed)
