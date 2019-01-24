from django.shortcuts import render
import requests
import json

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from . import mfc_api, mfc_parser

class MFCItemViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    def retrieve(self, request, pk=None):
      return Response(mfc_api.get_figure_data(pk))

class FiguresViewSet(viewsets.ViewSet):
  """
  A simple ViewSet for listing or retrieving users.
  """

  permission_classes = [permissions.AllowAny]
  @action(methods=['get'], detail=False)
  def search(self, request):
    keywords = request.query_params.get('keywords', '')
    page = request.query_params.get('page', 1)
    print(request)
    response = mfc_api.figure_search(keywords, page)
    return Response(response.json())
  
  def retrieve(self, request, pk=None):
    page = request.query_params.get('page', 1)
    items_per_page = 22
    return Response(mfc_parser.getUserFigures(pk, int(page), items_per_page))

class PicturesViewset(viewsets.ViewSet):
  permission_classes = [permissions.AllowAny]

  @action(methods=['get'], detail=False)
  def search(self, request):
    username = request.query_params.get('username', '')
    page = request.query_params.get('page', 1)
    response = mfc_api.get_pictures(username, page)
    return Response(response.json())

