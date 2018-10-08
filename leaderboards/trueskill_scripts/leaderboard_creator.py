import json
import glob
from collections import defaultdict
from trueskill import Rating, rate_1vs1

debug = False  # Changing to True will cause printing out exposure change for each match up
current_file = ''  # Global variable to track which file is being processed, used in name_check function
calculate_per_round = False
tournament_limit = 2  # Hides people who played low amount of tourneys from the leaderboards
seeded_multiplier = 4


def main():
    racers = defaultdict(dict)
    seeded_racers = defaultdict(dict)
    unseeded_racers = defaultdict(dict)

    # Looping through every file in the tournaments folder
    for infile in sorted(glob.glob('tournaments/*.json')):
        players_in_all_tourneys = []
        players_in_seeded_tourneys = []  # Variables to keep track of players participation in a tourney
        players_in_unseeded_tourneys = []
        global current_file
        current_file = infile
        with open(infile) as datafile:
            tournament_data = json.load(datafile)
        race_list = tournament_data['matchups']

        # Looping through every race in the tournament
        for race in race_list:
            if tournament_data['ruleset'] == 'seeded':
                check_racer(race, racers)
                check_racer(race, seeded_racers)
                increment_tourney_played(race, racers, players_in_all_tourneys)
                increment_tourney_played(race, seeded_racers, players_in_seeded_tourneys)
                increment_match_played(race, racers)
                increment_match_played(race, seeded_racers)
                if debug:
                    print('seeded')
                for i in range(seeded_multiplier):
                    if calculate_per_round is True:
                        mmr_per_round(race, racers, False)
                    else:
                        calculate_mmr(race, racers)
                if calculate_per_round is True:
                    mmr_per_round(race, seeded_racers, False)
                else:
                    calculate_mmr(race, seeded_racers)
            elif tournament_data['ruleset'] == 'mixed':
                check_racer(race, racers)
                check_racer(race, unseeded_racers)
                increment_tourney_played(race, racers, players_in_all_tourneys)
                increment_tourney_played(race, unseeded_racers, players_in_unseeded_tourneys)
                increment_match_played(race, racers)
                increment_match_played(race, unseeded_racers)
                if debug:
                    print('mixed')
                if calculate_per_round is True:
                    mmr_per_round(race, racers, True)
                else:
                    for i in range(2):
                        calculate_mmr(race, racers)
                    calculate_mmr(race, unseeded_racers)

            elif tournament_data['ruleset'] == 'multiple':
                if debug:
                    print('multiple')
                if race['ruleset'] == 'seeded':
                    check_racer(race, racers)
                    check_racer(race, seeded_racers)
                    increment_tourney_played(race, racers, players_in_all_tourneys)
                    increment_tourney_played(race, seeded_racers, players_in_seeded_tourneys)
                    increment_match_played(race, racers)
                    increment_match_played(race, seeded_racers)
                    for i in range(seeded_multiplier):
                        if calculate_per_round is True:
                            mmr_per_round(race, racers, False)
                        else:
                            calculate_mmr(race, racers)
                    if calculate_per_round is True:
                        mmr_per_round(race, seeded_racers, False)
                    else:
                        calculate_mmr(race, seeded_racers)
                else:
                    check_racer(race, racers)
                    check_racer(race, unseeded_racers)
                    increment_tourney_played(race, racers, players_in_all_tourneys)
                    increment_tourney_played(race, unseeded_racers, players_in_unseeded_tourneys)
                    increment_match_played(race, racers)
                    increment_match_played(race, unseeded_racers)
                    if debug:
                        print('unseeded')
                    if calculate_per_round is True:
                        mmr_per_round(race, racers, False)
                        mmr_per_round(race, unseeded_racers, False)
                    else:
                        calculate_mmr(race, racers)
                        calculate_mmr(race, unseeded_racers)

            elif tournament_data['ruleset'] == 'other':
                continue
            else:
                check_racer(race, racers)
                check_racer(race, unseeded_racers)
                increment_tourney_played(race, racers, players_in_all_tourneys)
                increment_tourney_played(race, unseeded_racers, players_in_unseeded_tourneys)
                increment_match_played(race, racers)
                increment_match_played(race, unseeded_racers)
                if debug:
                    print('unseeded')
                if calculate_per_round is True:
                    mmr_per_round(race, racers, False)
                    mmr_per_round(race, unseeded_racers, False)
                else:
                    calculate_mmr(race, racers)
                    calculate_mmr(race, unseeded_racers)

    mixed_leaderboard = calculate_places(racers)
    seeded_leaderboard = calculate_places(seeded_racers)
    unseeded_leaderboard = calculate_places(unseeded_racers)
    dump_json('leaderboards/mixed_leaderboard.json', mixed_leaderboard)
    dump_json('leaderboards/seeded_leaderboard.json', seeded_leaderboard)
    dump_json('leaderboards/unseeded_leaderboard.json', unseeded_leaderboard)
    print_leaderboard(mixed_leaderboard)


def increment_tourney_played(matchup, racers_dict, tourney_players):
    winner = name_check(matchup['winner'], racers_dict)
    loser = name_check(matchup['loser'], racers_dict)
    if winner not in tourney_players:
        tourney_players.append(winner)
        racers_dict[winner]['tournaments_played'] += 1
    if loser not in tourney_players:
        tourney_players.append(loser)
        racers_dict[loser]['tournaments_played'] += 1


def calculate_places(racers_dict):
    # Creating leaderboard, sorting by exposure value
    leaderboards_list = [
        {
            'name': key,
            'tournaments_played': value['tournaments_played'],
            'matches_played': value['matches_played'],
            'exposure': value['rating'].exposure,
            'mu': value['rating'].mu,
            'sigma': value['rating'].sigma
        } for key, value in racers_dict.items() if value['tournaments_played'] >= tournament_limit
    ]
    leaderboards_list.sort(key=lambda x: x['exposure'], reverse=True)
    for place, player in enumerate(leaderboards_list):
        player['place'] = place + 1
    return leaderboards_list


def adjust_trueskill(winner, loser, racers_dict):
    racers_dict[winner]['rating'], racers_dict[loser]['rating'] = \
        rate_1vs1(racers_dict[winner]['rating'], racers_dict[loser]['rating'])


def name_check(name, racers_dict):
    for key, _ in racers_dict.items():
        if name.lower() == key.lower():
            if name != key:
                print(f'WARNING: expected name {key} got {name} in {current_file} file')
            return key
    return name


def check_racer(matchup, racers_dict):
    winner = name_check(matchup['winner'], racers_dict)
    loser = name_check(matchup['loser'], racers_dict)
    if winner not in racers_dict:  # If the person doesn't have existing rating, assign rating of 25
        racers_dict[winner]['rating'] = Rating(25)
        racers_dict[winner]['matches_played'] = 0
        racers_dict[winner]['tournaments_played'] = 0
    if loser not in racers_dict:
        racers_dict[loser]['rating'] = Rating(25)
        racers_dict[loser]['matches_played'] = 0
        racers_dict[loser]['tournaments_played'] = 0


def increment_match_played(matchup, racers_dict):
    winner = name_check(matchup['winner'], racers_dict)
    loser = name_check(matchup['loser'], racers_dict)
    racers_dict[winner]['matches_played'] += 1
    racers_dict[loser]['matches_played'] += 1


def calculate_mmr(matchup, racers_dict):
    winner = name_check(matchup['winner'], racers_dict)
    loser = name_check(matchup['loser'], racers_dict)
    old_exposure_1 = racers_dict[winner]['rating'].exposure  # Variables for debug purpose
    old_exposure_2 = racers_dict[loser]['rating'].exposure

    if not (matchup['score'] == 'draw'):  # We want to ignore draws because they most likely are mistake in the json.
        adjust_trueskill(winner, loser, racers_dict)
    if debug:
        # Printing out every change in the exposure value
        print(winner + ' ' + loser + ' ' + str(racers_dict[winner]['rating'].exposure) + ' ' + str(
            racers_dict[loser]['rating'].exposure) + ' +' + str(
            racers_dict[winner]['rating'].exposure - old_exposure_1) + ' ' + str(
            racers_dict[loser]['rating'].exposure - old_exposure_2))

    return racers_dict


def print_leaderboard(leaderboard_json):
    max_name_length = 0
    for record in leaderboard_json:
        if len(str(record['name'])) > max_name_length:
            max_name_length = len(str(record['name']))
    print('Place  ' + 'Name' + (max_name_length - 2) * ' ' + 'Trueskill')
    print('-' * 6 + '-' * max_name_length + '-' * 12)
    for record in leaderboard_json:
        place = str(record['place'])
        name = record['name']
        exposure = str(round(record['exposure'], 2))
        print('#' + place + (5 - len(place)) * ' ' + ' ' + name + (max_name_length - len(name) + 2) * ' ' + exposure)


def dump_json(filename, data):
    with open(filename, 'w') as output:
        json.dump(data, output, indent=2)


def mmr_per_round(race, racers_dict, mixed_flag=False):
    winner = name_check(race['winner'], racers_dict)
    loser = name_check(race['loser'], racers_dict)
    if race['score'] != 'draw':
        if mixed_flag is False:
            scores = race['score'].split('-')
            for i in range(int(scores[1])):
                adjust_trueskill(loser, winner, racers_dict)
            for i in range(int(scores[0])):
                adjust_trueskill(winner, loser, racers_dict)
        else:
            for round in race['ruleset_per_round']:
                if round['ruleset'] == 'seeded':
                    for i in range(seeded_multiplier):
                        if winner == round['winner']:
                            adjust_trueskill(winner, loser, racers_dict)
                        else:
                            adjust_trueskill(loser, winner, racers_dict)
                else:
                    if winner == round['winner']:
                        adjust_trueskill(winner, loser, racers_dict)
                    else:
                        adjust_trueskill(loser, winner, racers_dict)


if __name__ == '__main__':
    main()
