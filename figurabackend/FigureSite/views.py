from django.shortcuts import render
from .models import User
from rest_framework import viewsets

from . import serializers

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  lookup_field = 'username'
  def get_serializer_class(self):
    if self.request.user.is_staff or self.kwargs.get('pk') == 'current':
      return serializers.FullUserSerializer
    return serializers.PublicUserSerializer

  def get_object(self):
    pk = self.kwargs.get('username')
    if pk == "current":
      return self.request.user

    return super(UserViewSet, self).get_object()
