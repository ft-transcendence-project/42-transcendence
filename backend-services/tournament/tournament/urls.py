from django.urls import path

from .views import SaveDataView, TournamentRegisterView, GetTournamentByGameIdView

app_name = "tournament"
urlpatterns = [
    path(
        "register/",
        TournamentRegisterView.as_view(),
        name="tournament-register",
    ),
    path(
        "register/<int:pk>/",
        TournamentRegisterView.as_view(),
        name="tournament-register",
    ),
    path(
        "save-data/<int:pk>/",
        SaveDataView.as_view(),
        name="save-data",
    ),
    path(
        "get-game-id/<int:game_id>/",
        GetTournamentByGameIdView.as_view(),
        name="get-game-id",
    )
]