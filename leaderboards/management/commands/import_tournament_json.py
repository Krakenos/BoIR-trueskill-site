from django.core.management.base import BaseCommand, CommandError
import leaderboards.models
import json
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Imports tournament json into database'

    def add_arguments(self, parser):
        parser.add_argument('tourney_name', nargs='+', type=str)

    def handle(self, *args, **options):
        for file_name in options['tourney_name']:
            try:
                with open(os.path.join(settings.BASE_DIR,
                                       'leaderboards/tournament_jsons',
                                       file_name)) as tournament_json:
                    tournament_data = json.load(tournament_json)
            except FileNotFoundError:
                raise CommandError('File "%s" not found' % file_name)
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
        for match in tournament_data['matchups']:
            match_winner = self.check_player_in_db(match['winner'])
            match_loser = self.check_player_in_db(match['loser'])
            db_match = new_tournament.match_set.create(winner=match_winner,
                                                       loser=match_loser,
                                                       score=match['score'])
            if 'description' in match:
                db_match.description = match['description']
            if 'ruleset' in match:
                db_match.ruleset = leaderboards.models.Ruleset.objects.get_or_create(
                    ruleset=match['ruleset'])[0]
            db_match.save()
        new_tournament.save(create_leaderboards=True)
        self.stdout.write(self.style.SUCCESS(f"Successfully added {tournament_data['name']} tournament"))

    def check_player_in_db(self, player_name):
        if leaderboards.models.PlayerAlias.objects.filter(alias=player_name.lower()).exists():
            pass
        else:
            self.new_player_prompt(player_name)
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
