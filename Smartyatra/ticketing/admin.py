from django.contrib import admin
from .models import Stop,Route , RouteStop, Bus, Ticket
# Register your models here.
admin.site.register([Stop,Route , RouteStop, Bus, Ticket])