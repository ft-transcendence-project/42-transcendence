from django.db import models


# Create your models here.
# status: init,stop,restart
class GameState(models.Model):
    status = models.CharField(max_length=10)
