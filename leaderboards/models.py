from django.db import models
from django.conf import settings
from leaderboards.trueskill_scripts.trueskill_calculation import TrueskillCalculations


class Player(models.Model):
    name = models.CharField(max_length=200, unique=True)
    last_played = models.DateField(null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Stat(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self):
        return self.name


class PlayerStat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    stat = models.ForeignKey(Stat, null=True, blank=True, on_delete=models.CASCADE)
    value = models.FloatField(default=0)

    def __str__(self):
        return f'{self.player}: {self.stat_name}'


class Ruleset(models.Model):
    ruleset = models.CharField(max_length=200)
    description = models.CharField(max_length=400, null=True, blank=True)

    class Meta:
        ordering = ['ruleset']

    def __str__(self):
        return self.ruleset


class AllowedScore(models.Model):
    score = models.CharField(max_length=5)

    class Meta:
        ordering = ['score']

    def __str__(self):
        return self.score


class PlayerAlias(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    alias = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.player} - {self.alias}'


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    challonge_id = models.CharField(max_length=200, null=True, blank=True)
    challonge_url = models.URLField(null=True, blank=True)
    organizers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    date = models.DateField()
    notability = models.CharField(max_length=200, default='minor')
    ruleset = models.ForeignKey(Ruleset, null=True, blank=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=400, null=True, blank=True)
    winner = models.ForeignKey(Player, null=True, blank=True, on_delete=models.CASCADE, related_name='tournament_wins')
    winner_team = models.ForeignKey('Team', null=True, blank=True, on_delete=models.CASCADE,
                                    related_name='tournament_wins')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, create_leaderboards=False):
        super().save()
        if create_leaderboards:
            TrueskillCalculations(tournament_model=self.__class__, leaderboard_model=Leaderboard,
                                  player_model=Player).create_leaderboards()


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


class TournamentUrl(models.Model):  # Used for other links like spreadsheets, tournament pages etc
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return f'{self.tournament}: {self.description}'


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE, related_name='match_wins')
    loser = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE, related_name='match_loses')
    winner_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE, related_name='match_wins')
    loser_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE, related_name='match_loses')
    score = models.ForeignKey(AllowedScore, blank=True, null=True, on_delete=models.CASCADE)
    ruleset = models.ForeignKey(Ruleset, null=True, blank=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True, blank=True)  # Description for forfeits etc

    def __str__(self):
        return f'{self.tournament}: {self.winner} vs {self.loser}'


class RulesetPerRound(models.Model):  # Used to store individual rounds in mixed ruleset
    round_number = models.IntegerField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE, related_name='round_wins')
    winner_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE, related_name='round_wins')
    ruleset = models.ForeignKey(Ruleset, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.match}: Round {self.round_number}'


class Vod(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, blank=True, null=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return f'{self.tournament}: {self.description}'


class Leaderboard(models.Model):
    leaderboard_type = models.CharField(max_length=200)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    exposure = models.FloatField(null=True)  # Default sorting value
    mu = models.FloatField(null=True)
    sigma = models.FloatField(null=True)
    tournaments_played = models.IntegerField(default=0)
    matches_played = models.IntegerField(default=0)

    class Meta:
        ordering = ['-exposure']

    def __str__(self):
        return f'{self.leaderboard_type}: {self.exposure}.{self.player}'
