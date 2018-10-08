from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=200)
    unseeded_tournaments_played = models.IntegerField(default=0)
    unseeded_matches_played = models.IntegerField(default=0)
    seeded_tournaments_played = models.IntegerField(default=0)
    seeded_matches_played = models.IntegerField(default=0)
    other_tournaments_played = models.IntegerField(default=0)
    other_matches_played = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class PlayerAlias(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    alias = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.player} - {self.alias}'


class TournamentOrganizer(models.Model):
    name = models.CharField(max_length=200)
    tournaments_organized = models.IntegerField()

    def __str__(self):
        return self.name


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    challonge_id = models.CharField(max_length=200)
    challonge_url = models.URLField()
    organizers = models.ManyToManyField(TournamentOrganizer)
    date = models.DateField()
    notability = models.CharField(max_length=200)
    ruleset = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
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
    ruleset = models.CharField(max_length=200, null=True)
    video = models.URLField(null=True)  # If specific match has it's own vod, this is the field to use
    description = models.CharField(max_length=200, null=True)  # Description for forfeits etc

    def __str__(self):
        return f'{self.tournament}: {self.winner} vs {self.loser}'


class TeamMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='wins')
    loser = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='loses')
    score = models.CharField(max_length=200)
    ruleset = models.CharField(max_length=200, null=True)
    video = models.URLField(null=True)  # If specific match has it's own vod, this is the field to use
    description = models.CharField(max_length=200, null=True)  # Description for forfeits etc

    def __str__(self):
        return f'{self.tournament}: {self.winner} vs {self.loser}'


class RulesetPerRound(models.Model):  # Used to store individual rounds in mixed ruleset
    round_number = models.IntegerField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='wins_round')
    ruleset = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.match}: Round {self.round_number}'


class Leaderboard(models.Model):
    leaderboard_type = models.CharField(max_length=200)
    placement = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    exposure = models.FloatField()  # Default sorting value
    mu = models.FloatField()
    sigma = models.FloatField()
    tournaments_played = models.IntegerField(default=0)  # Different from data in Players model, these fields only track
    matches_played = models.IntegerField(default=0)      # tourneys and matches that count towards specific leaderboard

    def __str__(self):
        return f'{self.leaderboard_type}: {self.placement}.{self.player}'
