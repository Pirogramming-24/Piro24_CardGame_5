from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Game
from accounts.models import User
from django.contrib.auth import get_user_model

User = get_user_model()
def playing_view(request):
    # 테스트 단계: 로그인 강제 안 걸고, 후보만 내려줌
    defenders = User.objects.all().order_by("username")
    return render(request, "game/playing.html", {"defenders": defenders})
    # 임시 데이터 (테스트용)
    """"
    defenders = User.objects.exclude(id=request.user.id) if request.user.is_authenticated else []

    context = {
        "mode": "attack",      # or "counter"
        "defenders": defenders,
        "attacker": request.user if request.user.is_authenticated else None,
    }
    return render(request, "game/playing.html", context)
    """



@login_required
def game_list(request):
    # 임시: 나중에 전적 쿼리로 교체
    games = Game.objects.all().order_by("-created_at")
    return render(request, "game/list.html", {"games": games})


@login_required
def attack(request):
    # 임시: 나중에 랜덤 5장 + 상대 선택 + 생성 로직으로 교체
    if request.method == "POST":
        return redirect("game:list")
    return render(request, "game/attack.html")


@login_required
def detail(request, game_id: int):
    game = get_object_or_404(Game, id=game_id)
    return render(request, "game/detail.html", {"game": game})


@login_required
def counter(request, game_id: int):
    game = get_object_or_404(Game, id=game_id)
    # 임시: 나중에 반격 제출 + 결과 계산으로 교체
    if request.method == "POST":
        return redirect("game:detail", game_id=game.id)
    return render(request, "game/counter.html", {"game": game})


@login_required
def cancel(request, game_id: int):
    game = get_object_or_404(Game, id=game_id)
    # 임시: 나중에 "공격자 & PENDING일 때만" 취소 허용 로직으로 교체
    if request.method == "POST":
        return redirect("game:list")
    return redirect("game:detail", game_id=game.id)


@login_required
def playing(request):
    # ATTACKER 화면 (새 매치 생성)
    defenders = User.objects.exclude(id=request.user.id)

    return render(request, "game/playing.html", {
        "mode": "attack",                 # ⭐ 템플릿 분기 핵심
        "defenders": defenders,
    })


@login_required
def counter_playing(request, game_id):
    # DEFENDER 화면 (반격)
    game = get_object_or_404(Game, id=game_id)

    return render(request, "game/playing.html", {
        "mode": "counter",                # ⭐ 분기
        "attacker": game.attacker,        # _match_rolebar.html 에서 사용
        "game": game,
    })
