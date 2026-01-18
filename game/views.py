from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Game


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
