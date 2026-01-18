from django.urls import path
from . import views
from .views import playing_view

app_name = "game"

urlpatterns = [
    path("", views.game_list, name="list"),
    path("attack/", views.attack, name="attack"),
    path("<int:game_id>/", views.detail, name="detail"),
    path("<int:game_id>/counter/", views.counter, name="counter"),
    path("<int:game_id>/cancel/", views.cancel, name="cancel"),
    path("playing/", playing_view, name="playing"),
    path("playing/<int:game_id>/", views.counter_playing, name="counter_playing"),
]
