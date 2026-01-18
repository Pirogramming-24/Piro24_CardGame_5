from django.contrib import admin
from django.urls import path, include

from config import views as config_views
from accounts import views as accounts_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # allauth (소셜 로그인)
    path("accounts/", include("allauth.urls")),

    # 로그인 전 메인 (landing)
    path("", config_views.home, name="home"),

    # 랭킹
    path("ranking/", accounts_views.ranking, name="ranking"),

    # 게임
    path("game/", include(("game.urls", "game"), namespace="game")),
]
