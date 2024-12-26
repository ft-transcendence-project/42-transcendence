# SPAの場合はいらないかも

from django.shortcuts import render


def index(request):
    return render(request, "websocket/index.html")


# from rest_framework import permissions, viewsets

# from .models import GameState
# from .serializers import GameStateSerializer


# class GameStateViewSet(viewsets.ModelViewSet):

#     queryset = GameState.objects.all()
#     serializer_class = GameStateSerializer
