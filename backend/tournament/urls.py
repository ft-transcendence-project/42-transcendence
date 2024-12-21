from django.urls import path

from .views import TournamentRegisterView
from .views import SaveScoreView

app_name = "tournament"
urlpatterns = [
    path(
        "api/register/",
        TournamentRegisterView.as_view(),
        name="tournament-register",
    ),
    path(
        "api/save-score/",
        SaveScoreView.as_view(),
        name="save-score",
    ),
]

