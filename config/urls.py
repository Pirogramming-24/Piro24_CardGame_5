from django.contrib import admin
from django.urls import path, include
from config import views as config_views
from accounts import views as accounts_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # allauth
    path("accounts/", include("allauth.urls")),

    # home
    path("", config_views.home, name="home"),

    # ranking
    path("ranking/", accounts_views.ranking, name="ranking"),

    # game
    path("game/", include(("game.urls", "game"), namespace="game")),
]
