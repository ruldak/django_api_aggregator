from rest_framework import permissions
from rest_framework_api_key.permissions import BaseHasAPIKey
from user.models import UserAPIKey

class HasUserAPIKey(BaseHasAPIKey):
    model = UserAPIKey

class IsAPIKeyOwner(permissions.BasePermission):
    """Permission untuk memastikan API key milik user yang sesuai"""

    def has_permission(self, request, view):
        # Dapatkan API key dari header
        key = request.META.get("HTTP_AUTHORIZATION", "").split()
        if not key or key[0] != "Api-Key":
            return False

        try:
            api_key = auth_header.split()[1]  # Extract key-nya
            user_api_key = UserAPIKey.objects.get_from_key(api_key)

            # Validasi tambahan
            if user_api_key.revoked:
                return False

            if not user_api_key.user.is_active:
                return False

            # SET USER di request - INI YANG PENTING!
            request.user = user_api_key.user
            return True
        except UserAPIKey.DoesNotExist:
            return False
