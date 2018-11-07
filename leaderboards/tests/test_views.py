from django.test import TestCase
from django.urls import reverse
from leaderboards.models import Tournament, Ruleset
from django.core.cache import cache


def create_ruleset(name):
    return Ruleset.objects.create(ruleset=name)


def create_tournament(name, date, ruleset):
    return Tournament.objects.create(name=name, date=date, ruleset=ruleset)


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
