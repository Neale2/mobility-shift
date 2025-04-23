from django.contrib import admin
from .models import User, Trip, DeletedUser, DeletedTrip

#user model
admin.site.register(User)
admin.site.register(DeletedUser)
admin.site.register(Trip)
admin.site.register(DeletedTrip)