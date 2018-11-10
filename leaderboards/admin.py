from django.contrib import admin
from .models import *
from django.apps import apps

app = apps.get_app_config('leaderboards')

for model_name, model in app.models.items():
    admin.site.register(model)

admin.site.unregister(Tournament)


class TournamentVodInLine(admin.TabularInline):
    model = Vod
    fields = ['url', 'description']


class MatchInLine(admin.StackedInline):
    model = Match
    raw_id_fields = ('winner', 'loser', 'winner_team', 'loser_team')


class TournamentAdmin(admin.ModelAdmin):
    class Media:
        js = ('/static/admin/js/hide_team_fields.js',)

    inlines = [TournamentVodInLine, MatchInLine]


admin.site.register(Tournament, TournamentAdmin)
