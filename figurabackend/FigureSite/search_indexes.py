from django.utils import timezone
from haystack import indexes
from .models import Post

class PostIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, model_attr='content')
    username = indexes.CharField(model_attr='creator__username')
    thread_slug = indexes.CharField(model_attr='thread__slug')
    page = indexes.IntegerField(model_attr='page')
    hid = indexes.CharField(model_attr='hid')
    thread_title = indexes.CharField(model_attr='thread__title')
    thread_id = indexes.CharField(model_attr='thread__hid')
    thread_forum = indexes.CharField(model_attr='thread__forum__slug')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            created__lte=timezone.now()
        )
