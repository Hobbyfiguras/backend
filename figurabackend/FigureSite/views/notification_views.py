from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework_serializer_extensions.views import ExternalIdViewMixin
from rest_framework import mixins
from rest_framework.decorators import action

from dry_rest_permissions.generics import DRYPermissions

from FigureSite.models import Notification
from FigureSite import serializers

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