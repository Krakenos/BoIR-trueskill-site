from django.core.management.base import BaseCommand
import leaderboards.models
import json
from django.conf import settings
import glob
import os
from leaderboards.trueskill_scripts.trueskill_calculation import TrueskillCalculations


class Command(BaseCommand):
    help = 'Takes no argument, imports every json from tournament_jsons folder into database, if player doesnt exist ' \
           'he is automatically added into db, this command assumes all the json dumps are correct and is used in the ' \
           'initial db setup '

    def handle(self, *args, **options):
        for infile in sorted(glob.glob(os.path.join(settings.BASE_DIR, 'leaderboards', 'tournament_jsons', '*.json'))):
            with open(infile) as tournament_json:
                tournament_data = json.load(tournament_json)
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
            new_tournament.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully added {tournament_data['name']} tournament"))
        TrueskillCalculations(tournament_model=leaderboards.models.Tournament,
                              leaderboard_model=leaderboards.models.Leaderboard,
                              player_model=leaderboards.models.Player).create_leaderboards()
        self.stdout.write(self.style.SUCCESS(f"Successfully added all tournaments"))

    @staticmethod
    def check_player_in_db(player_name):
        if leaderboards.models.PlayerAlias.objects.filter(alias=player_name.lower()).exists():
            pass
        else:
            new_player = leaderboards.models.Player.objects.create(name=player_name)
            new_player.playeralias_set.create(alias=player_name.lower())
            new_player.save()
        return leaderboards.models.Player.objects.get(playeralias__alias=player_name.lower())

