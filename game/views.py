# import random
# from dataclasses import dataclass
# from enum import Enum
# from typing import Dict

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
# from django.shortcuts import redirect, render, get_object_or_404
# from django.db import transaction

# from .models import Game
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class MatchStatus(str, Enum):
#     WAITING = "WAITING"    # 상대 반격 전 (진행중)
#     COUNTER = "COUNTER"    # 반격 진행 중(카운터 플로우 진입)
#     FINISHED = "FINISHED"  # 종료


# @dataclass
# class FakeMatch:
#     id: int
#     attacker: str
#     defender: str
#     status: MatchStatus


# _FAKE_DB: Dict[int, FakeMatch] = {}
# _SEQ = 1


# def _next_id() -> int:
#     global _SEQ
#     v = _SEQ
#     _SEQ += 1
#     return v


# @login_required
# def home(request: HttpRequest) -> HttpResponse:
#     # 로그인 후 메인: new match / list 버튼만 있어도 됨
#     return render(request, "game/main_logged_in.html")


# @login_required
# def match_list(request: HttpRequest) -> HttpResponse:
#     # 임시: 내 관련 매치만 보여주기
#     username = request.user.username
#     matches = [
#         m for m in _FAKE_DB.values()
#         if m.attacker == username or m.defender == username
#     ]
#     matches.sort(key=lambda x: x.id, reverse=True)
#     return render(request, "game/match_list.html", {"matches": matches})


# @login_required
# def new_match(request: HttpRequest) -> HttpResponse:
#     # NEW MATCH 화면
#     if request.method == "GET":
#         return render(request, "game/match.html", {"mode": "NEW"})

#     if request.method != "POST":
#         return HttpResponseNotAllowed(["GET", "POST"])

#     # 임시로 defender 문자열만 받음 (DB 붙이면 User 선택)
#     defender = (request.POST.get("defender") or "").strip() or "defender"
#     match_id = _next_id()
#     _FAKE_DB[match_id] = FakeMatch(
#         id=match_id,
#         attacker=request.user.username,
#         defender=defender,
#         status=MatchStatus.WAITING,
#     )

#     # "카드 뽑기"로 바로 넘어가고 싶으면 play로 리다이렉트
#     return redirect("game:play", match_id=match_id)


# @login_required
# def match_result(request: HttpRequest, match_id: int) -> HttpResponse:
#     m = _FAKE_DB.get(match_id)
#     if not m:
#         messages.error(request, "게임을 찾을 수 없습니다.")
#         return redirect("game:home")

#     # 템플릿에서 WAITING/FINISHED/COUNTER 분기 가능하도록 state 제공
#     return render(request, "game/match_result.html", {"match": m, "state": m.status})


# @login_required
# def counter_prompt(request: HttpRequest, match_id: int) -> HttpResponse:
#     """
#     리스트에서 '반격하기' 눌렀을 때:
#     match_result.html#counter 느낌 = COUNTER 상태 화면(카운터어택 버튼 활성화)
#     """
#     m = _FAKE_DB.get(match_id)
#     if not m:
#         messages.error(request, "게임을 찾을 수 없습니다.")
#         return redirect("game:home")

#     # 임시로 상태 COUNTER로 바꿈
#     m.status = MatchStatus.COUNTER
#     return render(request, "game/match_result.html", {"match": m, "state": MatchStatus.COUNTER})


# @login_required
# def counter_start(request: HttpRequest, match_id: int) -> HttpResponse:
#     """
#     match_result COUNTER 화면에서 '카운터어택' 버튼 누르면:
#     match.html COUNTER 모드(카드 뽑기 버튼 활성화)
#     """
#     m = _FAKE_DB.get(match_id)
#     if not m:
#         messages.error(request, "게임을 찾을 수 없습니다.")
#         return redirect("game:home")

#     return render(request, "game/match.html", {"mode": "COUNTER", "match": m})


# @login_required
# def play(request: HttpRequest, match_id: int) -> HttpResponse:
#     """
#     카드 뽑기 눌렀을 때 playing.html
#     (임시: 결과 계산 안 함)
#     """
#     m = _FAKE_DB.get(match_id)
#     if not m:
#         messages.error(request, "게임을 찾을 수 없습니다.")
#         return redirect("game:home")

#     return render(request, "game/playing.html", {"match": m})


# @login_required
# def cancel_match(request: HttpRequest, match_id: int) -> HttpResponse:
#     """
#     진행중(WAITING)만 취소 가능
#     취소하면 메인으로 가고 게임 삭제
#     """
#     if request.method != "POST":
#         return HttpResponseNotAllowed(["POST"])

#     m = _FAKE_DB.get(match_id)
#     if not m:
#         messages.error(request, "게임을 찾을 수 없습니다.")
#         return redirect("game:home")

#     if m.status != MatchStatus.WAITING:
#         messages.error(request, "진행중인 게임만 취소할 수 있습니다.")
#         return redirect("game:detail", match_id=match_id)

#     if m.attacker != request.user.username:
#         messages.error(request, "공격자만 취소할 수 있습니다.")
#         return redirect("game:detail", match_id=match_id)

#     del _FAKE_DB[match_id]
#     messages.success(request, "게임을 취소했습니다.")
#     return redirect("game:home")

import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.contrib.auth import get_user_model
from .models import Game

User = get_user_model()

# ==========================================
# 1. 메인 & 리스트
# ==========================================

@login_required
def home(request):
    """로그인 후 메인: NEW MATCH / LIST 버튼"""
    return render(request, "game/main_logged_in.html")

@login_required
def match_list(request):
    """전적 리스트: 나를 기준으로 승/패/진행중 텍스트를 가공해서 전달"""
    user = request.user
    # 나랑 관련된 게임 모두 조회 (최신순)
    matches = Game.objects.filter(
        Q(attacker=user) | Q(defender=user)
    ).order_by('-created_at')

    # 템플릿에 넘겨줄 가공된 데이터 리스트
    rows = []

    for match in matches:
        # 기본 정보
        row = {
            'id': match.id,
            'attacker': match.attacker.username,
            'defender': match.defender.username,
            'state_text': '',   # 화면에 표시할 텍스트 (예: 승리, 패배, 대결 수락 대기 중)
            'result_class': ''  # CSS 클래스 (예: win, lose, pending)
        }

        # 1. 진행 중인 게임 (PENDING)
        if match.status == Game.Status.PENDING:
            row['result_class'] = 'pending'
            if user == match.attacker:
                row['state_text'] = "수락 대기 중 ⏳"
            else:
                row['state_text'] = "도전장이 왔습니다! ⚔️" # 수비자 입장
        
        # 2. 종료된 게임 (FINISHED)
        elif match.status == Game.Status.FINISHED:
            # (1) 무승부
            if match.result == Game.Result.DRAW:
                row['state_text'] = "무승부 🤝"
                row['result_class'] = 'draw'
            
            # (2) 승패 결정
            else:
                # 내가 공격자일 때
                if user == match.attacker:
                    if match.result == Game.Result.ATTACKER_WIN:
                        row['state_text'] = "승리 🏆"
                        row['result_class'] = 'win'
                    else:
                        row['state_text'] = "패배 😭"
                        row['result_class'] = 'lose'
                # 내가 수비자일 때
                else:
                    if match.result == Game.Result.DEFENDER_WIN:
                        row['state_text'] = "승리 🏆"
                        row['result_class'] = 'win'
                    else:
                        row['state_text'] = "패배 😭"
                        row['result_class'] = 'lose'
        
        # 3. 취소된 게임 등 기타
        else:
            row['state_text'] = "취소됨"
            row['result_class'] = 'cancel'

        rows.append(row)
    
    # 템플릿 변수명을 'matches'가 아니라 'rows'로 전달
    return render(request, "game/match_list.html", {"rows": rows})

# ==========================================
# 2. 게임 생성 (공격하기)
# ==========================================

@login_required
def new_match(request):
    """
    GET: 상대 선택 및 카드 선택 화면 (game/match.html)
    POST: 게임 생성 후 상세 페이지로 이동
    """
    if request.method == "POST":
        defender_username = request.POST.get("defender")
        selected_card = request.POST.get("selected_card")

        if not defender_username or not selected_card:
            messages.error(request, "상대방과 카드를 모두 선택해주세요.")
            return redirect("game:new")

        defender = get_object_or_404(User, username=defender_username)
        card_value = int(selected_card)

        # 1. 공격자 패 생성 (선택한 카드는 무조건 포함 + 나머지 랜덤 4장)
        pool = [i for i in range(1, 11) if i != card_value]
        attacker_hand = random.sample(pool, 4)
        attacker_hand.append(card_value)
        random.shuffle(attacker_hand)

        # 2. 수비자 패 미리 생성 (랜덤 5장)
        defender_hand = random.sample(range(1, 11), 5)

        # 3. 룰 랜덤 결정
        rule = random.choice([Game.Rule.HIGH_WINS, Game.Rule.LOW_WINS])

        # 4. DB 저장
        game = Game.objects.create(
            attacker=request.user,
            defender=defender,
            status=Game.Status.PENDING,
            rule=rule,
            attacker_card=card_value,
            attacker_hand=attacker_hand,
            defender_hand=defender_hand,
        )
        return redirect("game:detail", match_id=game.id)

    else:
        # GET: 랜덤 카드 5장 보여주기 (시각용)
        random_cards = random.sample(range(1, 11), 5)
        defenders = User.objects.exclude(pk=request.user.pk)
        return render(request, "game/match.html", {
            "mode": "NEW",
            "random_cards": random_cards,
            "defenders": defenders
        })

# ==========================================
# 3. 상세 조회 및 반격 프로세스
# ==========================================

@login_required
def match_result(request, match_id):
    """
    결과/상세 페이지 (WAITING / FINISHED / COUNTER 등 상태 표시)
    """
    game = get_object_or_404(Game, pk=match_id)
    return render(request, "game/match_result.html", {
        "match": game,
        "state": game.status  # 템플릿에서 상태에 따라 UI 분기
    })

@login_required
def counter_prompt(request, match_id):
    """
    반격하기 버튼을 눌렀을 때의 중간 단계
    (match_result.html에서 '카운터 어택' 버튼을 활성화해서 보여주는 역할)
    """
    game = get_object_or_404(Game, pk=match_id)
    
    # 유효성 검사
    if request.user != game.defender or game.status != Game.Status.PENDING:
        return redirect("game:detail", match_id=game.id)

    # 템플릿에 'COUNTER' 상태를 강제로 넘겨서 반격 UI를 띄움
    return render(request, "game/match_result.html", {
        "match": game,
        "state": "COUNTER"
    })

@login_required
def counter_start(request, match_id):
    """
    실제 반격 화면: 카드 선택 (game/match.html)
    """
    game = get_object_or_404(Game, pk=match_id)

    if request.user != game.defender or game.status != Game.Status.PENDING:
        return redirect("game:list")

    # 수비자는 이미 정해진 패(defender_hand) 중에서 골라야 함
    return render(request, "game/match.html", {
        "mode": "COUNTER",
        "match": game,
        "random_cards": game.defender_hand 
    })

@login_required
def play(request, match_id):
    """
    [핵심 로직] 카드를 제출했을 때 승패 판별 (POST)
    결과 처리 후 playing.html(애니메이션) 렌더링
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    game = get_object_or_404(Game, pk=match_id)

    # 1. 유효성 검사
    if game.status != Game.Status.PENDING:
        return redirect("game:detail", match_id=game.id)
    
    selected_card = request.POST.get("selected_card")
    if not selected_card:
        messages.error(request, "카드를 선택해주세요.")
        return redirect("game:counter_start", match_id=game.id)
    
    card_value = int(selected_card)
    
    # 내 패에 있는 카드가 맞는지 확인
    if card_value not in game.defender_hand:
        messages.error(request, "보유하지 않은 카드입니다.")
        return redirect("game:counter_start", match_id=game.id)

    # 2. 승패 로직 (Atomic)
    with transaction.atomic():
        game.defender_card = card_value
        
        a = game.attacker_card
        d = card_value
        
        # (1) 무승부
        if a == d:
            game.result = Game.Result.DRAW
            game.attacker_delta = 0
            game.defender_delta = 0
        
        # (2) 승부 결정
        else:
            is_attacker_win = False
            if game.rule == Game.Rule.HIGH_WINS:
                is_attacker_win = (a > d)
            else: # LOW_WINS
                is_attacker_win = (a < d)
            
            if is_attacker_win:
                game.result = Game.Result.ATTACKER_WIN
                game.attacker_delta = a
                game.defender_delta = -d
            else:
                game.result = Game.Result.DEFENDER_WIN
                game.attacker_delta = -a
                game.defender_delta = d

        # (3) 점수 반영
        if game.result != Game.Result.DRAW:
            game.attacker.total_score += game.attacker_delta
            game.defender.total_score += game.defender_delta
            game.attacker.save()
            game.defender.save()

        game.status = Game.Status.FINISHED
        game.save()

    # 결과 애니메이션 페이지(playing.html)로 이동
    return render(request, "game/playing.html", {"match": game})

@login_required
def cancel_match(request, match_id):
    """게임 취소"""
    if request.method == "POST":
        game = get_object_or_404(Game, pk=match_id)
        # 내가 공격자이고, 아직 상대가 받기 전(PENDING)일 때만 취소 가능
        if game.attacker == request.user and game.status == Game.Status.PENDING:
            game.delete()
            messages.success(request, "게임이 취소되었습니다.")
        else:
            messages.error(request, "취소할 수 없는 게임입니다.")
    
    return redirect("game:list")