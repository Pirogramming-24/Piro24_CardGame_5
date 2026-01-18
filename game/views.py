from dataclasses import dataclass
from enum import Enum
from typing import Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render


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


def _next_id() -> int:
    global _SEQ
    v = _SEQ
    _SEQ += 1
    return v


@login_required
def home(request: HttpRequest) -> HttpResponse:
    # 로그인 후 메인: new match / list 버튼만 있어도 됨
    return render(request, "game/main_logged_in.html")


@login_required
def match_list(request: HttpRequest) -> HttpResponse:
    # 임시: 내 관련 매치만 보여주기
    username = request.user.username
    matches = [
        m for m in _FAKE_DB.values()
        if m.attacker == username or m.defender == username
    ]
    matches.sort(key=lambda x: x.id, reverse=True)
    return render(request, "game/match_list.html", {"matches": matches})


@login_required
def new_match(request: HttpRequest) -> HttpResponse:
    # NEW MATCH 화면
    if request.method == "GET":
        return render(request, "game/match.html", {"mode": "NEW"})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    # 임시로 defender 문자열만 받음 (DB 붙이면 User 선택)
    defender = (request.POST.get("defender") or "").strip() or "defender"
    match_id = _next_id()
    _FAKE_DB[match_id] = FakeMatch(
        id=match_id,
        attacker=request.user.username,
        defender=defender,
        status=MatchStatus.WAITING,
    )

    # "카드 뽑기"로 바로 넘어가고 싶으면 play로 리다이렉트
    return redirect("game:play", match_id=match_id)


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
    진행중(WAITING)만 취소 가능
    취소하면 메인으로 가고 게임 삭제
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    m = _FAKE_DB.get(match_id)
    if not m:
        messages.error(request, "게임을 찾을 수 없습니다.")
        return redirect("game:home")

    if m.status != MatchStatus.WAITING:
        messages.error(request, "진행중인 게임만 취소할 수 있습니다.")
        return redirect("game:detail", match_id=match_id)

    if m.attacker != request.user.username:
        messages.error(request, "공격자만 취소할 수 있습니다.")
        return redirect("game:detail", match_id=match_id)

    del _FAKE_DB[match_id]
    messages.success(request, "게임을 취소했습니다.")
    return redirect("game:home")
