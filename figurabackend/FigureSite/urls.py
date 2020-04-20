from django.urls import path
from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import user_views, thread_views, forum_category_views, forum_views, report_views, notification_views, private_message_views, post_views, forum_settings_views, classified_views
router = DefaultRouter()
router.register(r'users', user_views.UserViewSet)
router.register(r'forum/categories', forum_category_views.ForumCategoryViewSet)
router.register(r'forum', forum_views.ForumViewSet)
router.register(r'thread', thread_views.ThreadViewSet)
router.register(r'posts', post_views.PostViewSet)
router.register(r'reports', report_views.ReportViewSet)
router.register(r'private_messages', private_message_views.PrivateMessageViewSet)
router.register(r'notifications', notification_views.NotificationsViewSet, base_name='notifications')
#router.register(r'search/posts', views.PostSearchView, base_name="post-search")
router.register(r'search/threads', thread_views.ThreadSearchView, base_name="thread-search")
router.register(r'search/users', user_views.UserSearchView, base_name="user-search")
router.register(r'search/classifieds', classified_views.ClassifiedADSearchView, base_name="ad-search")
router.register(r'classifieds', classified_views.ClassifiedADViewSet, base_name="classified-ads")
urlpatterns = [
    path('', include(router.urls)),
    path('settings/', forum_settings_views.ForumSettings.as_view())
]
