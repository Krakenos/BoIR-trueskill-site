from django.core.management.base import BaseCommand
import leaderboards.models
import json
from django.conf import settings
import os
import glob
from leaderboards.trueskill_scripts.trueskill_calculation import TrueskillCalculations
from django.contrib.auth.models import User
import string
import random


class Command(BaseCommand):
    help = 'Imports tournament json into database'

    def add_arguments(self, parser):
        parser.add_argument('tourney_name', nargs='+', type=str)
        parser.add_argument('--bulk',
                            action='store_true',
                            dest='bulk',
                            help='Imports all the jsons from tournament_jsons folder')
        parser.add_argument('--verify',
                            action='store_true',
                            dest='verification',
                            help='Allows manual players verification, before adding them into database')
        parser.add_argument('--adduser',
                            action='store_true',
                            dest='add_user',
                            help='Adds tournament organizers into database as users')

    def handle(self, *args, **options):
        if options['bulk']:
            for infile in sorted(
                    glob.glob(os.path.join(settings.BASE_DIR, 'leaderboards', 'tournament_jsons', '*.json'))):
                with open(infile) as tournament_json:
                    tournament_data = json.load(tournament_json)
                self.add_tournament(tournament_data, options)
            self.stdout.write(self.style.SUCCESS('Successfully added all tournaments'))
        else:
            for file_name in options['tourney_name']:
                try:
                    with open(os.path.join(settings.BASE_DIR,
                                           'leaderboards', 'tournament_jsons',
                                           file_name)) as tournament_json:
                        tournament_data = json.load(tournament_json)
                except FileNotFoundError:
                    self.stdout.write(f"File {options['tourney_name']} not found")
                    continue
                self.add_tournament(tournament_data, options)
        self.stdout.write('Calculating trueskill...')
        TrueskillCalculations(tournament_model=leaderboards.models.Tournament,
                              leaderboard_model=leaderboards.models.Leaderboard,
                              player_model=leaderboards.models.Player).create_leaderboards()

    def add_tournament(self, tournament_data, options):
        new_tournament = leaderboards.models.Tournament(
            name=tournament_data['name'],
            challonge_id=tournament_data['challonge_id'],
            challonge_url=tournament_data['challonge'],
            date=tournament_data['date'],
            notability=tournament_data['notability'],
            ruleset=leaderboards.models.Ruleset.objects.get_or_create(ruleset=tournament_data['ruleset'])[0],
            description=tournament_data['description']
        )
        new_tournament.save()
        if options['add_user']:
            self.add_user(tournament_data, new_tournament)
        for match in tournament_data['matchups']:
            match_winner = self.check_player_in_db(match['winner'], options)
            match_loser = self.check_player_in_db(match['loser'], options)
            db_match = new_tournament.match_set.create(winner=match_winner,
                                                       loser=match_loser,
                                                       score=match['score'])
            if 'description' in match:
                db_match.description = match['description']
            if 'ruleset' in match:
                db_match.ruleset = leaderboards.models.Ruleset.objects.get_or_create(
                    ruleset=match['ruleset'])[0]
            db_match.save()
        new_tournament.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully added {tournament_data['name']} tournament"))

    def add_user(self, tournament_data, tournament):
        for organizer in tournament_data['organizer']:
            tournament_organizer = self.get_or_create_user(organizer)
            tournament.organizers.add(tournament_organizer)
        tournament.save()

    @staticmethod
    def get_or_create_user(name):
        try:
            tournament_organizer = User.objects.get(username=name)
        except User.DoesNotExist:
            tournament_organizer = User.objects.create_user(username=name, password=''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)))  # random pass
            tournament_organizer.is_staff = False
            tournament_organizer.is_superuser = False
        return tournament_organizer

    def check_player_in_db(self, player_name, options):
        if leaderboards.models.PlayerAlias.objects.filter(alias=player_name.lower()).exists():
            pass
        else:
            if options['verification']:
                self.new_player_prompt(player_name)
            else:
                new_player = leaderboards.models.Player.objects.create(name=player_name)
                new_player.playeralias_set.create(alias=player_name.lower())
                new_player.save()
        return leaderboards.models.Player.objects.get(playeralias__alias=player_name.lower())

    def new_player_prompt(self, player_name):
        self.stdout.write('Players in the database:')
        for player in leaderboards.models.Player.objects.all():
            self.stdout.write(f'{player.pk}. {player.name}')
        self.stdout.write(f'Couldn\'t find player {player_name} in the database. Do you want to add an alias to '
                          'existing player? If no new player is going to be added into database')
        user_input = 'x'
        while user_input not in 'yYnN':
            user_input = input('(y/n):')
        if user_input in 'nN':
            new_player = leaderboards.models.Player.objects.create(name=player_name)
            new_player.playeralias_set.create(alias=player_name.lower())
            new_player.save()
            self.stdout.write(self.style.SUCCESS('Successfully added new player into database'))
        else:
            chosen_pk = input('Choose a player by typing in his number:')
            chosen_player = leaderboards.models.Player.objects.get(pk=chosen_pk)
            chosen_player.playeralias_set.create(alias=player_name.lower())
            chosen_player.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully added new alias for {chosen_player}'))
