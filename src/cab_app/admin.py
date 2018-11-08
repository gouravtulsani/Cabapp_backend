from django.contrib import admin

# Register your models here.
from .models import Register, RideHistory

admin.site.register(Register)
admin.site.register(RideHistory)
