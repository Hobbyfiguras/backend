from django.utils import timezone
from haystack import indexes
from .models import Post, Thread
from haystack import signals
from haystack.exceptions import NotHandled

from .search_fields import AvatarField

class ThreadIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, model_attr='title')
    username = indexes.CharField(model_attr='creator__username')
    slug = indexes.CharField(model_attr='slug')
    thread_id = indexes.CharField(model_attr='hid')
    forum = indexes.CharField(model_attr='forum__slug')
    modified = indexes.DateTimeField(model_attr='modified')
    created = indexes.DateTimeField(model_attr='created')
    post_count = indexes.IntegerField(model_attr='post_count')
    last_post_creator = indexes.CharField(model_attr='last_post__creator__username')
    avatar = AvatarField(model_attr='creator__avatar')
    def get_model(self):
        return Thread

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            created__lte=timezone.now()
        )