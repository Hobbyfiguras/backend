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
from . import serializers

from rest_framework import permissions

class UserPostPagination(PageNumberPagination):
    page_size = 30
class UserViewSet(viewsets.ModelViewSet):
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
class ForumCategoryViewSet(viewsets.ModelViewSet):
  queryset = ForumCategory.objects.all()
  permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
  serializer_class = serializers.ForumCategorySerializer
  lookup_field = 'slug'

class ForumPagination(PageNumberPagination):
    page_size = 30

class ForumViewSet(viewsets.ModelViewSet):
  queryset = Forum.objects.all()
  permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
  serializer_class = serializers.FullForumSerializer
  lookup_field = 'slug'

  @action(detail=True, pagination_class=ForumPagination)
  def threads(self, request, slug=None):
    forum = self.get_object()
    page = self.paginate_queryset(forum.threads.all().order_by('modified'))
    threads = {}
    if page is not None:
      serializer = serializers.ThreadSerializer(page, many=True, context={'request': request})
      threads = self.get_paginated_response(serializer.data).data
    else:
      threads = serializers.ThreadSerializer(forum.threads, many=True, context={'request': request}).data

    return Response({**{'threads': threads}, **serializers.BasicForumSerializer(forum).data})

class ThreadPagination(PageNumberPagination):
    page_size = 30

class ThreadViewSet(viewsets.ModelViewSet):
  queryset = Thread.objects.all()
  permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
  serializer_class = serializers.ThreadSerializer
  pagination_class = ThreadPagination

  def retrieve(self, request, pk=None):
    thread = self.get_object()
    page = self.paginate_queryset(thread.posts.all().order_by('modified'))
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
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostsPagination(PageNumberPagination):
    page_size = 10

class PostViewSet(viewsets.ModelViewSet):
  queryset = Post.objects.all()
  pagination_class = PostsPagination
  permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
  serializer_class = serializers.PostSerializer

  