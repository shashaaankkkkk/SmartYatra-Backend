from django.contrib import admin
from .models import BusLocation , LocationHistory
admin.site.register([BusLocation,LocationHistory])