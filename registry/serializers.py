from rest_framework import serializers

from registry.models import Member, Membership, Role, Period, Client, AuthEvent


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class AuthEventSerializer(serializers.ModelSerializer):
    member = serializers.StringRelatedField()
    client = serializers.StringRelatedField()

    class Meta:
        model = AuthEvent
        fields = '__all__'


class MemberEnrollmentSerializer(serializers.Serializer):
    member = MemberSerializer()
    period = serializers.PrimaryKeyRelatedField(queryset=Period.objects.all())
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all())
    fee_paid = serializers.BooleanField()
