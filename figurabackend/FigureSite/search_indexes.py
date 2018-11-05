from django.utils import timezone
from haystack import indexes
from .models import Post, Thread

class ThreadIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, model_attr='title')
    username = indexes.CharField(model_attr='creator__username')
    slug = indexes.CharField(model_attr='slug')
    id = indexes.CharField(model_attr='hid')
    forum = indexes.CharField(model_attr='forum__slug')


    def get_model(self):
        return Thread

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            created__lte=timezone.now()
        )
