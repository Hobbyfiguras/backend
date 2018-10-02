from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication, JWTAuthentication
import json
from django.utils.six import text_type
from allauth.account.models import EmailAddress
from rest_framework import serializers
from FigureSite.models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken
from django.db import close_old_connections
from django.contrib.auth.models import AnonymousUser

class CustomTokenObtainSerializer(TokenObtainSerializer):
    def validate(self, attrs):
        u = User.objects.filter(email__iexact=attrs[self.username_field]).first()
        username = attrs[self.username_field]
        if u:
            username = u.username
        self.user = authenticate(**{
            self.username_field: username,
            'password': attrs['password'],
        })

        # Prior to Django 1.10, inactive users could be authenticated with the
        # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
        # prevents inactive users from authenticating.  App designers can still
        # allow inactive users to authenticate by opting for the new
        # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
        # users from authenticating to enforce a reasonable policy and provide
        # sensible backwards compatibility with older Django versions.

        if self.user is None or not self.user.is_active:
            raise serializers.ValidationError(
                _('No hemos encontrado una cuenta con esos credenciales'),
            )

        if not EmailAddress.objects.filter(user=self.user, verified=True).exists() and not self.user.is_staff:
            raise serializers.ValidationError(
                _('Tienes que verificar el correo antes'),
            )

        return {}

class CustomTokenObtainPairSerializer(CustomTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = text_type(refresh)
        data['access'] = text_type(refresh.access_token)

        return data

class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = CustomTokenObtainPairSerializer

token_obtain_pair = TokenObtainPairView.as_view()

class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        if scope['query_string']:
            query_string = scope['query_string'].decode('utf-8')
            if query_string.startswith('token='):
                try:
                    token = query_string.replace('token=', '')
                    auth = JWTAuthentication()
                    validated_token = auth.get_validated_token(token)
                    scope['user'] = auth.get_user(validated_token)
                    close_old_connections()
                except InvalidToken:
                    scope['user'] = AnonymousUser()
        return self.inner(scope)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))