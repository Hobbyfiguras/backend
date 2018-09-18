from django.shortcuts import render
from .models import User, ForumCategory, Forum, Thread, Post
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
from rest_framework_serializer_extensions.utils import external_id_from_model_and_internal_id
from dry_rest_permissions.generics import DRYPermissions

class UserPostPagination(PageNumberPagination):
    page_size = 10
class UserViewSet(viewsets.ModelViewSet, EagerLoadingMixin):
  queryset = User.objects.all()
  lookup_field = 'username'

  permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
  def get_serializer_class(self):
    if self.request.user.is_staff or self.kwargs.get('pk') == 'current':
      return serializers.FullUserSerializer
    return serializers.PublicUserSerializer

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
class ForumCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = ForumCategory.objects.all()
  permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
  serializer_class = serializers.ForumCategorySerializer
  lookup_field = 'slug'

class ForumPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 20
    page_size_query_param = 'page_size'

class ForumViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Forum.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.FullForumSerializer
  lookup_field = 'slug'

  @action(detail=True, pagination_class=ForumPagination)
  def threads(self, request, slug=None):
    forum = self.get_object()
    page = self.paginate_queryset(forum.threads.all().order_by('-is_sticky', '-modified'))
    threads = {}
    if page is not None:
      serializer = serializers.ThreadSerializer(page, many=True, context={'request': request})
      threads = self.get_paginated_response(serializer.data).data
    else:
      threads = serializers.ThreadSerializer(forum.threads.all().order_by('-modified'), many=True, context={'request': request}).data

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
        data = thread_serializer.data
        data['slug'] = thread.slug
        data['id'] = external_id_from_model_and_internal_id(Thread, thread.id)
        return Response(data, status=status.HTTP_201_CREATED)
      else:
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    else:
      return Response(thread_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ThreadPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20
    page_size_query_param = 'page_size'

class ThreadViewSet(ExternalIdViewMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Thread.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.ThreadSerializer
  pagination_class = ThreadPagination

  def filter_queryset(self, queryset):
    queryset = super(ThreadViewSet, self).filter_queryset(queryset)
    return queryset.order_by('-created')

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
    return Response({**{'posts': posts}, **serializers.ThreadSerializer(thread).data})

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
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def get_throttles(self):
      if self.action == 'create_post':
          self.throttle_scope = 'posts'
      else:
          self.throttle_scope = None
      return super().get_throttles()

class PostsPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10
    page_size_query_param = 'page_size'

class PostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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
    serializer.save()
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

  def get_throttles(self):
    if self.action in ['delete', 'partial_update']:
        self.throttle_scope = 'posts'
    else:
        self.throttle_scope = None
    return super().get_throttles()