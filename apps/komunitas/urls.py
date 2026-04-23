from django.urls import path
from . import views

app_name = 'komunitas'

urlpatterns = [
    path('', views.index, name='index'),
    path('messages/', views.message_list, name='message_list'),
    path('post/', views.post_message, name='post_message'),
]