import uuid
import datetime
from django.db import models

from django.db.models import UniqueConstraint # Constrains fields to unique values

class User(models.Model):
    """Model storing users."""
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(max_length=320, help_text='Enter your email', unique=True)
    sign_up_time = models.DateTimeField(editable=False, default=(datetime.datetime.now))
    age_group = models.CharField(choices=[("<13", "Less than 13"), ("13-17", "13 - 17"), ("18-24", "18 - 24"), ("25-34", "25 - 34"), ("35-44", "35 - 44"), ("45-64", "45 - 64"), (">65", "More than 65"), ("prefer_not", "Prefer not to say")], help_text='Select your age group')
    gender = models.CharField(choices=[("male", "Male"), ("female", "Female"), ("other", "Other"), ("prefer_not", "Prefer not to say")], help_text='Select your gender')

    def __str__(self):
        """String for representing the Model object."""
        return self.email

class Trip(models.Model):
    """Model storing trips."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mode = models.CharField(choices=[("walk", "Walking"), ("bike", "Cycling"), ("bus", "Bussing")])
    #NOT when the trip was, but when trip was logged
    log_time = models.DateTimeField(editable=False, default=(datetime.datetime.now))
    #stored in METERS
    distance = models.PositiveIntegerField(choices=[(500, "0.5km"), (1000, "1km"), (2500, "2.5km"), (5000, "5km"), (10000, "10km"), (25000, "25km"), (50000, "50km")])