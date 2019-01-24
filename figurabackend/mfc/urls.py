from django.urls import path
from django.conf.urls import url, include


from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'figures', views.FiguresViewSet, base_name='figures')
router.register(r'items', views.MFCItemViewSet, base_name='items')
router.register(r'pictures', views.PicturesViewset, base_name='pictures')

urlpatterns = [
    path('', include(router.urls)),
]
