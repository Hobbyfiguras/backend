from django.db.models import Q

from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework_serializer_extensions.views import ExternalIdViewMixin
from rest_framework import mixins

from dry_rest_permissions.generics import DRYPermissions

from FigureSite.models import PrivateMessage
from FigureSite import serializers

class PrivateMessagePagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20
    page_size_query_param = 'page_size'

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
    if read:
      return PrivateMessage.objects.filter(receiver=self.request.user, read=str2bool(read))
    elif self.request.query_params.get('sent', None):
      return PrivateMessage.objects.filter(creator=self.request.user)
    else:
      return PrivateMessage.objects.filter(Q(receiver=self.request.user) | Q(creator=self.request.user))

  def filter_queryset(self, queryset):
    queryset = super(PrivateMessageViewSet, self).filter_queryset(queryset)
    return queryset.order_by('-created')