from django.contrib import admin

# Register your models here.

from .models import GameState


class GameStateAdmin(admin.ModelAdmin):
    list_display = ("id", "state")


admin.site.register(GameState, GameStateAdmin)
