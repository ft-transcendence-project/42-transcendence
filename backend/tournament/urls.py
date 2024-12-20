from django.urls import path

from .views import TournamentRegisterView

app_name = "tournament"
urlpatterns = [
    path(
        "api/register/",
        TournamentRegisterView.as_view(),
        name="tournament-register",
    ),
]
