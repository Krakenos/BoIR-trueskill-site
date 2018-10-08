import json
import requests
import os
import dotenv

dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))  # Loading .env
api_key = os.environ.get('API_KEY')


def main():
    while True:
        print('Type q to exit')
        tourney_id = input('enter the tournament id:')
        if tourney_id == 'q':
            break

        # Getting the data through challonge api
        tourney = requests.get('https://api.challonge.com/v1/tournaments/' + tourney_id + '.json',
                               params={'api_key': api_key, 'include_participants': 1, 'include_matches': 1}).json()
        tourney_data = tourney['tournament']
        date = tourney_data['started_at'].split('T', 1)[0]  # YYYY-MM-DD
        json_var = json_parser(tourney_data, tourney_id, date)
        print(json_var)
        with open('tournaments/' + date + ' ' + ''.join(e for e in tourney_data['name']
                                                        if e not in '/\\?*"<>|:') + '.json', 'w') as data_file:
            json.dump(json_var, data_file, indent=2)


def json_parser(tournament, t_id, date):
    date_array = date.split('-', 2)
    matches = tournament['matches']
    participants = tournament['participants']
    parsed_json = {'name': tournament['name'],
                   'challonge_id': t_id,
                   'challonge': tournament['full_challonge_url'],
                   'date': date_array[2] + '-' + date_array[1] + '-' + date_array[0],
                   'notability': 'minor',
                   'organizer': '',
                   'ruleset': '',
                   'description': '',
                   'videos': [],
                   'matchups': []
                   }
    for match in matches:
        match_data = match['match']

        # If there is no winner in match up we want the score to be a draw
        if match_data['winner_id'] is None:
            parsed_json['matchups'].append({'winner': match_data['player1_id'],
                                            'loser': match_data['player2_id'],
                                            'score': 'draw'})

        # If there is a winner, we get the score
        else:
            scores = match_data['scores_csv'].split('-')
            scores.sort(reverse=True)
            try:
                match_score = scores[0] + '-' + scores[1]
            except IndexError:
                match_score = '3-0'   # scenario where match is forfeited
            parsed_json['matchups'].append({'winner': match_data['winner_id'],
                                            'loser': match_data['loser_id'],
                                            'score': match_score})

    # Looping through participants to get their id
    for participant in participants:
        participant_id = participant['participant']['id']
        participant_group_id = participant['participant']['group_player_ids']
        participant_name = participant['participant']['name']
        if participant_name == '':  # Sometimes name is empty because it's tied to challonge account
            participant_name = participant['participant']['challonge_username']
        # Replacing id's with player names in the parsed_json
        for match in parsed_json['matchups']:
            winner = match['winner']
            loser = match['loser']
            if winner == participant_id or winner in participant_group_id:
                match['winner'] = participant_name
            if loser == participant_id or loser in participant_group_id:
                match['loser'] = participant_name
    print('json parsed successfully')
    return parsed_json


if __name__ == '__main__':
    main()
