from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q

class User(AbstractUser):
    total_score = models.IntegerField(default=0)

    # ✅ 1. 총 게임 수 계산 (상태가 FINISHED인 게임만 카운트)
    @property
    def game_count(self):
        # game 앱의 Game 모델 가져오기 (순환 참조 방지)
        from game.models import Game
        
        # 내가 공격자거나 수비자이면서, 게임이 '끝난(FINISHED)' 상태인 것만 셈
        return Game.objects.filter(
            (Q(attacker=self) | Q(defender=self)) & 
            Q(status=Game.Status.FINISHED)
        ).count()

    # ✅ 2. 승리 수 계산 (내가 공격자일 때 공격자 승 + 내가 수비자일 때 수비자 승)
    @property
    def win_count(self):
        from game.models import Game
        
        # 케이스 A: 내가 공격자(attacker)이고 결과가 공격자 승리(ATTACKER_WIN)
        case_attacker_win = Q(attacker=self) & Q(result=Game.Result.ATTACKER_WIN)
        
        # 케이스 B: 내가 수비자(defender)이고 결과가 수비자 승리(DEFENDER_WIN)
        case_defender_win = Q(defender=self) & Q(result=Game.Result.DEFENDER_WIN)
        
        # 두 케이스 중 하나라도 해당하면 승리!
        return Game.objects.filter(case_attacker_win | case_defender_win).count()