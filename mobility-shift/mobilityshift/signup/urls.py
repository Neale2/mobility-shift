from django.urls import path
from . import views

#url pattern handling here
urlpatterns = [
    path('', views.index, name='index'),
    path('confirm/', views.confirm, name='confirm'),
]
