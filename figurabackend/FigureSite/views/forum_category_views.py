from rest_framework import viewsets
from rest_framework import permissions

from dry_rest_permissions.generics import DRYPermissions

from FigureSite.models import ForumCategory
from FigureSite import serializers


class ForumCategoryViewSet(viewsets.ModelViewSet):
  queryset = ForumCategory.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.ForumCategorySerializer
  lookup_field = 'slug'

  def filter_queryset(self, queryset):
    queryset = super(ForumCategoryViewSet, self).filter_queryset(queryset)
    return queryset.order_by('order')