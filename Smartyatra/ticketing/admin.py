from django.contrib import admin
from .models import Stop,Route , RouteStop, Bus, Ticket , Journey
# Register your models here.
admin.site.register([Stop,Route , RouteStop, Bus, Ticket,Journey])