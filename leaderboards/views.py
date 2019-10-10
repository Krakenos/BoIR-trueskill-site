import datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from .models import Leaderboard, Tournament


#@cache_page(60 * 15)
def index(request):
    context = {
        'mixed_events': Tournament.objects.filter(~Q(ruleset__ruleset='other') & ~Q(ruleset__ruleset='team')).order_by(
            '-date', '-id'),
        'seeded_events': Tournament.objects.filter(
            Q(ruleset__ruleset='seeded') | Q(ruleset__ruleset='multiple')).order_by(
            '-date', '-id'),
        'unseeded_events': Tournament.objects.filter(
            ~Q(ruleset__ruleset='other') & ~Q(ruleset__ruleset='team') & ~Q(ruleset__ruleset='seeded')).order_by(
            '-date', '-id')
    }
    return render(request, 'leaderboards/index.html', context)


#@cache_page(60 * 15)
def get_leaderboard(request, leaderboard_type):
    if leaderboard_type not in ['seeded', 'unseeded', 'mixed']:
        raise Http404("This leaderboard doesn't exist")

    # Get the leaderboard from the database and make it a list
    queryset_object = Leaderboard.objects.select_related('player__id').filter(
        leaderboard_type=leaderboard_type)
    leaderboard_list = list(
        queryset_object.values('player__name', 'player__last_played', 'exposure', 'tournaments_played', 'matches_played'))

    # Add an entry for adjusted exposure
    # (we want the rating to decay for players who have not played in a tournament for a while)
    days_inactive_threshold = 365  # 1 year
    total_decay_days = 4 * 365 + 1  # 4 years (we add 1 because of a leap year)
    todays_date = datetime.date.today()
    for entry in leaderboard_list:

        # Calculate the time differential between the last tournament played and now
        differential = todays_date - entry['player__last_played']
        days_since_last_tournament = differential.days

        # Decay only applies if they have not played in a tournament for a while
        decay = 0
        adjusted_exposure = entry['exposure']
        if days_since_last_tournament >= days_inactive_threshold:
            penalty = days_since_last_tournament / total_decay_days
            decay = entry['exposure'] * penalty
            adjusted_exposure = entry['exposure'] - decay

        # Add entries for decay and adjusted_exposure
        entry['decay'] = decay
        entry['adjusted_exposure'] = adjusted_exposure

    # Re-sort the leaderboard list based on the new adjusted exposure
    def sort_adjusted_exposure(leaderboard):
        return leaderboard['adjusted_exposure']
    leaderboard_list.sort(key=sort_adjusted_exposure, reverse=True)

    # Add a value for place
    place = 1
    for entry in leaderboard_list:
        entry['place'] = place
        place += 1

    # Return the data
    return JsonResponse({
        'data': leaderboard_list,
    })


# This is meant to be used by bots that need up-to-date rating information
def get_ratings(request, rating_type):
    if rating_type not in ['seeded', 'unseeded', 'mixed']:
        raise Http404("This rating type doesn't exist")

    leaderboards = Leaderboard.objects.select_related('player__name')
    querydict = leaderboards.filter(leaderboard_type=rating_type).values('player__name', 'mu', 'sigma')
    player_data = {
        p['player__name']: {'mu': p['mu'], 'sigma': p['sigma']} for p in querydict
    }
    return JsonResponse({
        'data': player_data,
    })
