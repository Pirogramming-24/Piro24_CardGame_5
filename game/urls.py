from django.urls import path
from . import views

urlpatterns = [
    path("", views.game_list, name="list"),
    path("attack/", views.attack, name="attack"),
    path("<int:game_id>/", views.detail, name="detail"),
    path("<int:game_id>/counter/", views.counter, name="counter"),
    path("<int:game_id>/cancel/", views.cancel, name="cancel"),
]
