from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    otp_enabled = models.BooleanField(default=False)
    default_language = models.CharField(
        max_length=10,  # 言語コード（例: "en", "ja"）を想定
        default="en",  # デフォルトの言語を英語に設定
        help_text="The user's preferred default language.",
    )

    def __str__(self):
        return self.username
