from django.contrib import admin

from .models import User , CustomUserManager
admin.site.register([User])

