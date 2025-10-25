from django.urls import path
from .views import generate_game, list_games, play_game

urlpatterns = [
    path('generate/', generate_game, name='generate-game'),
    path('', list_games, name='list-games'),
    path('<uuid:game_id>/play/', play_game, name='play-game'),
]