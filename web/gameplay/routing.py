from django.urls import path

from .PongLogic import consumers

websocket_urlpatterns = [
    path("ws/gameplay/", consumers.PongLogic.as_asgi()),
]
