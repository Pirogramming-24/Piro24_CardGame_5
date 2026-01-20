from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    # 로그인 후 메인: NEW MATCH / LIST
    path("", views.home, name="home"),

    # 리스트
    path("matches/", views.match_list, name="list"),

    # NEW MATCH (match.html NEW)
    path("new/", views.new_match, name="new"),

    # 결과/상세 (match_result.html) - WAITING/FINISHED/COUNTER
    path("matches/<int:match_id>/", views.match_result, name="detail"),

    # 반격하기: match_result.html#counter 느낌(= COUNTER 상태 표시)
    path("matches/<int:match_id>/counter/", views.counter_prompt, name="counter_prompt"),

    # 카운터어택 버튼 누르면: match.html COUNTER
    path("matches/<int:match_id>/counter/start/", views.counter_start, name="counter_start"),

    # 카드 뽑기(playing)
    path("matches/<int:match_id>/play/", views.play, name="play"),

    # 취소(진행중일 때만)
    path("matches/<int:match_id>/cancel/", views.cancel_match, name="cancel"),
]
