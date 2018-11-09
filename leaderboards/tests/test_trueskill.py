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
                                    ruleset=Ruleset.objects.get_or_create(ruleset=ruleset)[0])
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

    def assertTrueskillEqual(self, trueskill_object, database_object):
        self.assertAlmostEqual(trueskill_object.mu, database_object.mu)
        self.assertAlmostEqual(trueskill_object.sigma, database_object.sigma)
        self.assertAlmostEqual(trueskill.expose(trueskill_object), database_object.exposure)

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
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
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
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
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
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
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
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
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
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
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
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
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
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
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
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
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

    def test_mixed_leaderboard_with_other_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Other tournaments shouldn't appear in mixed leaderboards
        """
        tourney = create_tournament('Other Tournament', '2018-05-10', 'other')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='mixed')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='mixed')

    def test_unseeded_leaderboard_with_other_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Other tournaments shouldn't appear in unseeded leaderboards
        """
        tourney = create_tournament('Other Tournament', '2018-05-10', 'other')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')

    def test_seeded_leaderboard_with_other_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Other tournaments shouldn't appear in seeded leaderboards
        """
        tourney = create_tournament('Other Tournament', '2018-05-10', 'other')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_all_leaderboards_with_team_tournament_with_one_match(self):
        """
        Team tournaments shouldn't appear in any leaderboard
        """
        tourney = create_tournament('Team Tournament', '2018-05-10', 'team')
        create_match('team_1', 'team_2', tourney)
        create_leaderboard_without_limit()
        self.assertQuerysetEqual(Leaderboard.objects.all(), [])

    def test_mixed_leaderboard_with_unknown_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Tournaments that ruleset is unknown by default shouldn't count towards leaderboards
        """
        tourney = create_tournament('Unknown Tournament', '2018-05-10', 'unknown')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='mixed')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='mixed')

    def test_unseeded_leaderboard_with_unknown_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Tournaments that ruleset is unknown by default shouldn't count towards leaderboards
        """
        tourney = create_tournament('Unknown Tournament', '2018-05-10', 'unknown')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')

    def test_seeded_leaderboard_with_unknown_tournament_with_one_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Tournaments that ruleset is unknown by default shouldn't count towards leaderboards
        """
        tourney = create_tournament('Unknown Tournament', '2018-05-10', 'unknown')
        create_match('player_1', 'player_2', tourney)
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_mixed_leaderboard_with_multiple_tournament_with_one_seeded_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Seeded match in multiple tournament by default should be weighted 4 times more than regular match
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'seeded')
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(4):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_unseeded_leaderboard_with_multiple_tournament_with_one_seeded_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Seeded match of multiple format shouldn't appear in unseeded leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'seeded')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')

    def test_seeded_leaderboard_with_multiple_tournament_with_one_seeded_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Seeded match of multiple tournament should appear in seeded leaderboard and be weighted equally as other matches
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'seeded')
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'seeded')
        db_player_2 = get_rating('player_2', 'seeded')
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_mixed_leaderboard_with_multiple_tournament_with_one_unseeded_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Unseeded match in multiple tournament should count towards mixed leaderboard and be weighted as 1
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'unseeded')
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_seeded_leaderboard_with_multiple_tournament_with_one_unseeded_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Uneeded match of multiple format shouldn't appear in seeded leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'unseeded')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_unseeded_leaderboard_with_multiple_tournament_with_one_unseeded_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Unseeded match of multiple tournament should appear in unseeded leaderboard and be weighted equally to other
        matches
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'unseeded')
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_mixed_leaderboard_with_multiple_tournament_with_one_diversity_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Diversity match in multiple tournament should count towards mixed leaderboard and be weighted as 1
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'diversity')
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_seeded_leaderboard_with_multiple_tournament_with_one_diversity_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Diversity match of multiple format shouldn't appear in seeded leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'diversity')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_unseeded_leaderboard_with_multiple_tournament_with_one_diversity_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Diversity match of multiple tournament should appear in unseeded leaderboard and be weighted equally to other
        matches
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'diversity')
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_mixed_leaderboard_with_multiple_tournament_with_one_mixed_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Mixed match in multiple tournament should count towards mixed leaderboard and be weighted 2 on default
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'mixed')
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(2):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_seeded_leaderboard_with_multiple_tournament_with_one_mixed_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Mixed match of multiple format shouldn't appear in seeded leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'mixed')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_unseeded_leaderboard_with_multiple_tournament_with_one_mixed_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Mixed match of multiple tournament should appear in unseeded leaderboard and be weighted equally to other
        matches
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'mixed')
        create_leaderboard_without_limit()
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)
        self.assertEqual(1, db_player_1.tournaments_played)
        self.assertEqual(1, db_player_1.matches_played)
        self.assertEqual(1, db_player_2.tournaments_played)
        self.assertEqual(1, db_player_2.matches_played)

    def test_mixed_leaderboard_with_multiple_tournament_with_one_other_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Other match of multiple tournament shouldn't count towards mixed leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'other')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='mixed')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='mixed')

    def test_seeded_leaderboard_with_multiple_tournament_with_one_other_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Other match of multiple format shouldn't appear in seeded leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'other')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_unseeded_leaderboard_with_multiple_tournament_with_one_other_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Other match of multiple tournament shouldn't appear in unseeded leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'other')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')

    def test_mixed_leaderboard_with_multiple_tournament_with_one_multiple_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Having multiple match in multiple tournaments is most likely an error and shouldn't count towards mixed
        leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'multiple')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='mixed')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='mixed')

    def test_seeded_leaderboard_with_multiple_tournament_with_one_multiple_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Having multiple match in multiple tournaments is most likely an error and shouldn't count towards mixed
        leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'multiple')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_unseeded_leaderboard_with_multiple_tournament_with_one_multiple_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Having multiple match in multiple tournaments is most likely an error and shouldn't count towards mixed
        leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'multiple')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')

    def test_all_leaderboards_with_multiple_tournament_with_one_team_match(self):
        """
        Team match of multiple tournament shouldn't appear in any leaderboard
        """
        tourney = create_tournament('Team Tournament', '2018-05-10', 'team')
        create_match('team_1', 'team_2', tourney, 'team')
        create_leaderboard_without_limit()
        self.assertQuerysetEqual(Leaderboard.objects.all(), [])

    def test_mixed_leaderboard_with_multiple_tournament_with_one_unknown_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Unknown matches in tournaments shouldn't count towards mixed leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'unknown')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='mixed')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='mixed')

    def test_seeded_leaderboard_with_multiple_tournament_with_one_unknown_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Unknown matches in tournaments shouldn't count towards seeded leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'unknown')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')

    def test_unseeded_leaderboard_with_multiple_tournament_with_one_unknown_match(self):
        """
        Checks if calculations made in TrueskillCalculations class are equal to raw trueskill calculations
        Unknown matches in tournaments shouldn't count towards unseeded leaderboard
        """
        tourney = create_tournament('Multiple Tournament', '2018-05-10', 'multiple')
        create_match('player_1', 'player_2', tourney, 'unknown')
        create_leaderboard_without_limit()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_1',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')

    def test_match_ordering_in_tournament(self):
        """
        Matches in tournament should be ordered and calculated in the same order as they are added. Since order in
        the trueskill algorithm matters, we can check it with comparing trueskill values.
        """
        tourney = create_tournament('Unseeded Tournament', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney)
        create_match('player_1', 'player_2', tourney)
        create_match('player_1', 'player_2', tourney)
        create_match('player_2', 'player_1', tourney)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(3):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        player_2, player_1 = trueskill.rate_1vs1(player_2, player_1)
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)

    def test_tournament_ordering_with_different_dates(self):
        """
        When tournaments have different dates they should be ordered by them.
        """
        tourney_3 = create_tournament('Unseeded Tournament 3', '2018-05-12', 'unseeded')
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-08', 'unseeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_2', 'player_1', tourney_3)
        create_match('player_1', 'player_2', tourney_2)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(2):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        player_2, player_1 = trueskill.rate_1vs1(player_2, player_1)
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)

    def test_tournament_ordering_with_the_same_dates(self):
        """
        When tournaments have the same dates they should be calculated in order they were added.
        """
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-10', 'unseeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'unseeded')
        tourney_3 = create_tournament('Unseeded Tournament 3', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_2', 'player_1', tourney_3)
        create_match('player_1', 'player_2', tourney_2)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(2):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        player_2, player_1 = trueskill.rate_1vs1(player_2, player_1)
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)

    def test_default_tournament_limit_in_unseeded_leaderboard(self):
        """
        Check if default limit of 2 tournaments to show on the leaderboard works properly
        """
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-10', 'unseeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_3', tourney_2)
        TrueskillCalculations(tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_3',
                          leaderboard_type='unseeded')
        self.assertTrue(Leaderboard.objects.filter(player__name='player_1', leaderboard_type='unseeded').exists())

    def test_default_tournament_limit_in_mixed_leaderboard(self):
        """
        Check if default limit of 2 tournaments to show on the leaderboard works properly
        """
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-10', 'unseeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_3', tourney_2)
        TrueskillCalculations(tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='mixed')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_3',
                          leaderboard_type='mixed')
        self.assertTrue(Leaderboard.objects.filter(player__name='player_1', leaderboard_type='mixed').exists())

    def test_default_tournament_limit_in_seeded_leaderboard(self):
        """
        Check if default limit of 2 tournaments to show on the leaderboard works properly
        """
        tourney_1 = create_tournament('Seeded Tournament 1', '2018-05-10', 'seeded')
        tourney_2 = create_tournament('Seeded Tournament 2', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_3', tourney_2)
        TrueskillCalculations(tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_3',
                          leaderboard_type='seeded')
        self.assertTrue(Leaderboard.objects.filter(player__name='player_1', leaderboard_type='seeded').exists())

    def test_custom_tournament_limit_in_unseeded_leaderboard(self):
        """
        Check if custom tournament limit works as expected
        """
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-10', 'unseeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'unseeded')
        tourney_3 = create_tournament('Unseeded Tournament 3', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_3', tourney_2)
        create_match('player_1', 'player_3', tourney_3)
        TrueskillCalculations(tournament_limit=3, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='unseeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_3',
                          leaderboard_type='unseeded')
        self.assertTrue(Leaderboard.objects.filter(player__name='player_1', leaderboard_type='unseeded').exists())

    def test_custom_tournament_limit_in_mixed_leaderboard(self):
        """
        Check if custom tournament limit works as expected
        """
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-10', 'unseeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'unseeded')
        tourney_3 = create_tournament('Unseeded Tournament 3', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_3', tourney_2)
        create_match('player_1', 'player_3', tourney_3)
        TrueskillCalculations(tournament_limit=3, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='mixed')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_3',
                          leaderboard_type='mixed')
        self.assertTrue(Leaderboard.objects.filter(player__name='player_1', leaderboard_type='mixed').exists())

    def test_custom_tournament_limit_in_seeded_leaderboard(self):
        """
        Check if custom tournament limit works as expected
        """
        tourney_1 = create_tournament('Seeded Tournament 1', '2018-05-10', 'seeded')
        tourney_2 = create_tournament('Seeded Tournament 2', '2018-05-10', 'seeded')
        tourney_3 = create_tournament('Seeded Tournament 3', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_3', tourney_2)
        create_match('player_1', 'player_3', tourney_3)
        TrueskillCalculations(tournament_limit=3, tournament_model=Tournament, leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_2',
                          leaderboard_type='seeded')
        self.assertRaises(Leaderboard.DoesNotExist, Leaderboard.objects.get, player__name='player_3',
                          leaderboard_type='seeded')
        self.assertTrue(Leaderboard.objects.filter(player__name='player_1', leaderboard_type='seeded').exists())

    def test_custom_seeded_multiplier_for_mixed_leaderboard(self):
        """
        Testing if changing default seeded multiplier works as expected
        """
        tourney = create_tournament('Seeded Tournament', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney)
        custom_multiplier = 5
        TrueskillCalculations(seeded_multiplier=custom_multiplier, tournament_limit=0, tournament_model=Tournament,
                              leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(custom_multiplier):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)

    def test_custom_mixed_multiplier_for_mixed_leaderboard(self):
        """
        Testing if changing default mixed multiplier works as expected
        """
        tourney = create_tournament('Mixed Tournament', '2018-05-10', 'mixed')
        create_match('player_1', 'player_2', tourney)
        custom_multiplier = 5
        TrueskillCalculations(mixed_multiplier=custom_multiplier, tournament_limit=0, tournament_model=Tournament,
                              leaderboard_model=Leaderboard,
                              player_model=Player).create_leaderboards()
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
        player_1 = trueskill.Rating(25)
        player_2 = trueskill.Rating(25)
        for _ in range(custom_multiplier):
            player_1, player_2 = trueskill.rate_1vs1(player_1, player_2)
        self.assertTrueskillEqual(player_1, db_player_1)
        self.assertTrueskillEqual(player_2, db_player_2)

    def test_match_incrementation_in_mixed_leaderboard(self):
        """
        Test if matches played are incremented properly
        """
        tourney = create_tournament('Unseeded Tournament', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney)
        create_match('player_1', 'player_3', tourney)
        create_match('player_1', 'player_4', tourney)
        create_match('player_3', 'player_2', tourney)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
        db_player_3 = get_rating('player_3', 'mixed')
        db_player_4 = get_rating('player_4', 'mixed')
        self.assertEqual(db_player_1.matches_played, 3)
        self.assertEqual(db_player_2.matches_played, 2)
        self.assertEqual(db_player_3.matches_played, 2)
        self.assertEqual(db_player_4.matches_played, 1)

    def test_match_incrementation_in_seeded_leaderboard(self):
        """
        Test if matches played are incremented properly
        """
        tourney = create_tournament('Seeded Tournament', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney)
        create_match('player_1', 'player_3', tourney)
        create_match('player_1', 'player_4', tourney)
        create_match('player_3', 'player_2', tourney)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'seeded')
        db_player_2 = get_rating('player_2', 'seeded')
        db_player_3 = get_rating('player_3', 'seeded')
        db_player_4 = get_rating('player_4', 'seeded')
        self.assertEqual(db_player_1.matches_played, 3)
        self.assertEqual(db_player_2.matches_played, 2)
        self.assertEqual(db_player_3.matches_played, 2)
        self.assertEqual(db_player_4.matches_played, 1)

    def test_match_incrementation_in_unseeded_leaderboard(self):
        """
        Test if matches played are incremented properly
        """
        tourney = create_tournament('Unseeded Tournament', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney)
        create_match('player_1', 'player_3', tourney)
        create_match('player_1', 'player_4', tourney)
        create_match('player_3', 'player_2', tourney)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
        db_player_3 = get_rating('player_3', 'unseeded')
        db_player_4 = get_rating('player_4', 'unseeded')
        self.assertEqual(db_player_1.matches_played, 3)
        self.assertEqual(db_player_2.matches_played, 2)
        self.assertEqual(db_player_3.matches_played, 2)
        self.assertEqual(db_player_4.matches_played, 1)

    def test_tournaments_incrementation_in_mixed_leaderboard(self):
        """
        Test if tournaments played are incremented properly
        """
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-10', 'unseeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'unseeded')
        tourney_3 = create_tournament('Unseeded Tournament 3', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_2', tourney_2)
        create_match('player_3', 'player_2', tourney_3)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'mixed')
        db_player_2 = get_rating('player_2', 'mixed')
        db_player_3 = get_rating('player_3', 'mixed')
        self.assertEqual(db_player_1.tournaments_played, 2)
        self.assertEqual(db_player_2.tournaments_played, 3)
        self.assertEqual(db_player_3.tournaments_played, 1)

    def test_tournaments_incrementation_in_unseeded_leaderboard(self):
        """
        Test if tournaments played are incremented properly
        """
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-10', 'unseeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'unseeded')
        tourney_3 = create_tournament('Unseeded Tournament 3', '2018-05-10', 'unseeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_2', tourney_2)
        create_match('player_3', 'player_2', tourney_3)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'unseeded')
        db_player_2 = get_rating('player_2', 'unseeded')
        db_player_3 = get_rating('player_3', 'unseeded')
        self.assertEqual(db_player_1.tournaments_played, 2)
        self.assertEqual(db_player_2.tournaments_played, 3)
        self.assertEqual(db_player_3.tournaments_played, 1)

    def test_tournaments_incrementation_in_seeded_leaderboard(self):
        """
        Test if tournaments played are incremented properly
        """
        tourney_1 = create_tournament('Unseeded Tournament 1', '2018-05-10', 'seeded')
        tourney_2 = create_tournament('Unseeded Tournament 2', '2018-05-10', 'seeded')
        tourney_3 = create_tournament('Unseeded Tournament 3', '2018-05-10', 'seeded')
        create_match('player_1', 'player_2', tourney_1)
        create_match('player_1', 'player_2', tourney_2)
        create_match('player_3', 'player_2', tourney_3)
        create_leaderboard_without_limit()
        db_player_1 = get_rating('player_1', 'seeded')
        db_player_2 = get_rating('player_2', 'seeded')
        db_player_3 = get_rating('player_3', 'seeded')
        self.assertEqual(db_player_1.tournaments_played, 2)
        self.assertEqual(db_player_2.tournaments_played, 3)
        self.assertEqual(db_player_3.tournaments_played, 1)
