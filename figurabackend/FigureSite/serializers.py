import random
from .models import User, ForumCategory, Forum
from rest_framework import serializers
from django.templatetags.static import static

DEFAULT_AVATARS = [
        '/avatars/avatar_1.png',
        '/avatars/avatar_2.png',
        '/avatars/avatar_3.png',
        '/avatars/avatar_4.png',
        '/avatars/avatar_5.png'
    ]

class AvatarField(serializers.ImageField):

    def get_attribute(self, obj):
        return obj

    def to_representation(self, obj):
        """
        Serialize the object's class name.
        """
        if obj.avatar:
            return super(AvatarField, self).to_representation(obj.avatar)
        else:
            random.seed(obj.id)
            return self.context['request'].build_absolute_uri(static(random.choice(DEFAULT_AVATARS)))

    def to_internal_value(self, obj):
        return super(serializers.ImageField, self).to_internal_value(obj)

class PublicUserSerializer(serializers.ModelSerializer):
    avatar = AvatarField()
    #avatar = serializers.ImageField()
    def get_avatar(self, obj):
        print("get avatar")


    class Meta:
        model = User
        exclude = ('password', 'email',)



class FullUserSerializer(PublicUserSerializer):
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
