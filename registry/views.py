from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from registry.models import Member, Membership, Period, Role, Client, AuthEvent
from registry.serializers import MemberSerializer, MembershipSerializer, PeriodSerializer, RoleSerializer, \
    ClientSerializer, AuthEventSerializer, MemberEnrollmentSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all().order_by('id')
    serializer_class = MemberSerializer
    filterset_fields = '__all__'
    search_fields = ('given_name', 'surname', 'email', 'discord_id', 'card_id', 'ldap_uid')

    @action(detail=True)
    def memberships(self, request, pk=None):
        member = self.get_object()
        memberships = Membership.objects.filter(member=member).all()
        json = MembershipSerializer(memberships, many=True)
        return Response(json.data)

    @action(detail=False, methods=['POST'])
    def enroll_with_membership(self, request):
        serializer = MemberEnrollmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        m = Member.objects.create(**serializer.validated_data['member'])
        membership = Membership.objects.create(member=m, period=serializer.validated_data['period'],
                                               fee_paid=serializer.validated_data['fee_paid'])
        membership.roles.add(*serializer.validated_data['roles'])
        return Response()


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all().order_by('id')
    serializer_class = MembershipSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = '__all__'


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all().order_by('id')
    serializer_class = PeriodSerializer
    filterset_fields = '__all__'


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    filterset_fields = '__all__'


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('name')
    serializer_class = ClientSerializer
    filterset_fields = '__all__'


class AuthEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuthEvent.objects.all().order_by('-date')
    serializer_class = AuthEventSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = '__all__'

    @action(detail=False)
    def last_scanned_card(self, request):
        event = AuthEvent.objects.filter(event_type=AuthEvent.CARD).order_by('-date').first()
        if event is None:
            raise NotFound(detail="No scanned cards", code=404)
        return Response({"card_id": event.value})
