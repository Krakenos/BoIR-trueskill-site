import trueskill
from leaderboards.models import Tournament


class TrueskillCalculations:
    tournament_limit = 2  # Hides people who played low amount of tourneys from the leaderboards
    seeded_multiplier = 4
    mixed_multiplier = 2

    def create_leaderboards(self):
        for tournament in Tournament.objects.all().order_by('date'):
            if tournament.ruleset == 'other':
                continue
            elif tournament.ruleset == 'seeded':
                for _ in range(self.seeded_multiplier):
                    continue
            elif tournament.ruleset == 'mixed':
                for _ in range(self.mixed_multiplier):
                    continue
            elif tournament.ruleset == 'multiple':
                continue
            else:
                continue
