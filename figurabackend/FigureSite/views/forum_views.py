from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import mixins
from rest_framework import filters

from dry_rest_permissions.generics import DRYPermissions

from FigureSite.models import Forum
from FigureSite import serializers

class ForumPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 20
    page_size_query_param = 'page_size'

class ForumViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Forum.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.FullForumSerializer
  lookup_field = 'slug'
  filter_backends = (filters.OrderingFilter,)
  ordering_fields = ('created',)

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
    filtered_queryset = filters.OrderingFilter().filter_queryset(request, forum.threads.all().order_by('-is_sticky', '-modified'), self)
    page = self.paginate_queryset(filtered_queryset)
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
    related_items = []
    if request.data['related_items']:
      for item in request.data['related_items']:
        db_item = MFCItem.get_or_fetch_mfc_item(item)
        if db_item:
          related_items.append(db_item)
    
    thread_serializer = serializers.CreateThreadSerializer(data=request.data)
    if thread_serializer.is_valid() and request.data['content']:
      thread = thread_serializer.save()
      post_data = {
        'thread': thread.id,
        'creator': request.user.id,
        'content': request.data['content'],
        'nsfw': request.data['nsfw']
      }
      thread.related_items
      post_serializer = serializers.CreatePostSerializer(data=post_data)
      if post_serializer.is_valid():
        post_serializer.save()
        thread.related_items.set(related_items)
        thread.save()
        data = thread_serializer.data
        data['slug'] = thread.slug
        data['id'] = external_id_from_model_and_internal_id(Thread, thread.id)
        return Response(data, status=status.HTTP_201_CREATED)
      else:
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    else:
      return Response(thread_serializer.errors, status=status.HTTP_400_BAD_REQUEST)