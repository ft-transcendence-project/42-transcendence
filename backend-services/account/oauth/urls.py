from django.urls import path

from . import views

app_name = "oauth"
urlpatterns = [
    path("", views.oauth_view, name="oauth"),
    path("callback/", views.oauth_callback_view, name="callback"),
]
