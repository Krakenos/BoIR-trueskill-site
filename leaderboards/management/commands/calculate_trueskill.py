from django.core.management.base import BaseCommand
from leaderboards.trueskill_scripts.trueskill_calculation import TrueskillCalculations


class Command(BaseCommand):
    help = 'test command'

    def handle(self, *args, **options):
        TrueskillCalculations().create_leaderboards()

