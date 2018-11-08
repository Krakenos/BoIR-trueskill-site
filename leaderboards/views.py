from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
from .models import Leaderboard, Tournament
from django.db.models import Q


@cache_page(60 * 15)
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


@cache_page(60 * 15)
def get_leaderboard(request, leaderboard_type):
    queryset_object = Leaderboard.objects.select_related('player__id').filter(
        leaderboard_type=leaderboard_type)
    leaderboard_list = list(
        queryset_object.values('placement', 'player__name', 'exposure', 'tournaments_played', 'matches_played'))
    data = {
        'data': leaderboard_list
    }
    return JsonResponse(data)


def get_ratings(request, rating_type):
    leaderboards = Leaderboard.objects.select_related('player__name')
    querydict = leaderboards.filter(leaderboard_type=rating_type).values('player__name', 'mu', 'sigma')
    player_data = {
        p['player__name']: {'mu': p['mu'], 'sigma': p['sigma']} for p in querydict
    }
    return JsonResponse({'data': player_data})
