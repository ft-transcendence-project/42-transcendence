from django.urls import path, include

# from .views import GameStateViewSet

from . import views

urlpatterns = [path("", views.index, name="index")]
