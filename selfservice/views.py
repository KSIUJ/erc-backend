from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from registry.models import AuthEvent
from selfservice.models import SelfServiceToken
from selfservice.serializers import SelfServiceTokenSerializer, SelfServiceTokenValueSerializer, \
    SelfServiceSetCardIdSerializer


class SelfServiceTokenViewSet(mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    queryset = SelfServiceToken.objects.all().order_by('id')
    serializer_class = SelfServiceTokenSerializer
    filterset_fields = '__all__'
    permission_classes = [IsAuthenticated]


class SelfServiceView(GenericViewSet, mixins.RetrieveModelMixin):
    queryset = SelfServiceToken.objects.all().order_by('id')
    lookup_field = 'token'
    serializer_class = SelfServiceTokenValueSerializer
    TIMOUT_S = 5

    @action(detail=True, methods=["POST"])
    def set_card_id(self, request, token):
        token = self.get_object()
        serializer = SelfServiceSetCardIdSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        client = serializer.validated_data["client"]
        event = AuthEvent.objects.filter(client=client).order_by('-date').first()
        if event is None or (timezone.now() - event.date).seconds > SelfServiceView.TIMOUT_S:
            raise NotFound(detail="No recently scanned cards for this client", code=404)
        member = token.member
        with transaction.atomic():
            member.card_id = event.value
            member.save()
            token.delete()
        return Response(data={
            "card_id": event.value
        })
