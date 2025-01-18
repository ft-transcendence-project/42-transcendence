from django.db import models


# Create your models here.
class GameSetting(models.Model):
    BALL_VELOCITY_CHOICES = [
        ("fast", "Fast"),
        ("normal", "Normal"),
        ("slow", "Slow"),
    ]
    ball_velocity = models.CharField(
        max_length=10,
        choices=BALL_VELOCITY_CHOICES,
        default="normal",
    )

    BALL_SIZE_CHOICES = [
        ("big", "Big"),
        ("normal", "Normal"),
        ("small", "Small"),
    ]
    ball_size = models.CharField(
        max_length=10,
        choices=BALL_SIZE_CHOICES,
        default="normal",
    )

    MAP_CHOICES = [
        ("a", "A"),
        ("b", "B"),
        ("c", "C"),
    ]
    map = models.CharField(
        max_length=10,
        choices=MAP_CHOICES,
        default="a",
    )
