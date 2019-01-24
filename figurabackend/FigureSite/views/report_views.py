from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework.decorators import action

from dry_rest_permissions.generics import DRYPermissions

from FigureSite.models import Report
from FigureSite import serializers

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