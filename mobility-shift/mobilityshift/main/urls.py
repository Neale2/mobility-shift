from django.urls import path
from . import views

#url pattern handling here
urlpatterns = [
    path('', views.signup, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signup/confirm/', views.confirm, name='confirm'),
    path('yes/<pk>', views.yes, name='yes-log'),
    path('no/<pk>', views.no, name='no-log'),
    path('dash/<pk>/', views.dash, name='dash'),
    path('edit/<pk>/', views.edit, name='edit'),
    path('unsubscribe/<pk>', views.unsub, name='unsub'),
    path('unsubscribe/stillsubbed/<pk>', views.stillsubbed, name='stillsubbed'),
    path('unsubscribe/unsubbed/', views.unsubbed, name='unsubbed'),
    path('wh/bounce', views.bounce, name='bounce'),
    # Friend functionality
    path('friends/send/<pk>', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>', views.accept_friend_request, name='accept_friend_request'),
    path('friends/decline/<int:request_id>', views.decline_friend_request, name='decline_friend_request'),
]
