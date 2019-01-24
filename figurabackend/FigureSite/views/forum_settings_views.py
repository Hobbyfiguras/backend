from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from dry_rest_permissions.generics import DRYPermissions

from FigureSite.models import VoteType
from FigureSite import serializers

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