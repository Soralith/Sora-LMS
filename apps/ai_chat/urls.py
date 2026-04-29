from django.urls import path
from . import views

app_name = 'ai_chat'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/', views.chat_api, name='chat_api'),
    path('live-data/', views.live_data_api, name='live_data_api'),
]
