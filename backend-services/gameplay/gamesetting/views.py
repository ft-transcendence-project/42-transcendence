import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import GameSetting
from .serializers import GameSettingSerializer


logger = logging.getLogger("gamesetting")

class GameSettingView(APIView):
    def get(self, request, pk=None):
        try:
            if pk:
                logger.info(f"Getting GameSetting with id: {pk}")
                game_setting = GameSetting.objects.get(id=pk)
                serializer = GameSettingSerializer(game_setting)
                return Response(serializer.data)
            else:
                logger.info("Getting all GameSettings")
                game_settings = GameSetting.objects.all()
                serializer = GameSettingSerializer(game_settings, many=True)
                return Response(serializer.data)
        except GameSetting.DoesNotExist:
            logger.error(f"GameSetting with id {pk} not found")
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in GET request: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        logger.info("Creating new GameSetting")
        serializer = GameSettingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("GameSetting created successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Invalid data in POST request: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            logger.info(f"Updating GameSetting with id: {pk}")
            game_setting = GameSetting.objects.get(id=pk)
            serializer = GameSettingSerializer(game_setting, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info("GameSetting updated successfully")
                return Response(serializer.data)
            logger.error(f"Invalid data in PUT request: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except GameSetting.DoesNotExist:
            logger.error(f"GameSetting with id {pk} not found")
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in PUT request: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        try:
            logger.info(f"Deleting GameSetting with id: {pk}")
            game_setting = GameSetting.objects.get(id=pk)
            game_setting.delete()
            logger.info("GameSetting deleted successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except GameSetting.DoesNotExist:
            logger.error(f"GameSetting with id {pk} not found")
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in DELETE request: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
