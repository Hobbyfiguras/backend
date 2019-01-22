import random
from .models import User, ForumCategory, Forum, Post, Thread, Report, VoteType, UserVote, Notification, BanReason, PrivateMessage, MFCItem
from rest_framework import serializers
from django.templatetags.static import static
from django.core.paginator import Paginator
from .mixins import EagerLoadingMixin
from rest_framework_serializer_extensions.fields import HashIdField
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin
from drf_extra_fields.fields import Base64ImageField
from rest_framework_serializer_extensions.utils import external_id_from_model_and_internal_id
from .avatars import get_avatar

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
            return self.context['request'].build_absolute_uri(get_avatar(obj))

    def to_internal_value(self, obj):
        return super(serializers.ImageField, self).to_internal_value(obj)



class UpdateUserSerializer(serializers.ModelSerializer):
    id = HashIdField(model=User)
    avatar = AvatarField()
    location = serializers.CharField(allow_null=True, allow_blank=True)
    mfc_username = serializers.CharField(allow_null=True, allow_blank=True)
    anilist_username = serializers.CharField(allow_null=True, allow_blank=True)
    twitter_username = serializers.CharField(allow_null=True, allow_blank=True)
    class Meta:
        model = User
        exclude = ('password',)


class MFCItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFCItem
        fields = '__all__'


class MinimalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class MinimalPostSerializer(serializers.ModelSerializer):
    id = HashIdField(model=Post)
    creator = MinimalUserSerializer()
    content = None
    class Meta:
        model = Post
        exclude = ('content',)

class BanReasonSerializer(serializers.ModelSerializer):
    id = HashIdField(model=BanReason)
    banner = MinimalUserSerializer()
    banned_user = MinimalUserSerializer()
    post = MinimalPostSerializer()
    class Meta:
        model = BanReason
        fields = '__all__'

class PublicUserSerializer(serializers.ModelSerializer):
    id = HashIdField(model=User)
    avatar = AvatarField()
    post_count = serializers.SerializerMethodField()
    thread_count = serializers.SerializerMethodField()
    bans = serializers.SerializerMethodField() 

    def get_bans(self, obj):
        bans = obj.bans.all().order_by('-created')
        return BanReasonSerializer(bans, many=True).data

    def get_post_count(self, obj):
        return obj.posts.count()
    def get_thread_count(self, obj):
        return obj.threads.count()
    class Meta:
        model = User
        exclude = ('password', 'email', 'nsfw_enabled',)
class FullUserSerializer(PublicUserSerializer):
    id = HashIdField(model=User)
    class Meta:
        model = User
        exclude = ('password',)
class CreatePostSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    id = HashIdField(model=Post, required=False)
    class Meta:
        model = Post
        fields = ('id', 'creator', 'content', 'thread',)


class CreateThreadSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    class Meta:
        model = Thread
        fields = ('creator', 'title', 'forum', 'nsfw',)

class BasicForumSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    id = HashIdField(model=Forum)
    thread_count = serializers.SerializerMethodField()

    def get_thread_count(self, obj):
        return obj.threads.count()

    class Meta:
        model = Forum
        lookup_field = 'slug'
        fields = '__all__'

class MinimalThreadSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    forum = BasicForumSerializer()
    id = HashIdField(model=Thread)
    creator = MinimalUserSerializer()
    class Meta:
        model = Thread
        exclude = ('subscribers',)

class BasePostSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    id = HashIdField(model=Post)
    content = serializers.SerializerMethodField()
    def get_content(self, obj):
        if not obj.deleted:
            return obj.content
        else:
            return '< Post eliminado >'

class UserVoteSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    id = HashIdField(model=UserVote)
    class Meta:
        model = UserVote
        fields = ('id', 'name', 'image',)

class VoteTypeSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    id = HashIdField(model=VoteType)
    class Meta:
        model = VoteType
        fields = ('name', 'order', 'icon', 'id',)



class PostSerializer(BasePostSerializer):
    creator = PublicUserSerializer()
    thread = MinimalThreadSerializer()
    votes = serializers.SerializerMethodField()
    page = serializers.ReadOnlyField()
    bans = BanReasonSerializer(many=True)
    modified_by = MinimalUserSerializer()

    def get_votes(self, obj):
        votes = []
        for user_vote in obj.votes.all():
            for i, vote in enumerate(votes):
                if vote['id'] == external_id_from_model_and_internal_id(VoteType, user_vote.vote_type.id):
                    break
            else:
                serializer = VoteTypeSerializer(user_vote.vote_type, context=self.context)
                votes.append({**serializer.data, **{'vote_count': 0, 'users': []}})

            for i, vote in enumerate(votes):
                if vote['id'] == external_id_from_model_and_internal_id(VoteType, user_vote.vote_type.id):
                    votes[i]['vote_count'] += 1
                    votes[i]['users'].append(user_vote.user.username)
                    break
        return votes
        

    class Meta:
        model = Post
        fields = '__all__'


class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('content',)
class MinimalPostSerializerContent(BasePostSerializer):
    creator = MinimalUserSerializer()
    class Meta:
        model = Post
        fields = '__all__'

class ThreadSerializer(serializers.ModelSerializer):
    id = HashIdField(model=Thread)
    creator = PublicUserSerializer()
    forum = BasicForumSerializer()
    post_count = serializers.SerializerMethodField()
    last_post = MinimalPostSerializer()
    first_post = MinimalPostSerializerContent()
    def get_post_count(self, obj):
        return obj.posts.count()

    class Meta:
        model = Thread
        exclude = ('subscribers', 'is_sticky',)

class FullThreadSerializer(ThreadSerializer):
    related_items = MFCItemSerializer(many=True)
    class Meta:
        model = Thread
        exclude = ('subscribers',)

class FullCreateThreadSerializer(ThreadSerializer):
    class Meta:
        model = Thread
        exclude = ('subscribers',)

class PrivateMessageSerializer(serializers.ModelSerializer):
    id = HashIdField(model=PrivateMessage)
    creator = PublicUserSerializer()
    receiver = PublicUserSerializer()

    class Meta:
        model = PrivateMessage
        fields = '__all__'

class CreatePrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        fields = ('subject', 'content', 'creator', 'receiver',)
class UpdatePrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        fields = ('read',)
class ForumCategorySerializer(serializers.ModelSerializer):
    forums = BasicForumSerializer(many=True, read_only=True)
    
    class Meta:
        model = ForumCategory
        lookup_field = 'slug'
        fields = ('id', 'name', 'description', 'forums', 'slug', 'order', )

class FullForumSerializer(serializers.ModelSerializer):
    threads = ThreadSerializer(many=True, read_only=True)
    category = ForumCategorySerializer()

    class Meta:
        model = Forum
        lookup_field = 'slug'
        fields = '__all__'

class CreateForumSerializer(BasicForumSerializer):
    description = serializers.CharField(required = False, allow_blank = True, allow_null = True)
    icon = Base64ImageField(required = False, allow_null = True)
    id = None
    class Meta:
        model = Forum
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):

    post = PostSerializer()

    class Meta:
        model = Report
        fields = '__all__'

class CreateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class NotificationPostSerializer(BasePostSerializer):
    creator = MinimalUserSerializer()
    page = serializers.ReadOnlyField()
    thread = MinimalThreadSerializer()
    class Meta:
        model = Post
        fields = '__all__'

class NotificationObjectField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Post):
            return NotificationPostSerializer(value).data

class NotificationUserSerializer(serializers.ModelSerializer):
    avatar = AvatarField()
    class Meta:
        model = User
        fields = ('username', 'avatar',)

class NotificationSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    id = HashIdField(model=Notification)
    actor = NotificationUserSerializer()
    notification_object = NotificationObjectField(read_only = True)
    class Meta:
        model = Notification
        exclude = ('object_id', 'user', 'object_type',)