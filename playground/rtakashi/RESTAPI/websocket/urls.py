from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GameStateViewSet

router = DefaultRouter()
router.register("status", GameStateViewSet)

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/", include(router.urls)),
]
