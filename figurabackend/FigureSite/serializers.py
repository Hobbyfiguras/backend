import random
from .models import User, ForumCategory, Forum, Post, Thread
from rest_framework import serializers
from django.templatetags.static import static
from django.core.paginator import Paginator
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

class MinimalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)

class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('creator', 'content', 'thread',)

class CreateThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('creator', 'title', 'forum',)

class BasicForumSerializer(serializers.ModelSerializer):
    thread_count = serializers.SerializerMethodField()

    def get_thread_count(self, obj):
        return obj.threads.count()

    class Meta:
        model = Forum
        lookup_field = 'slug'
        fields = '__all__'

class MinimalThreadSerializer(serializers.ModelSerializer):
    forum = BasicForumSerializer()
    class Meta:
        model = Thread
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    creator = PublicUserSerializer()
    thread = MinimalThreadSerializer()
    class Meta:
        model = Post
        fields = '__all__'



class MinimalPostSerializer(serializers.ModelSerializer):
    creator = MinimalUserSerializer()

    class Meta:
        model = Post
        exclude = ('content',)

class ThreadSerializer(serializers.ModelSerializer):
    creator = MinimalUserSerializer()
    forum = BasicForumSerializer()
    post_count = serializers.SerializerMethodField()
    last_post = MinimalPostSerializer()
    def get_post_count(self, obj):
        return obj.posts.count()

    class Meta:
        model = Thread
        fields = '__all__'

class FullForumSerializer(serializers.ModelSerializer):

    threads = ThreadSerializer(many=True, read_only=True)

    class Meta:
        model = Forum
        lookup_field = 'slug'
        fields = '__all__'



class ForumCategorySerializer(serializers.ModelSerializer):
    forums = BasicForumSerializer(many=True, read_only=True)
    
    class Meta:
        model = ForumCategory
        lookup_field = 'slug'
        fields = ('id', 'name', 'description', 'forums', 'slug',)
