from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
import jwt


class SimpleUser:
    def __init__(self, user_id, username=None, email=None):
        # Keep both id and _id for compatibility with existing code
        self.id = user_id
        self.pk = user_id
        self._id = user_id
        self.username = username
        self.email = email

    @property
    def is_authenticated(self):
        return True


class MongoJWTAuthentication(BaseAuthentication):
    """
    Custom authentication that decodes HS256 JWTs issued by the app's
    generate_access_token helper. It returns a SimpleUser-like object so
    existing views that expect `request.user.id` / `request.user._id` work.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token = parts[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            # Don't block AllowAny endpoints (like token refresh) when the
            # access token has expired. Returning None lets DRF continue
            # without an authenticated user; protected endpoints will still
            # enforce authentication via permissions.
            return None
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

        # Ensure token is an access token
        if payload.get('token_type') != 'access':
            raise exceptions.AuthenticationFailed('Given token not valid for this token type')

        user_id = payload.get('user_id')
        if not user_id:
            raise exceptions.AuthenticationFailed('Token payload missing user identifier')

        user = SimpleUser(user_id=user_id, username=payload.get('username'), email=payload.get('email'))
        return (user, None)
