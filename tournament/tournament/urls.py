from django.urls import path

from .views import SaveDataView, TournamentRegisterView

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
]
