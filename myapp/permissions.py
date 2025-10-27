from rest_framework.permissions import BasePermission
from django.conf import settings

class IsAdminWithSecretPin(BasePermission):
    """
    Custom permission to allow access only if a valid secret PIN 
    is provided in the 'X-Admin-Pin' header.
    """
    def has_permission(self, request, view):
        # 1. Check if the PIN is configured (safety check)
        secret_pin = getattr(settings, 'ADMIN_SECRET_PIN', None)
        if not secret_pin:
            return False

        # 2. Get the PIN from the request headers
        # We expect the admin app to send this header: X-Admin-Pin: 26344
        provided_pin = request.headers.get('X-Admin-Pin')

        # 3. Compare the provided PIN with the secret
        # Use constant time comparison for production security (not shown here 
        # for maximum simplicity, but highly recommended)
        return provided_pin == secret_pin