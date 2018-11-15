from django.shortcuts import render
from .models import User, ForumCategory, Forum, Thread, Post, Report, VoteType, Notification, BanReason, PrivateMessage
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework import mixins
from . import serializers
import datetime
from rest_framework import permissions
from django.utils import timezone
from .mixins import EagerLoadingMixin
from django.http import Http404
from rest_framework_serializer_extensions.views import ExternalIdViewMixin
from rest_framework.views import APIView
from rest_framework_serializer_extensions.utils import external_id_from_model_and_internal_id, internal_id_from_model_and_external_id
from dry_rest_permissions.generics import DRYPermissions
from .notifications import send_notification
from .search_indexes import ThreadIndex, UserIndex
from django.db.models import Q
from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet

class PrivateMessagePagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20
    page_size_query_param = 'page_size'

class ThreadPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20
    page_size_query_param = 'page_size'

class UserPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20
    page_size_query_param = 'page_size'

class ThreadSerializer(HaystackSerializer):
    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [ThreadIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [ "text", "username", "slug", "nsfw", "thread_id", "forum", "modified", "created", "post_count", "last_post_creator" ]

class UserSerializer(HaystackSerializer):
    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [UserIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [ "avatar", "text", "date_joined", "post_count", "is_staff" ]

class UserSearchView(HaystackViewSet):
    index_models = [User]
    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    pagination_class = UserPagination
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def finalize_response(self, request, response, *args, **kwargs):
      response = super(UserSearchView, self).finalize_response(request, response, *args, **kwargs)
      print(response.data)
      for i, user in enumerate(response.data['results']):
        response.data['results'][i]['avatar'] = request.build_absolute_uri(response.data['results'][i]['avatar'])
      return response

class ThreadSearchView(HaystackViewSet):
    index_models = [Thread]
    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    pagination_class = ThreadPagination
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
class UserPostPagination(PageNumberPagination):
    page_size = 10

class ReportPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 15
    page_size_query_param = 'page_size'

class ReportViewSet(viewsets.ModelViewSet):
  queryset = Report.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.ReportSerializer
  pagination_class = ReportPagination

  def filter_queryset(self, queryset):
    queryset = super(ReportViewSet, self).filter_queryset(queryset)
    return queryset.order_by('-created')
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")
class PrivateMessageViewSet(ExternalIdViewMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = PrivateMessage.objects.all()
  permission_classes = (DRYPermissions,)
  pagination_class = PrivateMessagePagination
  serializer_class = serializers.PrivateMessageSerializer

  def get_serializer_class(self):
    if self.action == 'partial_update' or self.action == 'update':
      return serializers.UpdatePrivateMessageSerializer
    return serializers.PrivateMessageSerializer

  def get_queryset(self):
    read = self.request.query_params.get('read', None)
    print(read)
    if read:
      return PrivateMessage.objects.filter(receiver=self.request.user, read=str2bool(read))
    elif self.action == 'sent':
      return PrivateMessage.objects.filter(creator=self.request.user)
    else:
      return PrivateMessage.objects.filter(receiver=self.request.user)

  def filter_queryset(self, queryset):
    queryset = super(PrivateMessageViewSet, self).filter_queryset(queryset)
    return queryset.order_by('-created')

class UserViewSet(viewsets.ModelViewSet, EagerLoadingMixin):
  queryset = User.objects.all()
  permission_classes = (DRYPermissions,)
  lookup_field = 'username'

  def retrieve(self, request, username=None):
    if self.request.user.is_anonymous:
      return Response({}, status=status.HTTP_403_FORBIDDEN)
    else:
      return super(UserViewSet, self).retrieve(request, username)
  def get_serializer_class(self):
    if self.action == 'partial_update':
      return serializers.UpdateUserSerializer
    if self.request.user.is_staff or self.kwargs.get('pk') == 'current':
      return serializers.FullUserSerializer

    return serializers.PublicUserSerializer

  @action(methods=['post'], detail=True)
  def ban_user(self, request, username=None):
    user = self.get_object()
    if request.data['post']:
      post = Post.objects.get(pk=internal_id_from_model_and_external_id(Post, request.data['post']))
      ban_reason = BanReason(post=post, ban_reason=request.data['ban_reason'], banner=request.user, banned_user=post.creator, ban_expiry_date=request.data['ban_expiry_date'])
      ban_reason.save()
      return Response(serializers.BanReasonSerializer(ban_reason).data, status=status.HTTP_200_OK)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

  @action(methods=['post'], detail=True)
  def send_message(self, request, username=None):
    user = self.get_object()
    request.data['creator'] = request.user.id
    request.data['receiver'] = user.id
    serializer = serializers.CreatePrivateMessageSerializer(data=request.data)
    if serializer.is_valid():
      message = serializer.save()
      return Response(serializers.PrivateMessageSerializer(message, context={'request': request}).data, status=status.HTTP_200_OK)
    else: 
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def get_object(self):
    pk = self.kwargs.get('username')
    if pk == "current":
      return self.request.user

    return super(UserViewSet, self).get_object()

  @action(methods=['get'], pagination_class=UserPostPagination, detail=True)
  def posts(self, request, username=None):
    user = self.get_object()
    page = self.paginate_queryset(user.posts.all().order_by('created'))
    if page is not None:
      serializer = serializers.PostSerializer(page, many=True, context={'request': request})
      return self.get_paginated_response(serializer.data)
    else:
      posts = serializers.PostSerializer(user.posts, many=True, context={'request': request})
    return Response(posts.data)

  @action(methods=['get'], pagination_class=UserPostPagination, detail=True)
  def threads(self, request, username=None):
    user = self.get_object()
    page = self.paginate_queryset(user.threads.all().order_by('-created'))
    if page is not None:
      serializer = serializers.ThreadSerializer(page, many=True, context={'request': request})
      return self.get_paginated_response(serializer.data)
    else:
      threads = serializers.ThreadSerializer(user.threads.all().order_by('-created'), many=True, context={'request': request})
    return Response(threads.data)



class ForumCategoryViewSet(viewsets.ModelViewSet):
  queryset = ForumCategory.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.ForumCategorySerializer
  lookup_field = 'slug'

  def filter_queryset(self, queryset):
    queryset = super(ForumCategoryViewSet, self).filter_queryset(queryset)
    return queryset.order_by('order')

class ForumPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 20
    page_size_query_param = 'page_size'

class ForumViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Forum.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.FullForumSerializer
  lookup_field = 'slug'

  def get_serializer_class(self):
    if self.action == 'create' or self.action == 'partial_update':
      return serializers.CreateForumSerializer
    return serializers.FullForumSerializer

  @action(detail=True, methods=['post'])
  def move_up(self, request, slug=None):
    forum = self.get_object()
    forum.up()
    return Response({}, status=status.HTTP_200_OK)

  @action(detail=True, methods=['post'])
  def move_down(self, request, slug=None):
    forum = self.get_object()
    forum.down()
    return Response({}, status=status.HTTP_200_OK)

  @action(detail=True, pagination_class=ForumPagination)
  def threads(self, request, slug=None):
    forum = self.get_object()
    page = self.paginate_queryset(forum.threads.all().order_by('-is_sticky', '-modified'))
    threads = {}
    if page is not None:
      serializer = serializers.FullThreadSerializer(page, many=True, context={'request': request})
      threads = self.get_paginated_response(serializer.data).data
    else:
      threads = serializers.FullThreadSerializer(forum.threads.all().order_by('-modified'), many=True, context={'request': request}).data

    return Response({**{'threads': threads}, **serializers.BasicForumSerializer(forum).data})

  @action(detail=True, methods=['post'])
  def create_thread(self, request, slug=None):
    forum = self.get_object()
    request.data['creator'] = request.user.id
    request.data['forum'] = forum.id
    
    thread_serializer = serializers.CreateThreadSerializer(data=request.data)
    if thread_serializer.is_valid() and request.data['content']:
      thread = thread_serializer.save()
      post_data = {
        'thread': thread.id,
        'creator': request.user.id,
        'content': request.data['content'],
        'nsfw': request.data['nsfw']
      }
      post_serializer = serializers.CreatePostSerializer(data=post_data)
      if post_serializer.is_valid():
        post_serializer.save()
        thread.save()
        data = thread_serializer.data
        data['slug'] = thread.slug
        data['id'] = external_id_from_model_and_internal_id(Thread, thread.id)
        return Response(data, status=status.HTTP_201_CREATED)
      else:
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    else:
      return Response(thread_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    thread.change_user_subscription(request.user, request.data['subscribed'])
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


class NotificationsPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 5
    page_size_query_param = 'page_size'

class NotificationsViewSet(ExternalIdViewMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.NotificationSerializer
  pagination_class = NotificationsPagination

  def filter_queryset(self, queryset):
    queryset = super(NotificationsViewSet, self).filter_queryset(queryset)
    return queryset.order_by('-created')

  def get_queryset(self):
    if self.action == 'unread':
      return Notification.objects.filter(user=self.request.user, read=False)
    else:
      return Notification.objects.filter(user=self.request.user)
  
  @action(detail=False)
  def unread(self, request, pk=None):
    queryset = self.filter_queryset(self.get_queryset())

    page = self.paginate_queryset(queryset)
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    serializer = self.get_serializer(queryset, many=True)

    return Resposne(serializer.data)
  
class PostsPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10
    page_size_query_param = 'page_size'

class PostViewSet(ExternalIdViewMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Post.objects.all()
  pagination_class = PostsPagination
  serializer_class = serializers.PostSerializer
  permission_classes = (DRYPermissions,)

  def get_serializer_class(self):
    if self.action == 'partial_update':
      return serializers.UpdatePostSerializer
    else:
      return serializers.PostSerializer

  def partial_update(self, request, *args, **kwargs):
    post = self.get_object()
    serializer = self.get_serializer(post, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(modified=timezone.now(), modified_by=request.user)
    if getattr(post, '_prefetched_objects_cache', None):
      # If 'prefetch_related' has been applied to a queryset, we need to
      # forcibly invalidate the prefetch cache on the instance.
      post._prefetched_objects_cache = {}

    print(serializer.data)
    return Response(serializer.data)
  @action(detail=True, methods=['post'])
  def delete(self, request, pk=None):
    post = self.get_object()
    try:
      post.deleted = True
      if request.data['delete_reason']:
        post.delete_reason = request.data['delete_reason']
        post.modified_by = request.user
      post.save()
    except Http404:
      pass
    return Response(status=status.HTTP_204_NO_CONTENT)

  @action(detail=True, methods=['post'])
  def report(self, request, pk=None):
    post = self.get_object()
    request.data['post'] = post.id
    request.data['creator'] = request.user.id
    report = serializers.CreateReportSerializer(data=request.data)
    if report.is_valid():
      report.save()
      return Response(report.data, status=status.HTTP_201_CREATED)
    else:
      return Response(report.errors, status=status.HTTP_400_BAD_REQUEST)

  @action(detail=True, methods=['post'])
  def vote(self, request, pk=None):
    post = self.get_object()
    vote_type = VoteType.objects.get(id=internal_id_from_model_and_external_id(VoteType, request.data['vote_type']))
    if vote_type:
      vote_result = post.vote(request.user, vote_type)
      if vote_result == 'ok':
        return Response({'success': "Voto añadido"}, status=status.HTTP_200_OK)
      elif vote_result == 'self_vote':
        return Response({'error': 'No puedes votarte a ti mismo'}, status=status.HTTP_403_FORBIDDEN)
      else:
        return Response({'error': 'Ya has votado este post antes'}, status=status.HTTP_403_FORBIDDEN)
    else:
      return Response({'error': 'No existe este tipo de voto'}, status=status.HTTP_400_BAD_REQUEST)
  
  def get_throttles(self):
    if self.action in ['delete', 'partial_update']:
        self.throttle_scope = 'posts'
    else:
        self.throttle_scope = None
    return super().get_throttles()

class ForumSettings(APIView):
  """
  View to list all forum settings (such as votes).
  """

  permission_classes = [permissions.IsAuthenticatedOrReadOnly]

  def get(self, request, format=None):
    """
    Return all data
    """
    vote_types = serializers.VoteTypeSerializer(VoteType.objects.all(), many=True, context={'request': request})
    return Response({'vote_types': vote_types.data})