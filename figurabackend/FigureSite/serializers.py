from .models import User, ForumCategory, Forum
from rest_framework import serializers

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'email',)

class FullUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = '__all__'


class ForumCategorySerializer(serializers.ModelSerializer):
    forums = ForumSerializer(many=True, read_only=True)

    class Meta:
        model = ForumCategory
        fields = ('id', 'name', 'description', 'forums',)
