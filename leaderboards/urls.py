from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/leaderboards/<str:leaderboard_type>', views.get_leaderboard, name='get_leaderboard')
]
