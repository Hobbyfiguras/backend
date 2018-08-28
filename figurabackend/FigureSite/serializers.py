from .models import User
from rest_framework import serializers

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'email',)

class FullUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)
