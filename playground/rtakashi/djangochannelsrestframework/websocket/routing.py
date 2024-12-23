from django.urls import path
from .PongLogic import consumers

websocket_urlpatterns = [
    path("ws/gamelogic/", consumers.PongLogic.as_asgi())
]
