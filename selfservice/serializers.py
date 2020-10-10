from rest_framework import serializers

from registry.models import Client, Member
from selfservice.models import SelfServiceToken


class SelfServiceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfServiceToken
        fields = '__all__'
        read_only_fields = ['token']


class SelfServiceTokenValueSerializer(serializers.ModelSerializer):
    member = serializers.StringRelatedField()

    class Meta:
        model = SelfServiceToken
        fields = ['token', "type", "member"]
        read_only_fields = fields


class SelfServiceSetCardIdSerializer(serializers.Serializer):
    client = serializers.SlugRelatedField(queryset=Client.objects.all().order_by('name'), slug_field="name")
