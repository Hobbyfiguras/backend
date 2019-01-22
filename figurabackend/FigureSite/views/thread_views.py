from rest_framework_serializer_extensions.views import ExternalIdViewMixin
from rest_framework import mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action

from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet

from dry_rest_permissions.generics import DRYPermissions

from FigureSite.models import Thread
from FigureSite import serializers
from FigureSite.search_indexes import ThreadIndex

class ThreadPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20
    page_size_query_param = 'page_size'

class ThreadSearchSerializer(HaystackSerializer):
    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [ThreadIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [ "text", "username", "slug", "nsfw", "thread_id", "forum", "modified", "created", "post_count", "last_post_creator" ]

class ThreadSearchView(HaystackViewSet):
    index_models = [Thread]
    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    pagination_class = ThreadPagination
    serializer_class = ThreadSearchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ThreadViewSet(ExternalIdViewMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Thread.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.ThreadSerializer
  pagination_class = ThreadPagination

  def filter_queryset(self, queryset):
    queryset = super(ThreadViewSet, self).filter_queryset(queryset)
    return queryset.order_by('-created')

  def get_serializer_class(self):
    if self.action == 'create' or 'update' or 'partial_update':
      if self.request.user.is_staff:
        return serializers.FullThreadSerializer
      else:
        return serializers.ThreadSerializer
    else:
      return serializers.FullThreadSerializer
  def retrieve(self, request, pk=None):
    thread = self.get_object()
    print(pk)
    page = self.paginate_queryset(thread.posts.all().order_by('created'))
    posts = {}
    if page is not None:
      serializer = serializers.PostSerializer(page, many=True, context={'request': request})
      posts = self.get_paginated_response(serializer.data).data
    else:
      posts = serializers.PostSerializer(thread.posts, many=True, context={'request': request})
    return Response({**{'posts': posts, 'subscribed': request.user in thread.subscribers.all()}, **serializers.FullThreadSerializer(thread, context={'request': request}).data})

  @action(detail=True, methods=['post'])
  def change_subscription(self, request, pk=None):
    thread = self.get_object()
    if 'subscribed' in request.data:
      thread.change_user_subscription(request.user, request.data['subscribed'])
      return Response({}, status=status.HTTP_200_OK)
    else:
      return Response({}, status=status.HTTP_400_BAD_REQUEST)

  @action(detail=True, methods=['post'])
  def move_thread(self, request, pk=None):
    thread = self.get_object()
    print(request.data)
    if 'forum' in request.data:
      forum = Forum.objects.get(id=internal_id_from_model_and_external_id(Forum, request.data['forum']))
      if forum:
        thread.forum = forum
        thread.save()
        return Response({}, status=status.HTTP_200_OK)
      else:
        return Response({}, status=status.HTTP_404_NOT_FOUND)
    else:
      return Response({}, status=status.HTTP_400_BAD_REQUEST)
  @action(detail=True, methods=['post'])
  def make_nsfw(self, request, pk=None):
    thread = self.get_object()
    thread.nsfw = True
    thread.save()
    return Response({}, status=status.HTTP_200_OK)
  @action(detail=True, methods=['post'])
  def create_post(self, request, pk=None):
    thread = self.get_object()
    request.data['creator'] = request.user.id
    request.data['thread'] = thread.id
    serializer = serializers.CreatePostSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      thread.modified = timezone.now()
      thread.save()

      for subscriber in thread.subscribers.all():
        # Users shouldn't get notifications about themselves
        if request.user.id != subscriber.id:
          notification = Notification.objects.create(notification_type="notification_post_sub", user = subscriber, actor=request.user, notification_object=serializer.instance)
          notification.save()
          send_notification(request, notification)

      return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def get_throttles(self):
      if self.action == 'create_post':
          self.throttle_scope = 'posts'
      else:
          self.throttle_scope = None
      return super().get_throttles()