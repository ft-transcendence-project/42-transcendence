from django.apps import AppConfig


class WebsocketConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "websocket"

    def ready(self):
        # アプリケーションが完全に初期化された後に必要なインポートを行う
        from .PongLogic import consumers  # 必要な場合にだけインポート
