from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match_number = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
    player1 = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="matches_as_player1"
    )
    player2 = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="matches_as_player2"
    )
    player1_score = models.PositiveIntegerField(default=0)
    player2_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Match {self.match_number} in {self.tournament.name}"

    @property
    def winner(self):
        return self.player1 if self.player1_score > self.player2_score else self.player2
    
    @winner.setter
    def winner(self, value):
        self._winner = value

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tournament", "match_number"], name="unique_match_number"
            )
        ]
