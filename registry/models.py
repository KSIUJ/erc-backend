from django.core.validators import validate_email
from django.db import models


class NullCharField(models.CharField):
    def get_db_prep_value(self, value, *args, **kwargs):
        if self.blank is True and self.null is True and value == '':
            value = None
        return super().get_db_prep_value(value, *args, **kwargs)


class Member(models.Model):
    given_name = models.CharField(max_length=128, blank=True)
    surname = models.CharField(max_length=128, blank=True)
    email = NullCharField(max_length=128, unique=True, validators=[validate_email])
    card_id = NullCharField(max_length=20, unique=True, null=True, blank=True, default=None)
    discord_id = NullCharField(max_length=128, unique=True, null=True, blank=True, default=None)
    ldap_uid = NullCharField(max_length=64, unique=True, null=True, blank=True, default=None)
    do_not_contact = models.BooleanField(default=False)
    tshirt = models.BooleanField(default=False)

    def display_name(self):
        return (self.given_name + " " + self.surname).strip()

    def __str__(self):
        return self.display_name()


class Period(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def years(self):
        return str(self.start_date.year) + "/" + str(self.end_date.year)

    def __str__(self):
        return self.years()


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="memberships")
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name="memberships")
    roles = models.ManyToManyField(Role, related_name='memberships')
    fee_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.member.display_name() + " " + self.period.years()

    class Meta:
        unique_together = ['member', 'period']


class Client(models.Model):
    client_id = models.CharField(max_length=32, unique=True)
    secret = models.CharField(max_length=64)
    name = models.CharField(max_length=64, unique=True)
    enabled = models.BooleanField(default=True)
    permissions = models.ManyToManyField(Role, blank=True)

    def __str__(self):
        return self.name


class AuthEvent(models.Model):
    CARD = 'CARD'
    LDAP = 'LDAP'
    DISCORD = 'DISCORD'
    EMAIL = 'EMAIL'
    AUTH_EVENT_TYPES = (
        (CARD, 'Card'),
        (LDAP, 'LDAP'),
        (DISCORD, 'Discord'),
        (EMAIL, 'Email')
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="auth_events")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="auth_events", null=True, blank=True)
    type = models.CharField(max_length=10, choices=AUTH_EVENT_TYPES, default=CARD)
    value = models.CharField(max_length=64, blank=False)
    success = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client.name + ' ' + (self.member.display_name() if self.member else 'UNKNOWN') + ' ' + str(
            self.date) + ' ' + str(self.success)
