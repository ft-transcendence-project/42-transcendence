from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameSettingView
from . import views

app_name = "gamesetting"

urlpatterns = [
	path('api/', GameSettingView.as_view(), name='game_settings_list'), # GET, POST
	path('api/<int:pk>/', GameSettingView.as_view(), name='game_settings_detail'), # GET, PUT, DELETE
]