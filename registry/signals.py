from django.dispatch import receiver
from django_cas_ng.signals import cas_user_authenticated


@receiver(cas_user_authenticated)
def cas_callback(sender, **kwargs):
    user = kwargs.pop('user')
    attributes = kwargs.pop('attributes')
    user.first_name = attributes["givenName"]
    user.last_name = attributes["sn"]
    user.is_staff = True
    user.is_superuser = True
    user.save()
