from django.conf import settings
from django.db import models


class Game(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        FINISHED = "FINISHED", "Finished"
        CANCELLED = "CANCELLED", "Cancelled"

    class Rule(models.TextChoices):
        HIGH_WINS = "HIGH_WINS", "Higher wins"
        LOW_WINS = "LOW_WINS", "Lower wins"

    class Result(models.TextChoices):
        ATTACKER_WIN = "ATTACKER_WIN", "Attacker wins"
        DEFENDER_WIN = "DEFENDER_WIN", "Defender wins"
        DRAW = "DRAW", "Draw"

    attacker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attacking_games",
    )
    defender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="defending_games",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rule = models.CharField(max_length=20, choices=Rule.choices)

    # 랜덤 제공 5장 (시연/디버깅에 유리)
    attacker_hand = models.JSONField(default=list)
    defender_hand = models.JSONField(default=list)

    attacker_card = models.PositiveSmallIntegerField(null=True, blank=True)
    defender_card = models.PositiveSmallIntegerField(null=True, blank=True)

    result = models.CharField(max_length=20, choices=Result.choices, null=True, blank=True)

    attacker_delta = models.IntegerField(default=0)
    defender_delta = models.IntegerField(default=0)

    finished_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["attacker", "status"]),
            models.Index(fields=["defender", "status"]),
        ]
