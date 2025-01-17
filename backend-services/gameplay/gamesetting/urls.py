from django.urls import path
from .views import GameSettingView

app_name = "gamesetting"

urlpatterns = [
    path('', GameSettingView.as_view(), name="game_settings_list"),  # GET, POST
    path('<int:pk>/', GameSettingView.as_view(), name="game_settings_detail"),  # GET, PUT, DELETE
]