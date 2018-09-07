import random
from .models import User, ForumCategory, Forum, Post, Thread
from rest_framework import serializers
from django.templatetags.static import static
from django.core.paginator import Paginator
from .mixins import EagerLoadingMixin
from rest_framework_serializer_extensions.fields import HashIdField

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

class CreatePostSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['creator', 'thread']

    class Meta:
        model = Post
        fields = ('id', 'creator', 'content', 'thread',)

class CreateThreadSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    class Meta:
        model = Thread
        fields = ('creator', 'title', 'forum', 'nsfw',)

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

class BasePostSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    def get_content(self, obj):
        if not obj.deleted:
            return obj.content
        else:
            return '< Post eliminado >'

class PostSerializer(BasePostSerializer):
    creator = PublicUserSerializer()
    modified_by = PublicUserSerializer()
    thread = MinimalThreadSerializer()
    class Meta:
        model = Post
        fields = '__all__'



class MinimalPostSerializer(BasePostSerializer):
    creator = MinimalUserSerializer()
    content = None
    class Meta:
        model = Post
        exclude = ('content',)

class ThreadSerializer(serializers.ModelSerializer):
    id = HashIdField(model=Thread)
    creator = MinimalUserSerializer()
    forum = BasicForumSerializer()
    post_count = serializers.SerializerMethodField()
    last_post = MinimalPostSerializer()
    def get_post_count(self, obj):
        return obj.posts.count()

    class Meta:
        model = Thread
        fields = '__all__'

class FullForumSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _PREFETCH_RELATED_FIELDS = ['threads']
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
