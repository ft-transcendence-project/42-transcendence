from django.urls import path

from .views import SaveDataView, TournamentRegisterView, GetMatchView

app_name = "tournament"
urlpatterns = [
    path(
        "api/register/",
        TournamentRegisterView.as_view(),
        name="tournament-register",
    ),
    path(
        "api/save-data/<int:pk>/",
        SaveDataView.as_view(),
        name="save-data",
    ),
    path(
        "api/get-match/<int:tournament_id>/<int:match_number>/",
        GetMatchView.as_view(),
        name="get-match",
    ),
]
