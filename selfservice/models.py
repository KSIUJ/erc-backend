import secrets

from django.db import models

from registry.models import Member


def _random_token():
    return secrets.token_urlsafe(32)


class SelfServiceTokenType(models.TextChoices):
    CARD_ID = "CARD_ID", "Card ID"


class SelfServiceToken(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, default=_random_token, unique=True)
    type = models.CharField(max_length=10, choices=SelfServiceTokenType.choices, default=SelfServiceTokenType.CARD_ID)
