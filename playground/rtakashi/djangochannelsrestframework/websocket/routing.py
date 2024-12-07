from django.urls import path
from .PongLogic import consumers

websocket_urlpatterns = [
    path("ws/websocket/", consumers.PongLogic.as_asgi()),
    path("ws/api/gamestatus/", consumers.GameStatusConsumer.as_asgi()),
]
