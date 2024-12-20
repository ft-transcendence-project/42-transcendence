from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import GameSetting
from .serializers import GameSettingSerializer

class GameplayView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "gameplay/playpage.html")


playpage = GameplayView.as_view()

# リクエストに対するレスポンスを定義
class GameSettingView(APIView):

    # GETリクエストの処理
    def get(self, request, pk=None):
        if pk:
            # IDで特定のGameSettingを取得
            game_setting = GameSetting.objects.get(id=pk)
            serializer = GameSettingSerializer(game_setting)
            return Response(serializer.data)
        else:
            # すべてのGameSettingを取得
            game_settings = GameSetting.objects.all()
            serializer = GameSettingSerializer(game_settings, many=True)
            return Response(serializer.data)

    # POSTリクエストの処理
    def post(self, request):
        serializer = GameSettingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 新しいデータを保存
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUTリクエストの処理
    def put(self, request, pk=None):
        game_setting = GameSetting.objects.get(id=pk)
        serializer = GameSettingSerializer(game_setting, data=request.data)
        if serializer.is_valid():
            serializer.save()  # 既存のデータを更新
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETEリクエストの処理
    def delete(self, request, pk=None):
        game_setting = GameSetting.objects.get(id=pk)
        game_setting.delete()  # 指定されたGameSettingを削除
        return Response(status=status.HTTP_204_NO_CONTENT)