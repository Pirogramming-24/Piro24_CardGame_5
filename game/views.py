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
from django.urls import reverse
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
    user = request.user

    matches = (
        Game.objects
        .select_related("attacker", "defender")
        .filter(Q(attacker=user) | Q(defender=user))
        .order_by("-id")
    )

    rows = []
    for m in matches:
        # 상태 텍스트만 결정
        if m.status == Game.Status.PENDING:
            if m.defender_id == user.id and m.defender_card is None:
                state_text = "반격하기"
            else:
                state_text = "진행중"

        elif m.status == Game.Status.FINISHED:
            if m.result == Game.Result.DRAW:
                state_text = "DRAW"
            else:
                user_win = (
                    (m.result == Game.Result.ATTACKER_WIN and m.attacker_id == user.id) or
                    (m.result == Game.Result.DEFENDER_WIN and m.defender_id == user.id)
                )
                state_text = "WIN" if user_win else "LOSE"
        else:
            state_text = "취소됨"

        rows.append({
            "id": m.id,
            "attacker": m.attacker.username.upper(),
            "defender": m.defender.username.upper(),
            "state_text": state_text,
        })

    return render(request, "game/match_list.html", {"rows": rows})



@login_required
def new_match(request: HttpRequest) -> HttpResponse:
    User = get_user_model()

    if request.method == "GET":
        candidates = User.objects.exclude(id=request.user.id).order_by("username")
        return render(request, "game/match.html", {"mode": "NEW", "candidates": candidates})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    defender_id = request.POST.get("defender_id")
    if not defender_id:
        return HttpResponseBadRequest("defender_id가 필요합니다.")

    defender = get_object_or_404(User, id=defender_id)
    if defender == request.user:
        return HttpResponseBadRequest("자기 자신에게는 공격할 수 없습니다.")

    # ✅ 여기서는 카드 선택/뽑기 안 함 (메인 로직에서 처리)
    game = Game.objects.create(
        attacker=request.user,
        defender=defender,
        status=Game.Status.PENDING,
        rule=_random_rule(),          # 룰은 생성 시 고정해도 되고, play에서 정해도 됨
    )

    # ✅ 카드 뽑기(메인 로직)로 연결만
    return redirect("game:play", match_id=game.id)


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
    game = get_object_or_404(Game, id=match_id)

    # 수비자만 반격 시작 가능
    if game.defender != request.user:
        messages.error(request, "수비자만 반격할 수 있습니다.")
        return redirect("game:detail", match_id=match_id)

    # 반격 전(PENDING)만
    if game.status != Game.Status.PENDING or game.defender_card is not None:
        messages.error(request, "이미 반격이 완료되었거나 종료된 게임입니다.")
        return redirect("game:detail", match_id=match_id)

    # COUNTER 상태를 DB에 저장하지 않고, 화면 표시만 세션으로 처리
    request.session[_counter_session_key(match_id)] = True
    return redirect("game:detail", match_id=match_id)


@login_required
def counter_start(request: HttpRequest, match_id: int) -> HttpResponse:
    game = get_object_or_404(Game, id=match_id)

    if game.defender != request.user:
        messages.error(request, "수비자만 반격할 수 있습니다.")
        return redirect("game:detail", match_id=match_id)

    if game.status != Game.Status.PENDING or game.defender_card is not None:
        messages.error(request, "이미 반격이 완료되었거나 종료된 게임입니다.")
        return redirect("game:detail", match_id=match_id)

    return render(
        request,
        "game/match.html",
        {
            "mode": "COUNTER",
            "match": game,
            "hand": game.defender_hand,  # COUNTER에서 카드 5장 보여주려면 이거 넘겨야 함
        },
    )


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