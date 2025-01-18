from django.shortcuts import render


def index(request):
    return render(request, "websocket/index.html")


from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from websocket.serializers import GroupSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


from .models import GameState
from .serializers import GameStateSerializer


class GameStateViewSet(viewsets.ModelViewSet):

    queryset = GameState.objects.all()
    serializer_class = GameStateSerializer
