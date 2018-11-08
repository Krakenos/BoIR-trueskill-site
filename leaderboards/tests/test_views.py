from django.test import TestCase
from django.urls import reverse
from leaderboards.models import Tournament, Ruleset, Leaderboard, Player
from django.core.cache import cache


def create_ruleset(name):
    return Ruleset.objects.create(ruleset=name)


def create_tournament(name, date, ruleset):
    return Tournament.objects.create(name=name, date=date, ruleset=ruleset)


def create_leaderboard_entry(leaderboard_type, place, player_name, exposure, tournaments_played, matches_played):
    return Leaderboard.objects.create(leaderboard_type=leaderboard_type, placement=place,
                                      player=Player.objects.create(name=player_name),
                                      exposure=exposure, tournaments_played=tournaments_played,
                                      matches_played=matches_played)


class IndexViewTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_with_no_tourneys(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'], [])
        self.assertQuerysetEqual(response.context['seeded_events'], [])
        self.assertQuerysetEqual(response.context['unseeded_events'], [])

    def test_with_unseeded_event(self):
        """
        Unseeded tourney should be listed as mixed and unseeded event
        """
        unseeded_ruleset = create_ruleset('unseeded')
        create_tournament('Unseeded Tourney', '2018-05-05', unseeded_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'], ['<Tournament: Unseeded Tourney>'])
        self.assertQuerysetEqual(response.context['seeded_events'], [])
        self.assertQuerysetEqual(response.context['unseeded_events'], ['<Tournament: Unseeded Tourney>'])

    def test_with_mixed_event(self):
        """
        Mixed tourneys should be listed as mixed and unseeded events
        """
        mixed_ruleset = create_ruleset('mixed')
        create_tournament('Mixed Tourney', '2018-05-05', mixed_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'], ['<Tournament: Mixed Tourney>'])
        self.assertQuerysetEqual(response.context['seeded_events'], [])
        self.assertQuerysetEqual(response.context['unseeded_events'], ['<Tournament: Mixed Tourney>'])

    def test_with_diversity_event(self):
        """
        Diversity tourney should be listed as mixed and unseeded event
        """
        diversity_ruleset = create_ruleset('diversity')
        create_tournament('Diversity Tourney', '2018-05-05', diversity_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'], ['<Tournament: Diversity Tourney>'])
        self.assertQuerysetEqual(response.context['seeded_events'], [])
        self.assertQuerysetEqual(response.context['unseeded_events'], ['<Tournament: Diversity Tourney>'])

    def test_with_seeded_event(self):
        """
        Seeded tourney should be listed as mixed and seeded event
        """
        seeded_ruleset = create_ruleset('seeded')
        create_tournament('Seeded Tourney', '2018-05-05', seeded_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'], ['<Tournament: Seeded Tourney>'])
        self.assertQuerysetEqual(response.context['seeded_events'], ['<Tournament: Seeded Tourney>'])
        self.assertQuerysetEqual(response.context['unseeded_events'], [])

    def test_with_multiple_event(self):
        """
        Multiple tourneys should be listed as mixed, seeded and unseeded events
        """
        multiple_ruleset = create_ruleset('multiple')
        create_tournament('Multiple Tourney', '2018-05-05', multiple_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'], ['<Tournament: Multiple Tourney>'])
        self.assertQuerysetEqual(response.context['seeded_events'], ['<Tournament: Multiple Tourney>'])
        self.assertQuerysetEqual(response.context['unseeded_events'], ['<Tournament: Multiple Tourney>'])

    def test_with_team_event(self):
        """
        Team tourneys shouldn't be listed at all
        """
        team_ruleset = create_ruleset('team')
        create_tournament('Team Tourney', '2018-05-05', team_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'], [])
        self.assertQuerysetEqual(response.context['seeded_events'], [])
        self.assertQuerysetEqual(response.context['unseeded_events'], [])

    def test_with_other_event(self):
        """
        Other tourneys shouldn't be listed at all
        """
        other_ruleset = create_ruleset('other')
        create_tournament('Other Tourney', '2018-05-05', other_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'], [])
        self.assertQuerysetEqual(response.context['seeded_events'], [])
        self.assertQuerysetEqual(response.context['unseeded_events'], [])

    def test_mixed_events_ordering_with_different_dates(self):
        """
        Events should be ordered by their date, newest being on top
        """
        unseeded_ruleset = create_ruleset('unseeded')
        create_tournament('Unseeded Tourney 4', '2018-05-08', unseeded_ruleset)
        create_tournament('Unseeded Tourney 1', '2018-05-05', unseeded_ruleset)
        create_tournament('Unseeded Tourney 3', '2018-05-07', unseeded_ruleset)
        create_tournament('Unseeded Tourney 2', '2018-05-06', unseeded_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'],
                                 ['<Tournament: Unseeded Tourney 4>', '<Tournament: Unseeded Tourney 3>',
                                  '<Tournament: Unseeded Tourney 2>', '<Tournament: Unseeded Tourney 1>'])

    def test_seeded_events_ordering_with_different_dates(self):
        """
        Events should be ordered by their date, newest being on top
        """
        seeded_ruleset = create_ruleset('seeded')
        create_tournament('Seeded Tourney 4', '2018-05-08', seeded_ruleset)
        create_tournament('Seeded Tourney 1', '2018-05-05', seeded_ruleset)
        create_tournament('Seeded Tourney 3', '2018-05-07', seeded_ruleset)
        create_tournament('Seeded Tourney 2', '2018-05-06', seeded_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['seeded_events'],
                                 ['<Tournament: Seeded Tourney 4>', '<Tournament: Seeded Tourney 3>',
                                  '<Tournament: Seeded Tourney 2>', '<Tournament: Seeded Tourney 1>'])

    def test_unseeded_events_ordering_with_different_dates(self):
        """
        Events should be ordered by their date, newest being on top
        """
        unseeded_ruleset = create_ruleset('unseeded')
        create_tournament('Unseeded Tourney 4', '2018-05-08', unseeded_ruleset)
        create_tournament('Unseeded Tourney 1', '2018-05-05', unseeded_ruleset)
        create_tournament('Unseeded Tourney 3', '2018-05-07', unseeded_ruleset)
        create_tournament('Unseeded Tourney 2', '2018-05-06', unseeded_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['unseeded_events'],
                                 ['<Tournament: Unseeded Tourney 4>', '<Tournament: Unseeded Tourney 3>',
                                  '<Tournament: Unseeded Tourney 2>', '<Tournament: Unseeded Tourney 1>'])

    def test_mixed_events_ordering_with_the_same_dates(self):
        """
        If date of the tournaments are the same, the newest added should be on top
        """
        unseeded_ruleset = create_ruleset('unseeded')
        create_tournament('Unseeded Tourney 1', '2018-10-08', unseeded_ruleset)
        create_tournament('Unseeded Tourney 2', '2018-10-08', unseeded_ruleset)
        create_tournament('Unseeded Tourney 3', '2018-10-08', unseeded_ruleset)
        create_tournament('Unseeded Tourney 4', '2018-10-08', unseeded_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mixed_events'],
                                 ['<Tournament: Unseeded Tourney 4>', '<Tournament: Unseeded Tourney 3>',
                                  '<Tournament: Unseeded Tourney 2>', '<Tournament: Unseeded Tourney 1>'])

    def test_seeded_events_ordering_with_the_same_dates(self):
        """
        If date of the tournaments are the same, the newest added should be on top
        """
        seeded_ruleset = create_ruleset('seeded')
        create_tournament('Seeded Tourney 1', '2018-10-08', seeded_ruleset)
        create_tournament('Seeded Tourney 2', '2018-10-08', seeded_ruleset)
        create_tournament('Seeded Tourney 3', '2018-10-08', seeded_ruleset)
        create_tournament('Seeded Tourney 4', '2018-10-08', seeded_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['seeded_events'],
                                 ['<Tournament: Seeded Tourney 4>', '<Tournament: Seeded Tourney 3>',
                                  '<Tournament: Seeded Tourney 2>', '<Tournament: Seeded Tourney 1>'])

    def test_unseeded_events_ordering_with_the_same_dates(self):
        """
        If date of the tournaments are the same, the newest added should be on top
        """
        unseeded_ruleset = create_ruleset('unseeded')
        create_tournament('Unseeded Tourney 1', '2018-10-08', unseeded_ruleset)
        create_tournament('Unseeded Tourney 2', '2018-10-08', unseeded_ruleset)
        create_tournament('Unseeded Tourney 3', '2018-10-08', unseeded_ruleset)
        create_tournament('Unseeded Tourney 4', '2018-10-08', unseeded_ruleset)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['unseeded_events'],
                                 ['<Tournament: Unseeded Tourney 4>', '<Tournament: Unseeded Tourney 3>',
                                  '<Tournament: Unseeded Tourney 2>', '<Tournament: Unseeded Tourney 1>'])


class AjaxLeaderboardsViewTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_seeded_leaderboard_with_no_entries(self):
        response = self.client.get(reverse('get_leaderboard', args=['seeded']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': []})

    def test_mixed_leaderboard_with_no_entries(self):
        response = self.client.get(reverse('get_leaderboard', args=['mixed']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': []})

    def test_unseeded_leaderboard_with_no_entries(self):
        response = self.client.get(reverse('get_leaderboard', args=['unseeded']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': []})

    def test_seeded_leaderboard_with_entry(self):
        create_leaderboard_entry(leaderboard_type='seeded', place=1, player_name='Player_1', exposure=15,
                                 tournaments_played=1,
                                 matches_played=1)
        response = self.client.get(reverse('get_leaderboard', args=['seeded']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': [{'placement': 1,
                                                          'player__name': 'Player_1',
                                                          'exposure': 15,
                                                          'tournaments_played': 1,
                                                          'matches_played': 1}]})

    def test_mixed_leaderboard_with_entry(self):
        create_leaderboard_entry(leaderboard_type='mixed', place=1, player_name='Player_1', exposure=15,
                                 tournaments_played=1,
                                 matches_played=1)
        response = self.client.get(reverse('get_leaderboard', args=['mixed']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': [{'placement': 1,
                                                          'player__name': 'Player_1',
                                                          'exposure': 15,
                                                          'tournaments_played': 1,
                                                          'matches_played': 1}]})

    def test_unseeded_leaderboard_with_entry(self):
        create_leaderboard_entry(leaderboard_type='unseeded', place=1, player_name='Player_1', exposure=15,
                                 tournaments_played=1,
                                 matches_played=1)
        response = self.client.get(reverse('get_leaderboard', args=['unseeded']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': [{'placement': 1,
                                                          'player__name': 'Player_1',
                                                          'exposure': 15,
                                                          'tournaments_played': 1,
                                                          'matches_played': 1}]})

    def test_seeded_leaderboard_ordering(self):
        """
        Leaderboard should be ordered by placement
        """
        create_leaderboard_entry(leaderboard_type='seeded', place=3, player_name='Player_3', exposure=10,
                                 tournaments_played=3,
                                 matches_played=3)
        create_leaderboard_entry(leaderboard_type='seeded', place=1, player_name='Player_1', exposure=20,
                                 tournaments_played=1,
                                 matches_played=4)
        create_leaderboard_entry(leaderboard_type='seeded', place=2, player_name='Player_2', exposure=15,
                                 tournaments_played=1,
                                 matches_played=1)
        response = self.client.get(reverse('get_leaderboard', args=['seeded']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': [{'placement': 1,
                                                          'player__name': 'Player_1',
                                                          'exposure': 20,
                                                          'tournaments_played': 1,
                                                          'matches_played': 4},
                                                         {'placement': 2,
                                                          'player__name': 'Player_2',
                                                          'exposure': 15,
                                                          'tournaments_played': 1,
                                                          'matches_played': 1},
                                                         {'placement': 3,
                                                          'player__name': 'Player_3',
                                                          'exposure': 10,
                                                          'tournaments_played': 3,
                                                          'matches_played': 3},
                                                         ]})

    def test_mixed_leaderboard_ordering(self):
        """
        Leaderboard should be ordered by placement
        """
        create_leaderboard_entry(leaderboard_type='mixed', place=3, player_name='Player_3', exposure=10,
                                 tournaments_played=3,
                                 matches_played=3)
        create_leaderboard_entry(leaderboard_type='mixed', place=1, player_name='Player_1', exposure=20,
                                 tournaments_played=1,
                                 matches_played=4)
        create_leaderboard_entry(leaderboard_type='mixed', place=2, player_name='Player_2', exposure=15,
                                 tournaments_played=1,
                                 matches_played=1)
        response = self.client.get(reverse('get_leaderboard', args=['mixed']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': [{'placement': 1,
                                                          'player__name': 'Player_1',
                                                          'exposure': 20,
                                                          'tournaments_played': 1,
                                                          'matches_played': 4},
                                                         {'placement': 2,
                                                          'player__name': 'Player_2',
                                                          'exposure': 15,
                                                          'tournaments_played': 1,
                                                          'matches_played': 1},
                                                         {'placement': 3,
                                                          'player__name': 'Player_3',
                                                          'exposure': 10,
                                                          'tournaments_played': 3,
                                                          'matches_played': 3},
                                                         ]})

    def test_unseeded_leaderboard_ordering(self):
        """
        Leaderboard should be ordered by placement
        """
        create_leaderboard_entry(leaderboard_type='unseeded', place=3, player_name='Player_3', exposure=10,
                                 tournaments_played=3,
                                 matches_played=3)
        create_leaderboard_entry(leaderboard_type='unseeded', place=1, player_name='Player_1', exposure=20,
                                 tournaments_played=1,
                                 matches_played=4)
        create_leaderboard_entry(leaderboard_type='unseeded', place=2, player_name='Player_2', exposure=15,
                                 tournaments_played=1,
                                 matches_played=1)
        response = self.client.get(reverse('get_leaderboard', args=['unseeded']))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': [{'placement': 1,
                                                          'player__name': 'Player_1',
                                                          'exposure': 20,
                                                          'tournaments_played': 1,
                                                          'matches_played': 4},
                                                         {'placement': 2,
                                                          'player__name': 'Player_2',
                                                          'exposure': 15,
                                                          'tournaments_played': 1,
                                                          'matches_played': 1},
                                                         {'placement': 3,
                                                          'player__name': 'Player_3',
                                                          'exposure': 10,
                                                          'tournaments_played': 3,
                                                          'matches_played': 3},
                                                         ]})
