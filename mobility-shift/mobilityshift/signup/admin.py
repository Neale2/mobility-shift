from django.contrib import admin
from .models import User, Trip

#user model
admin.site.register(User)
admin.site.register(Trip)