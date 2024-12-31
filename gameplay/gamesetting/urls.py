from django.urls import path
from .views import GameSettingView

app_name = "gamesetting"

urlpatterns = [
	path('api/', GameSettingView.as_view(), name="game_settings_list"), # GET, POST
	path('api/<int:pk>/', GameSettingView.as_view(), name="game_settings_detail"), # GET, PUT, DELETE
]