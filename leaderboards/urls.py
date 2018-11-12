from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/leaderboards/<str:leaderboard_type>', views.get_leaderboard, name='get_leaderboard'),
    path('api/ratings/<str:rating_type>', views.get_ratings, name='get_ratings'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout')
]
