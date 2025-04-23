from django.urls import path
from . import views

#url pattern handling here
urlpatterns = [
    path('yes/<pk>', views.YesUUIDView.as_view(), name='yes-log'),
    path('no/<pk>', views.NoUUIDView.as_view(), name='no-log'),
]
