from collections import defaultdict

import trueskill


class TrueskillCalculations:

    def __init__(self, tournament_limit=2, seeded_multiplier=4, mixed_multiplier=2, tournament_model=object,
                 leaderboard_model=object, player_model=object):
        """
        :param player_model: Model containing players
        :param leaderboard_model: Model in which leaderboard is created
        :param tournament_model: Model containing all tournaments
        :param tournament_limit: Limit of the tournaments that prevent player to show up in the leaderboard
        :param seeded_multiplier: Determines how much impact have seeded races in mixed leaderboard
        :param mixed_multiplier:  Determines how much impact have mixed races in the leaderboard
        """
        self.racers = defaultdict(dict)
        self.seeded_racers = defaultdict(dict)
        self.unseeded_racers = defaultdict(dict)
        self.tournament = tournament_model
        self.leaderboard = leaderboard_model
        self.player = player_model
        self.mixed_multiplier = mixed_multiplier
        self.seeded_multiplier = seeded_multiplier
        self.tournament_limit = tournament_limit

    def create_leaderboards(self):
        for tournament in self.tournament.objects.all().order_by('date', 'id'):
            players_in_tourney = []
            players_in_seeded_tourney = []
            players_in_unseeded_tourney = []
            for match in tournament.match_set.all().order_by('id'):
                ruleset = tournament.ruleset.ruleset
                if ruleset == 'other':
                    continue
                elif ruleset == 'team':
                    continue
                elif ruleset == 'seeded':
                    self.initiate_player(match, players_in_tourney, seeded=players_in_seeded_tourney)
                    for _ in range(self.seeded_multiplier):
                        self.calculate_rating(match, self.racers)
                    self.calculate_rating(match, self.seeded_racers)
                elif ruleset == 'mixed':
                    self.initiate_player(match, players_in_tourney, unseeded=players_in_unseeded_tourney)
                    for _ in range(self.mixed_multiplier):
                        self.calculate_rating(match, self.racers)
                    self.calculate_rating(match, self.unseeded_racers)
                elif ruleset == 'multiple':
                    if match.ruleset is not None:
                        if match.ruleset.ruleset == 'seeded':
                            self.initiate_player(match, players_in_tourney, seeded=players_in_seeded_tourney)
                            for _ in range(self.seeded_multiplier):
                                self.calculate_rating(match, self.racers)
                            self.calculate_rating(match, self.seeded_racers)
                        else:
                            self.initiate_player(match, players_in_tourney, unseeded=players_in_unseeded_tourney)
                            self.calculate_rating(match, self.racers)
                            self.calculate_rating(match, self.unseeded_racers)
                else:  # unseeded and diversity
                    self.initiate_player(match, players_in_tourney, unseeded=players_in_unseeded_tourney)
                    self.calculate_rating(match, self.racers)
                    self.calculate_rating(match, self.unseeded_racers)
        mixed_leaderboard = self.calculate_places(self.racers)
        unseeded_leaderboard = self.calculate_places(self.unseeded_racers)
        seeded_learderboard = self.calculate_places(self.seeded_racers)
        self.export_leaderboard_to_db('mixed', mixed_leaderboard)
        self.export_leaderboard_to_db('unseeded', unseeded_leaderboard)
        self.export_leaderboard_to_db('seeded', seeded_learderboard)

    def export_leaderboard_to_db(self, leaderboard_type: str, leaderboard_list):
        for record in leaderboard_list:
            player = self.leaderboard.objects.get_or_create(player=self.player.objects.get(name=record['name']),
                                                            leaderboard_type=leaderboard_type)[0]
            player.placement = record['place']
            player.exposure = record['exposure']
            player.mu = record['mu']
            player.sigma = record['sigma']
            player.tournaments_played = record['tournaments_played']
            player.matches_played = record['matches_played']
            player.save()

    def calculate_places(self, racers_dict):
        # Creating leaderboard, sorting by exposure value
        leaderboards_list = [
            {
                'name': key,
                'tournaments_played': value['tournaments_played'],
                'matches_played': value['matches_played'],
                'exposure': value['rating'].exposure,
                'mu': value['rating'].mu,
                'sigma': value['rating'].sigma
            } for key, value in racers_dict.items() if value['tournaments_played'] >= self.tournament_limit
        ]
        leaderboards_list.sort(key=lambda x: x['exposure'], reverse=True)
        for place, player in enumerate(leaderboards_list):
            player['place'] = place + 1
        return leaderboards_list

    def initiate_player(self, match, players_in_tourney, **kwargs):
        self.check_players(match, self.racers)
        self.increment_tourney_played(match, self.racers, players_in_tourney)
        self.increment_match_played(match, self.racers)
        for key, value in kwargs.items():
            if key == 'unseeded':
                self.check_players(match, self.unseeded_racers)
                self.increment_tourney_played(match, self.unseeded_racers, value)
                self.increment_match_played(match, self.unseeded_racers)
            elif key == 'seeded':
                self.check_players(match, self.seeded_racers)
                self.increment_tourney_played(match, self.seeded_racers, value)
                self.increment_match_played(match, self.seeded_racers)

    @staticmethod
    def check_players(match, racers_dict):
        winner = match.winner.name
        loser = match.loser.name
        if winner not in racers_dict:
            racers_dict[winner]['rating'] = trueskill.Rating(25)
            racers_dict[winner]['matches_played'] = 0
            racers_dict[winner]['tournaments_played'] = 0
        if loser not in racers_dict:
            racers_dict[loser]['rating'] = trueskill.Rating(25)
            racers_dict[loser]['matches_played'] = 0
            racers_dict[loser]['tournaments_played'] = 0

    @staticmethod
    def increment_tourney_played(match, racers_dict, tourney_players):
        winner = match.winner.name
        loser = match.loser.name
        if winner not in tourney_players:
            tourney_players.append(winner)
            racers_dict[winner]['tournaments_played'] += 1
        if loser not in tourney_players:
            tourney_players.append(loser)
            racers_dict[loser]['tournaments_played'] += 1

    @staticmethod
    def increment_match_played(match, racers_dict):
        winner = match.winner.name
        loser = match.loser.name
        racers_dict[winner]['matches_played'] += 1
        racers_dict[loser]['matches_played'] += 1

    @staticmethod
    def calculate_rating(match, racers_dict):
        winner = match.winner.name
        loser = match.loser.name
        if match.score != 'draw':
            racers_dict[winner]['rating'], racers_dict[loser]['rating'] = \
                trueskill.rate_1vs1(racers_dict[winner]['rating'], racers_dict[loser]['rating'])
