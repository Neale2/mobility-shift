from django.urls import path
from . import views

#url pattern handling here
urlpatterns = [
    path('', views.index, name='index'),
]
