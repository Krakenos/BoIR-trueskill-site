import trueskill
from django.test import TestCase

from leaderboards.models import Player, Leaderboard, Tournament, Ruleset, Match, Team
from leaderboards.trueskill_scripts.trueskill_calculation import TrueskillCalculations


def create_tournament(name, date, ruleset):
    return Tournament.objects.create(name=name, date=date, ruleset=Ruleset.objects.create(ruleset=ruleset))


def create_match(winner, loser, tournament, ruleset=None):
    if ruleset:
        return Match.objects.create(tournament=tournament,
                                    winner=Player.objects.get_or_create(name=winner)[0],
                                    loser=Player.objects.get_or_create(name=loser)[0],
                                    ruleset=Ruleset.objects.get_or_create(ruleset=ruleset))
    return Match.objects.create(tournament=tournament,
                                winner=Player.objects.get_or_create(name=winner)[0],
                                loser=Player.objects.get_or_create(name=loser)[0],
                                ruleset=tournament.ruleset)


def create_team_match(winner, loser, tournament):
    return Match.objects.create(tournament=tournament,
                                winner_team=Team.objects.get_or_create(tournament=tournament, name=winner)[0],
                                loser_team=Team.objects.get_or_create(tournament=tournament, name=loser)[0],
                                ruleset='team')


def create_leaderboard_without_limit():
    """
    By default it's required for the player to play in at least 2 tournaments, by changing tournament_limit to 0 we are
    bypassing this requirement to test calculations with a single match
    """
    return TrueskillCalculations(tournament_limit=0, tournament_model=Tournament, leaderboard_model=Leaderboard,
                                 player_model=Player).create_leaderboards()


def get_rating(player, leaderboard_type):
    return Leaderboard.objects.get(player__name=player, leaderboard_type=leaderboard_type)


class TrueskillCalculationsTests(TestCase):

    def test_mixed_leaderboard_with_unseeded_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        """
        tourney = create_tournament('Unseeded Tournament', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
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
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
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
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Unseeded matches shouldn't count towards seeded leaderboard
        """
        tourney = create_tournament('Unseeded Tournament', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_mixed_leaderboard_with_diversity_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        """
        tourney = create_tournament('Diversity Tournament', '2018-05-10', 'diversity')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
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
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
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
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Diversity tournaments shouldn't count towards seeded leaderboards
        """
        tourney = create_tournament('Diversity Tournament', '2018-05-10', 'diversity')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_mixed_leaderboard_with_seeded_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Seeded tournaments should by default be weighted 4 times more than regular unseeded events in mixed leaderboard
        """
        tourney = create_tournament('Seeded Tournament', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(4):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
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
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Seeded events shouldn't count towards unseeded leaderboard
        """
        tourney = create_tournament('Seeded Tournament', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')

    def test_seeded_leaderboard_with_seeded_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Seeded tournaments should by default be weighted 4 times more than regular unseeded events in mixed leaderboard
        """
        tourney = create_tournament('Seeded Tournament', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'seeded')
        db_player_2 = get_rating('player_2', 'seeded')
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

    def test_mixed_leaderboard_with_mixed_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Mixed tournaments should by default be weighted 2 times more than regular unseeded events in mixed leaderboard
        """
        tourney = create_tournament('Mixed Tournament', '2018-05-10', 'mixed')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(2):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
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

    def test_unseeded_leaderboard_with_mixed_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Mixed tournaments in unseeded leaderboard are weighted the same as other events
        """
        tourney = create_tournament('Mixed Tournament', '2018-05-10', 'mixed')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
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

    def test_seeded_leaderboard_with_mixed_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Mixed tournaments shouldn't appear in seeded leaderboards
        """
        tourney = create_tournament('Mixed Tournament', '2018-05-10', 'mixed')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')
