from dataclasses import dataclass
from enum import Enum
import random
from typing import Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.db.models import Q
from game.models import Game


class MatchStatus(str, Enum):
    WAITING = "WAITING"    # 상대 반격 전 (진행중)
    COUNTER = "COUNTER"    # 반격 진행 중(카운터 플로우 진입)
    FINISHED = "FINISHED"  # 종료


@dataclass
class FakeMatch:
    id: int
    attacker: str
    defender: str
    status: MatchStatus


_FAKE_DB: Dict[int, FakeMatch] = {}
_SEQ = 1


def _draw_hand() -> list[int]:
    return random.sample(range(1, 11), 5)


def _random_rule() -> str:
    return random.choice([Game.Rule.HIGH_WINS, Game.Rule.LOW_WINS])


@login_required
def home(request: HttpRequest) -> HttpResponse:
    # 로그인 후 메인 (NEW / LIST 버튼)
    return render(request, "game/main_logged_in.html")


@login_required
def match_list(request: HttpRequest) -> HttpResponse:
    """
    📋 내 게임 리스트
    """
    user = request.user
    matches = (
        Game.objects
        .filter(Q(attacker=user) | Q(defender=user))
        .order_by("-id")
    )
    return render(request, "game/match_list.html", {"matches": matches})


@login_required
def new_match(request: HttpRequest) -> HttpResponse:
    """
    🎮 게임 생성 (공격)
    """
    User = get_user_model()

    if request.method == "GET":
        hand = _draw_hand()
        request.session["new_match_hand"] = hand

        candidates = User.objects.exclude(id=request.user.id)

        return render(
            request,
            "game/match.html",
            {
                "mode": "NEW",
                "hand": hand,
                "candidates": candidates,
            },
        )

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    defender_id = request.POST.get("defender_id")
    attacker_card_raw = request.POST.get("attacker_card")

    if not defender_id or not attacker_card_raw:
        return HttpResponseBadRequest("필수 값이 누락되었습니다.")

    try:
        attacker_card = int(attacker_card_raw)
    except ValueError:
        return HttpResponseBadRequest("카드는 숫자여야 합니다.")

    hand = request.session.get("new_match_hand", [])
    if attacker_card not in hand:
        messages.error(request, "유효하지 않은 카드입니다.")
        return redirect("game:new")

    defender = get_object_or_404(User, id=defender_id)

    Game.objects.create(
        attacker=request.user,
        defender=defender,
        status=Game.Status.PENDING,
        rule=_random_rule(),
        attacker_hand=hand,
        defender_hand=_draw_hand(),
        attacker_card=attacker_card,
    )

    request.session.pop("new_match_hand", None)

    return redirect("game:list")


@login_required
def match_result(request: HttpRequest, match_id: int) -> HttpResponse:
    m = _FAKE_DB.get(match_id)
    if not m:
        messages.error(request, "게임을 찾을 수 없습니다.")
        return redirect("game:home")

    # 템플릿에서 WAITING/FINISHED/COUNTER 분기 가능하도록 state 제공
    return render(request, "game/match_result.html", {"match": m, "state": m.status})


@login_required
def counter_prompt(request: HttpRequest, match_id: int) -> HttpResponse:
    """
    리스트에서 '반격하기' 눌렀을 때:
    match_result.html#counter 느낌 = COUNTER 상태 화면(카운터어택 버튼 활성화)
    """
    m = _FAKE_DB.get(match_id)
    if not m:
        messages.error(request, "게임을 찾을 수 없습니다.")
        return redirect("game:home")

    # 임시로 상태 COUNTER로 바꿈
    m.status = MatchStatus.COUNTER
    return render(request, "game/match_result.html", {"match": m, "state": MatchStatus.COUNTER})


@login_required
def counter_start(request: HttpRequest, match_id: int) -> HttpResponse:
    """
    match_result COUNTER 화면에서 '카운터어택' 버튼 누르면:
    match.html COUNTER 모드(카드 뽑기 버튼 활성화)
    """
    m = _FAKE_DB.get(match_id)
    if not m:
        messages.error(request, "게임을 찾을 수 없습니다.")
        return redirect("game:home")

    return render(request, "game/match.html", {"mode": "COUNTER", "match": m})


@login_required
def play(request: HttpRequest, match_id: int) -> HttpResponse:
    """
    카드 뽑기 눌렀을 때 playing.html
    (임시: 결과 계산 안 함)
    """
    m = _FAKE_DB.get(match_id)
    if not m:
        messages.error(request, "게임을 찾을 수 없습니다.")
        return redirect("game:home")

    return render(request, "game/playing.html", {"match": m})


@login_required
def cancel_match(request: HttpRequest, match_id: int) -> HttpResponse:
    """
    ❌ 게임 취소 (공격자 + 진행중만)
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    game = get_object_or_404(Game, id=match_id)

    if game.attacker != request.user:
        messages.error(request, "공격자만 취소할 수 있습니다.")
        return redirect("game:list")

    if game.status != Game.Status.PENDING:
        messages.error(request, "진행중인 게임만 취소할 수 있습니다.")
        return redirect("game:list")

    game.status = Game.Status.CANCELLED
    game.save(update_fields=["status", "updated_at"])

    messages.success(request, "게임을 취소했습니다.")
    return redirect("game:list")