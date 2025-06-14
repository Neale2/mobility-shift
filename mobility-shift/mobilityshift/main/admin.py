from django.contrib import admin
from .models import User, Trip, DeletedUser, DeletedTrip, Employer, Region, All, Post

from markdownx.admin import MarkdownxModelAdmin
#user model
admin.site.register(User)
admin.site.register(DeletedUser)
admin.site.register(Trip)
admin.site.register(DeletedTrip)
admin.site.register(Employer)
admin.site.register(Region)
admin.site.register(All)
admin.site.register(Post, MarkdownxModelAdmin)