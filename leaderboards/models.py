from django.db import models
from django.conf import settings


class Player(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class PlayerStat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    stat_name = models.CharField(max_length=200)
    stat_number = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.player}: {self.stat_name}'


class Ruleset(models.Model):
    ruleset = models.CharField(max_length=200)
    description = models.CharField(max_length=400, null=True)

    def __str__(self):
        return self.ruleset


class PlayerAlias(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    alias = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.player} - {self.alias}'


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    challonge_id = models.CharField(max_length=200, null=True)
    challonge_url = models.URLField(null=True)
    organizers = models.ManyToManyField(settings.AUTH_USER_MODEL)
    date = models.DateField()
    notability = models.CharField(max_length=200)
    ruleset = models.ForeignKey(Ruleset, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=400, null=True)
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(Player)

    def __str__(self):
        return self.name


class RemovedItem(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    item = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.tournament} {self.item}'


class TournamentVod(models.Model):  # Used specifically for tournament VODs
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return f'{self.tournament}: {self.description}'


class TournamentUrl(models.Model):  # Used for other links like spreadsheets, tournament pages etc
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return f'{self.tournament}: {self.description}'


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='wins')
    loser = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='loses')
    score = models.CharField(max_length=200)
    ruleset = models.ForeignKey(Ruleset, null=True, on_delete=models.CASCADE)
    video = models.URLField(null=True)  # If specific match has it's own vod, this is the field to use
    description = models.CharField(max_length=200, null=True)  # Description for forfeits etc

    def __str__(self):
        return f'{self.tournament}: {self.winner} vs {self.loser}'


class TeamMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='wins')
    loser = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='loses')
    score = models.CharField(max_length=200)
    ruleset = models.ForeignKey(Ruleset, null=True, on_delete=models.CASCADE)
    video = models.URLField(null=True)  # If specific match has it's own vod, this is the field to use
    description = models.CharField(max_length=200, null=True)  # Description for forfeits etc

    def __str__(self):
        return f'{self.tournament}: {self.winner} vs {self.loser}'


class RulesetPerRound(models.Model):  # Used to store individual rounds in mixed ruleset
    round_number = models.IntegerField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='wins_round')
    ruleset = models.ForeignKey(Ruleset, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.match}: Round {self.round_number}'


class Leaderboard(models.Model):
    leaderboard_type = models.CharField(max_length=200)
    placement = models.IntegerField(null=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    exposure = models.FloatField(null=True)  # Default sorting value
    mu = models.FloatField(null=True)
    sigma = models.FloatField(null=True)
    tournaments_played = models.IntegerField(default=0)
    matches_played = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.leaderboard_type}: {self.placement}.{self.player}'
