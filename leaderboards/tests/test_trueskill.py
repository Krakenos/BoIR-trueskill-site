import trueskill
from django.test import TestCase

from leaderboards.models import Player, Leaderboard, Tournament, Ruleset, Match
from leaderboards.trueskill_scripts.trueskill_calculation import TrueskillCalculations


def create_tournament(name, date, ruleset):
    return Tournament.objects.create(name=name, date=date, ruleset=Ruleset.objects.create(ruleset=ruleset))


def create_match(winner, loser, tournament):
    return Match.objects.create(tournament=tournament,
                                winner=Player.objects.get_or_create(name=winner)[0],
                                loser=Player.objects.get_or_create(name=loser)[0])


class TrueskillCalculationsTests(TestCase):

    def test_mixed_leaderboard_with_unseeded_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        """
        tourney = create_tournament('Unseeded Tournament', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney)
        TrueskillCalculations(tournament_limit=0, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = Leaderboard.objects.get(player__name='player_1', leaderboard_type='mixed')
        db_player_2 = Leaderboard.objects.get(player__name='player_2', leaderboard_type='mixed')
        self.assertAlmostEqual(player_1.mu, db_player_1.mu)
        self.assertAlmostEqual(player_1.sigma, db_player_1.sigma)
        self.assertAlmostEqual(trueskill.expose(player_1), db_player_1.exposure)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertAlmostEqual(player_2.mu, db_player_2.mu)
        self.assertAlmostEqual(player_2.sigma, db_player_2.sigma)
        self.assertAlmostEqual(trueskill.expose(player_2), db_player_2.exposure)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_unseeded_leaderboard_with_unseeded_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        """
        tourney = create_tournament('Unseeded Tournament', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney)
        TrueskillCalculations(tournament_limit=0, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = Leaderboard.objects.get(player__name='player_1', leaderboard_type='unseeded')
        db_player_2 = Leaderboard.objects.get(player__name='player_2', leaderboard_type='unseeded')
        self.assertAlmostEqual(player_1.mu, db_player_1.mu)
        self.assertAlmostEqual(player_1.sigma, db_player_1.sigma)
        self.assertAlmostEqual(trueskill.expose(player_1), db_player_1.exposure)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertAlmostEqual(player_2.mu, db_player_2.mu)
        self.assertAlmostEqual(player_2.sigma, db_player_2.sigma)
        self.assertAlmostEqual(trueskill.expose(player_2), db_player_2.exposure)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_seeded_leaderboard_with_unseeded_tournament_with_one_match(self):
        """
        Unseeded matches shouldn't count towards seeded leaderboard
        """
        tourney = create_tournament('Unseeded Tournament', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney)
        TrueskillCalculations(tournament_limit=0, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        db_player_1 = Leaderboard.objects.filter(player__name='player_1', leaderboard_type='seeded')
        db_player_2 = Leaderboard.objects.filter(player__name='player_2', leaderboard_type='seeded')
        self.assertQuerysetEqual(db_player_1, [])
        self.assertQuerysetEqual(db_player_2, [])

    def test_mixed_leaderboard_with_diversity_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        """
        tourney = create_tournament('Diversity Tournament', '2018-05-10', 'diversity')
        create_match('player_1', 'player_2', tourney)
        TrueskillCalculations(tournament_limit=0, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = Leaderboard.objects.get(player__name='player_1', leaderboard_type='mixed')
        db_player_2 = Leaderboard.objects.get(player__name='player_2', leaderboard_type='mixed')
        self.assertAlmostEqual(player_1.mu, db_player_1.mu)
        self.assertAlmostEqual(player_1.sigma, db_player_1.sigma)
        self.assertAlmostEqual(trueskill.expose(player_1), db_player_1.exposure)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertAlmostEqual(player_2.mu, db_player_2.mu)
        self.assertAlmostEqual(player_2.sigma, db_player_2.sigma)
        self.assertAlmostEqual(trueskill.expose(player_2), db_player_2.exposure)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_unseeded_leaderboard_with_diversity_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        """
        tourney = create_tournament('Diversity Tournament', '2018-05-10', 'diversity')
        create_match('player_1', 'player_2', tourney)
        TrueskillCalculations(tournament_limit=0, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = Leaderboard.objects.get(player__name='player_1', leaderboard_type='unseeded')
        db_player_2 = Leaderboard.objects.get(player__name='player_2', leaderboard_type='unseeded')
        self.assertAlmostEqual(player_1.mu, db_player_1.mu)
        self.assertAlmostEqual(player_1.sigma, db_player_1.sigma)
        self.assertAlmostEqual(trueskill.expose(player_1), db_player_1.exposure)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertAlmostEqual(player_2.mu, db_player_2.mu)
        self.assertAlmostEqual(player_2.sigma, db_player_2.sigma)
        self.assertAlmostEqual(trueskill.expose(player_2), db_player_2.exposure)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_seeded_leaderboard_with_diversity_tournament_with_one_match(self):
        """
        Diversity tournaments shouldn't count towards seeded leaderboards
        """
        tourney = create_tournament('Diversity Tournament', '2018-05-10', 'diversity')
        create_match('player_1', 'player_2', tourney)
        new_calcs = TrueskillCalculations(tournament_limit=0, tournament_model=Tournament,
                                          leaderboard_model=Leaderboard,
                                          player_model=Player)
        new_calcs.create_leaderboards()
        db_player_1 = Leaderboard.objects.filter(player__name='player_1', leaderboard_type='seeded')
        db_player_2 = Leaderboard.objects.filter(player__name='player_2', leaderboard_type='seeded')
        self.assertQuerysetEqual(db_player_1, [])
        self.assertQuerysetEqual(db_player_2, [])

    def test_mixed_leaderboard_with_seeded_tournament_with_one_match(self):
        """
        Seeded tournaments should by default be weighted 4 times more than regular unseeded events in mixed leaderboard
        """
        tourney = create_tournament('Seeded Tournament', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney)
        TrueskillCalculations(tournament_limit=0, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(4):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = Leaderboard.objects.get(player__name='player_1', leaderboard_type='mixed')
        db_player_2 = Leaderboard.objects.get(player__name='player_2', leaderboard_type='mixed')
        self.assertAlmostEqual(player_1.mu, db_player_1.mu)
        self.assertAlmostEqual(player_1.sigma, db_player_1.sigma)
        self.assertAlmostEqual(trueskill.expose(player_1), db_player_1.exposure)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertAlmostEqual(player_2.mu, db_player_2.mu)
        self.assertAlmostEqual(player_2.sigma, db_player_2.sigma)
        self.assertAlmostEqual(trueskill.expose(player_2), db_player_2.exposure)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_unseeded_leaderboard_with_seeded_tournament_with_one_match(self):
        """
        Seeded events shouldn't count towards unseeded leaderboard
        """
        tourney = create_tournament('Seeded Tournament', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney)
        TrueskillCalculations(tournament_limit=0, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        db_player_1 = Leaderboard.objects.filter(player__name='player_1', leaderboard_type='unseeded')
        db_player_2 = Leaderboard.objects.filter(player__name='player_2', leaderboard_type='unseeded')
        self.assertQuerysetEqual(db_player_1, [])
        self.assertQuerysetEqual(db_player_2, [])
