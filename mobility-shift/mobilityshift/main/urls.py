from django.urls import path
from . import views

#url pattern handling here
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/confirm/', views.confirm, name='confirm'),
    path('yes/<pk>', views.yes, name='yes-log'),
    path('no/<pk>', views.no, name='no-log'),
    path('yes/thanks/', views.thanks, name='thanks'),
    path('no/thanks/', views.thanks, name='thanks'),
    path('unsubscribe/<pk>', views.unsub, name='unsub'),
    path('unsubscribe/stillsubbed/', views.stillsubbed, name='stillsubbed'),
    path('unsubscribe/unsubbed/', views.unsubbed, name='unsubbed')
]
