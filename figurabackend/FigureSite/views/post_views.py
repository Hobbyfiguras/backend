from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework_serializer_extensions.views import ExternalIdViewMixin
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_serializer_extensions.utils import internal_id_from_model_and_external_id
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions

from django.http import Http404
from django.utils import timezone

from FigureSite.models import Post, VoteType
from FigureSite import serializers

class PostsPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10
    page_size_query_param = 'page_size'

class PostViewSet(ExternalIdViewMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = Post.objects.all()
  pagination_class = PostsPagination
  serializer_class = serializers.PostSerializer
  permission_classes = (DRYPermissions,)

  def filter_queryset(self, queryset):
    queryset = super(PostViewSet, self).filter_queryset(queryset)
    return queryset.order_by('-created')

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