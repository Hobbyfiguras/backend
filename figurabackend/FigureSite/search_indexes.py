from django.utils import timezone
from haystack import indexes
from .models import Post, Thread, User
from haystack import signals
from haystack.exceptions import NotHandled

from .search_fields import AvatarField, UserAvatarField

class ThreadIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, model_attr='title')
    username = indexes.CharField(model_attr='creator__username')
    slug = indexes.CharField(model_attr='slug')
    thread_id = indexes.CharField(model_attr='hid')
    forum = indexes.CharField(model_attr='forum__slug')
    modified = indexes.DateTimeField(model_attr='modified')
    created = indexes.DateTimeField(model_attr='created')
    post_count = indexes.IntegerField(model_attr='post_count')
    nsfw = indexes.BooleanField(model_attr='nsfw')
    last_post_creator = indexes.CharField(model_attr='last_post__creator__username')
    def get_model(self):
        return Thread

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            created__lte=timezone.now()
        )

class UserIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, model_attr='username')
    avatar = UserAvatarField(model_attr='avatar')
    date_joined = indexes.DateTimeField(model_attr='date_joined')
    def get_model(self):
        return User