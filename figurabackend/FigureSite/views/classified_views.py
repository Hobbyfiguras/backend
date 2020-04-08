
from dry_rest_permissions.generics import DRYPermissions
from rest_framework_serializer_extensions.utils import external_id_from_model_and_internal_id
from rest_framework_serializer_extensions.views import ExternalIdViewMixin
from rest_framework import mixins
from FigureSite import serializers
from rest_framework import viewsets
from FigureSite.models import ClassifiedAD
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

class ClassifiedADViewSet(ExternalIdViewMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = ClassifiedAD.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.ClassifiedADSerializer
  @action(detail=False, methods=['post'])
  def create_ad(self, request):
    request.data['creator'] = request.user.id
    print(request.data)

    serializer = serializers.CreateClassifiedADSerializer(data=request.data)
    if serializer.is_valid():
      ad = serializer.save()
      for i in range(int(request.data['image_count'])):
        image_request_data = {
          'ad': ad.id,
          'image': request.data['image' + str(i)],
          'primary': i == 0
        }
        image_serializer = serializers.CreateclassifiedImageSerializer(data=image_request_data)
        if not image_serializer.is_valid():
          return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
          image_serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    """
    serializer = serializers.CreatePostSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      thread.modified = timezone.now()
      thread.save()
"""
