from django.urls import path
from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'forum/categories', views.ForumCategoryViewSet)
router.register(r'forum', views.ForumViewSet)
router.register(r'thread', views.ThreadViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'reports', views.ReportViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('settings/', views.ForumSettings.as_view())
]
