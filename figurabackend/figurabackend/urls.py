"""figurabackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from FigureSite.auth import CustomPasswordResetView
from rest_auth.registration.views import RegisterView, VerifyEmailView
from rest_auth.views import (
    LoginView, LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)

from django.middleware.csrf import get_token

from rest_framework_simplejwt.views import (
    TokenRefreshView
)

from FigureSite.auth import TokenObtainPairView

@method_decorator(csrf_exempt, name='dispatch')
class VerifyEmailViewNoCSRF(VerifyEmailView):
    pass

urlpatterns = [
    path('djadmin/', admin.site.urls),
    path('api/mfc/', include('mfc.urls')),
    path('api/', include('FigureSite.urls')),
    path('api/auth/register/', RegisterView.as_view()),
    path('api/auth/register/verify-email/', VerifyEmailViewNoCSRF.as_view()),
    path('api/auth/change_password/', csrf_exempt(PasswordChangeView.as_view())),
    path('api/auth/password_reset/', CustomPasswordResetView.as_view(), name='password_reset_confirm'),
    path('api/auth/password_reset/verify/', csrf_exempt(PasswordResetConfirmView.as_view())),
    path('api/auth/login/', TokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)