from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameSettingView
from . import views

app_name = "gameplay"

urlpatterns = [
	path("", views.playpage, name="gameplay"),
    path('api/gamesetting/', GameSettingView.as_view(), name='game_settings_list'), # GET, POST
	path('api/gamesetting/<int:pk>/', GameSettingView.as_view(), name='game_settings_detail'), # GET, PUT, DELETE
]