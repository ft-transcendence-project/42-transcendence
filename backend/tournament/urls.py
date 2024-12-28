from django.urls import path

from .views import TournamentRegisterView
from .views import SaveDataView

app_name = "tournament"
urlpatterns = [
    path(
        "api/register/",
        TournamentRegisterView.as_view(),
        name="tournament-register",
    ),
    path(
        "api/save-data/",
        SaveDataView.as_view(),
        name="save-data",
    ),
]

