from datetime import datetime
from json import JSONDecodeError

from django.db.models import Q
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.utils import json

from registry.models import Client, Member, Membership, Role, AuthEvent

CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
CARD_ID = "card_id"
DISCORD_ID = "discord_id"
LDAP = "ldap"
EMAIL = "email"
ROLE = "role"


def log_event(client: Client, member, event_type: str, value: str, success: bool):
    AuthEvent.objects.create(
        client=client,
        member=member,
        event_type=event_type,
        success=success,
        value=value,
    )


def check_access(member: Member, client: Client, event_type, value):
    roles = set(
        Role.objects.filter(
            Q(memberships__member=member)
            & Q(memberships__period__start_date__lte=datetime.now())
            & Q(memberships__period__end_date__gte=datetime.now())
            & Q(memberships__fee_paid=True)
        ).distinct()
    )
    if len(roles) <= 0:
        log_event(client, member, event_type, value, False)
        return HttpResponseForbidden("Membership inactive or expired")
    allowed = any([x in roles for x in client.permissions.all()])
    if not allowed:
        log_event(client, member, event_type, value, False)
        return HttpResponseForbidden("Member not authorised to use this endpoint")
    log_event(client, member, event_type, value, True)
    return HttpResponse("OK")


def check_bulk(client: Client):
    query = None
    for role in client.permissions.all():
        tmp_query = Q(memberships__roles__name=role.name)
        query = query | tmp_query if query is not None else tmp_query

    if query is None:
        return HttpResponseForbidden("Client not accepting of any roles")

    members = list(
        Member.objects.filter(
            Q(memberships__period__start_date__lte=datetime.now())
            & Q(memberships__period__end_date__gte=datetime.now())
            & Q(memberships__fee_paid=True)
            & query
        ).distinct()
    )
    log_event(client, None, AuthEvent.BULK, client.name, True)
    return HttpResponse(json.dumps(list(map(lambda m: m.card_id, members))))


@csrf_exempt
@require_http_methods(["POST"])
def authorize_bulk(request):
    try:
        rq = json.loads(request.body.decode("utf-8"))
    except JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON payload")
    if CLIENT_ID not in rq:
        return HttpResponseBadRequest("No client id specified")
    try:
        client = Client.objects.get(client_id=rq[CLIENT_ID])
    except Client.DoesNotExist:
        return HttpResponseBadRequest("Unknown client id")
    if CLIENT_SECRET not in rq or rq[CLIENT_SECRET] != client.secret:
        return HttpResponseForbidden("Bad client secret")
    if not client.enabled:
        return HttpResponseForbidden("Client is disabled")
    return check_bulk(client)


@csrf_exempt
@require_http_methods(["POST"])
def authorize(request):
    try:
        rq = json.loads(request.body.decode("utf-8"))
    except JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON payload")
    if CLIENT_ID not in rq:
        return HttpResponseBadRequest("No client id specified")
    try:
        client = Client.objects.get(client_id=rq[CLIENT_ID])
    except Client.DoesNotExist:
        return HttpResponseBadRequest("Unknown client id")
    if CLIENT_SECRET not in rq or rq[CLIENT_SECRET] != client.secret:
        return HttpResponseForbidden("Bad client secret")
    if not client.enabled:
        return HttpResponseForbidden("Client is disabled")
    if CARD_ID in rq:
        try:
            return check_access(
                Member.objects.get(card_id=rq[CARD_ID]),
                client,
                AuthEvent.CARD,
                rq[CARD_ID],
            )
        except Member.DoesNotExist:
            log_event(client, None, AuthEvent.CARD, rq[CARD_ID], False)
            return HttpResponseNotFound("Unknown card id")
    if DISCORD_ID in rq:
        try:
            return check_access(
                Member.objects.get(card_id=rq[DISCORD_ID]),
                client,
                AuthEvent.DISCORD,
                rq[DISCORD_ID],
            )
        except Member.DoesNotExist:
            log_event(client, None, AuthEvent.DISCORD, rq[DISCORD_ID], False)
            return HttpResponseNotFound("Unknown discord id")
    if LDAP in rq:
        try:
            return check_access(
                Member.objects.get(card_id=rq[LDAP]), client, AuthEvent.LDAP, rq[LDAP]
            )
        except Member.DoesNotExist:
            log_event(client, None, AuthEvent.LDAP, rq[LDAP], False)
            return HttpResponseNotFound("Unknown ldap uid")
    if EMAIL in rq:
        try:
            return check_access(
                Member.objects.get(card_id=rq[EMAIL]),
                client,
                AuthEvent.EMAIL,
                rq[EMAIL],
            )
        except Member.DoesNotExist:
            log_event(client, None, AuthEvent.EMAIL, rq[EMAIL], False)
            return HttpResponseNotFound("Unknown email address")

    return HttpResponseBadRequest("No query specified")


@csrf_exempt
@require_http_methods(["GET"])
def legacy_lock_controller(request):
    card_id = request.GET.get("card_id")
    if not card_id:
        return HttpResponseBadRequest("No query specified")
    try:
        client = Client.objects.get(client_id="legacy")
    except Client.DoesNotExist:
        return HttpResponseNotFound("Legacy endpoint not defined")
    if not client.enabled:
        return HttpResponseForbidden("Legacy endpoint disabled")
    try:
        return check_access(
            Member.objects.get(card_id=card_id), client, AuthEvent.CARD, card_id
        )
    except Member.DoesNotExist:
        log_event(client, None, AuthEvent.CARD, card_id, False)
        return HttpResponseNotFound("Unknown card id")
