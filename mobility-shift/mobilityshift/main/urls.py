from django.urls import path
from . import views
from django.conf import settings

#url pattern handling here
urlpatterns = [
    path('', views.signup, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signup/confirm/', views.confirm, name='confirm'),
    path('yes/<pk>', views.yes, name='yes-log'),
    path('no/<pk>', views.no, name='no-log'),
    path('nct/<pk>', views.nct, name='nct-log'),
    path('dash/<pk>/', views.dash, name='dash'),
    path('edit/<pk>/', views.edit, name='edit'),
    path('unsubscribe/<pk>', views.unsub, name='unsub'),
    path('unsubscribe/stillsubbed/<pk>', views.stillsubbed, name='stillsubbed'),
    path('unsubscribe/unsubbed/', views.unsubbed, name='unsubbed'),
    path('wh/bounce', views.bounce, name='bounce')
]

if settings.DUMMY_EMAIL_SENDING:
    urlpatterns += [path('dummy_email/<address>/<subject>', views.dummy_email, name='dummy_email')]
