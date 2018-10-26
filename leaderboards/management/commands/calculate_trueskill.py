from django.core.management.base import BaseCommand
from leaderboards.trueskill_scripts.trueskill_calculation import TrueskillCalculations
from leaderboards.models import Tournament, Player, Leaderboard


class Command(BaseCommand):
    help = 'Takes no argument. Recalculates and recreates leaderboards'

    def handle(self, *args, **options):
        TrueskillCalculations(tournament_model=Tournament, player_model=Player,
                              leaderboard_model=Leaderboard).create_leaderboards()

