from django.shortcuts import render
from .models import User, ForumCategory
from rest_framework import viewsets
from django.contrib.staticfiles import finders
from django.templatetags.static import static

from . import serializers

from rest_framework import permissions

# Create your views here.
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

class ForumCategoryViewSet(viewsets.ModelViewSet):
  queryset = ForumCategory.objects.all()
  permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
  serializer_class = serializers.ForumCategorySerializer