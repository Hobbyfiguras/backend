from django.shortcuts import render
import requests
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from . import mfc_api

class FiguresViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    @action(methods=['get'], detail=False)
    def search(self, request):
      keywords = request.query_params.get('keywords', '')
      page = request.query_params.get('page', 1)
      print(keywords)
      response = mfc_api.figure_search(keywords, page)
      return Response(response.json())

class PicturesViewset(viewsets.ViewSet):
    @action(methods=['get'], detail=False)
    def search(self, request):
      username = request.query_params.get('username', '')
      page = request.query_params.get('page', 1)
      response = mfc_api.get_pictures(username, page)
      return Response(response.json())
