from django.urls import include, path

from . import views

# from .views import GameStateViewSet


urlpatterns = [path("", views.index, name="index")]
