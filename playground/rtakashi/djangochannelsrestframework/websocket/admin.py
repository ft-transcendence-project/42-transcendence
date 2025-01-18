from django.contrib import admin

from .models import GameState

# Register your models here.



class GameStateAdmin(admin.ModelAdmin):
    list_display = ("id", "state")


admin.site.register(GameState, GameStateAdmin)
