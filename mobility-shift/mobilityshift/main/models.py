import uuid
import datetime
from django.db import models

from django.db.models import UniqueConstraint # Constrains fields to unique values

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Post(models.Model):
    title = models.CharField(max_length=30, help_text='For system use only - will not be displayed to users.')
    content = MarkdownxField(help_text="Use markdown to style post (https://www.markdownguide.org/basic-syntax/). Do not use single hashtag heading (#) as is too large. Drag images in to add, as that will automatically store the image.")
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.title
    
    def formatted_markdown(self):
        return markdownify(self.content)

class Employer(models.Model):
    name = models.CharField(primary_key=True, unique=True)
    emissions_saved = models.PositiveIntegerField(default=0)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Region(models.Model):
    name = models.CharField(primary_key=True, unique=True)
    emissions_saved = models.PositiveIntegerField(default=0)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

class All(models.Model):
    name = models.CharField(primary_key=True, unique=True)
    emissions_saved = models.PositiveIntegerField(default=0)
    def __str__(self):
        """String for representing the Model object."""
        return self.name


class User(models.Model):
    """Model storing users."""
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(max_length=320, unique=True)
    sign_up_time = models.DateTimeField(editable=False, default=(datetime.datetime.now))
    age_group = models.CharField(choices=[("<13", "Less than 13"), ("13-17", "13 - 17"), ("18-24", "18 - 24"), ("25-34", "25 - 34"), ("35-44", "35 - 44"), ("45-64", "45 - 64"), (">65", "More than 65"), ("prefer_not", "Prefer not to say")])
    name = models.CharField(max_length=20)
    distance = models.PositiveIntegerField(choices=[(500, "0.5km"), (1000, "1km"), (2500, "2.5km"), (5000, "5km"), (10000, "10km"), (25000, "25km"), (50000, "50km")])
    vehicle = models.PositiveIntegerField(choices=[(243, "Petrol"), (265, "Diesel"), (192, "Hybrid"), (98, "Plug-in Hybrid"), (19, "Electric"), (243, "Other / Don't know")])
    employer = models.ForeignKey(Employer, on_delete=models.SET_DEFAULT, default='None / Other / Prefer Not To Say')
    region = models.ForeignKey(Region, on_delete=models.SET_DEFAULT, default='Other')
    #1 gram = 1
    emissions_saved = models.PositiveIntegerField(default=0)
    logged_this_week = models.BooleanField(default=False)
    trigger_email = models.BooleanField(default=False)
    # Streak tracking fields
    current_streak = models.PositiveIntegerField(default=0)
    last_logged_week = models.DateField(null=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.email

class Trip(models.Model):
    """Model storing trips."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #left blank if response is no - used as a way to identify trip type
    mode = models.CharField(choices=[("walk", "Walk"), ("bike", "Bike / Scooter"), ("bus", "Bus"), ("ev", "EV"), ('carpool', "Carpool"), ('wfh', 'Work from Home')], null=True, blank=True)
    #NOT when the trip was, but when trip was logged
    log_time = models.DateTimeField(editable=False, default=(datetime.datetime.now))
    text_response = models.TextField(null=True, blank=True)
    quantity = models.PositiveIntegerField()

#when a user unsubscribes, they get moved here.    
class DeletedUser(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    sign_up_time = models.DateTimeField(editable=False)
    age_group = models.CharField(choices=[("<13", "Less than 13"), ("13-17", "13 - 17"), ("18-24", "18 - 24"), ("25-34", "25 - 34"), ("35-44", "35 - 44"), ("45-64", "45 - 64"), (">65", "More than 65"), ("prefer_not", "Prefer not to say")], help_text='Select your age group')
    distance = models.PositiveIntegerField(choices=[(500, "0.5km"), (1000, "1km"), (2500, "2.5km"), (5000, "5km"), (10000, "10km"), (25000, "25km"), (50000, "50km")])
    vehicle = models.PositiveIntegerField(choices=[(243, "Petrol"), (265, "Diesel"), (192, "Hybrid"), (98, "Plug-in Hybrid"), (19, "Electric"), (243, "Other / Don't know")])
    employer = models.ForeignKey(Employer, on_delete=models.SET_DEFAULT, default='None / Other / Prefer Not To Say')
    region = models.ForeignKey(Region, on_delete=models.SET_DEFAULT, default='Other')
    
    emissions_saved = models.PositiveIntegerField()
    
class DeletedTrip(models.Model):
    user = models.ForeignKey(DeletedUser, on_delete=models.CASCADE)
    #left blank if response is no - used as a way to identify trip type
    mode = models.CharField(choices=[("walk", "Walk"), ("bike", "Bike / Scooter"), ("bus", "Bus"), ("ev", "EV"), ('carpool', "Carpool")], null=True, blank=True)
    #NOT when the trip was, but when trip was logged
    log_time = models.DateTimeField(editable=False)
    text_response = models.TextField(null=True, blank=True)
    quantity = models.PositiveIntegerField()
    
class BackedEmail(models.Model):
    recipient = models.EmailField()
    subject = models.TextField()
    html_body = models.TextField()
    uuid = models.TextField()
    priority = models.PositiveIntegerField()


class FriendRequest(models.Model):
    """Model for friend requests between users."""
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_email = models.EmailField(max_length=320)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('from_user', 'to_email')
    
    def __str__(self):
        return f"{self.from_user.name} -> {self.to_email}"


class Friendship(models.Model):
    """Model for established friendships between users."""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    friend_streak = models.PositiveIntegerField(default=0)
    last_both_logged_week = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
    
    def __str__(self):
        return f"{self.user1.name} & {self.user2.name} (streak: {self.friend_streak})"
    
    @classmethod
    def get_friendship(cls, user1, user2):
        """Get friendship between two users regardless of order."""
        try:
            # Try both orders since friendship is bidirectional
            return cls.objects.get(user1=user1, user2=user2)
        except cls.DoesNotExist:
            try:
                return cls.objects.get(user1=user2, user2=user1)
            except cls.DoesNotExist:
                return None
