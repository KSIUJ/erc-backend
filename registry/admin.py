from django.contrib import admin

# Register your models here.

from .models import Member, Period, Membership, Role, Client, AuthEvent

admin.site.register(Member)
admin.site.register(Period)
admin.site.register(Membership)
admin.site.register(Role)
admin.site.register(Client)
admin.site.register(AuthEvent)
