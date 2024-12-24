from django.db import models

# Create your models here.


class GameState(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=20, null=False, default="waiting")
    r_player = models.FloatField(default=240)
    l_player = models.FloatField(default=240)
    ball_x = models.FloatField(default=500)
    ball_y = models.FloatField(default=300)
    r_score = models.PositiveIntegerField(default=0)
    l_score = models.PositiveIntegerField(default=0)
