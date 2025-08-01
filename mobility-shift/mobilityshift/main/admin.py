from django.contrib import admin
from django.contrib import messages
from markdownx.admin import MarkdownxModelAdmin

from .models import User, Trip, DeletedUser, DeletedTrip, Employer, Region, All, Post
from .tasks import email_user


class CustomUser(admin.ModelAdmin):
    """
    User Model Admin with custom actions."""

    def save_model(self, request, obj, form, change):
        if obj.trigger_email:
            messages.success(request, f"Email triggered for user: {obj.email}")
            email_user(obj)
            obj.trigger_email = False
        super().save_model(request, obj, form, change)


admin.site.register(User, CustomUser)
admin.site.register(DeletedUser)
admin.site.register(Trip)
admin.site.register(DeletedTrip)
admin.site.register(Employer)
admin.site.register(Region)
admin.site.register(All)
admin.site.register(Post, MarkdownxModelAdmin)
