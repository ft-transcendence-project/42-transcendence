from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"^gameplay.ws/ponglogic/(?P<settingid>\d+)/$", consumers.PongLogic.as_asgi()
    ),
]
