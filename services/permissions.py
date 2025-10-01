from rest_framework_api_key.permissions import BaseHasAPIKey
from user.models import UserAPIKey

class HasAPIKey(BaseHasAPIKey):
    model = UserAPIKey

    def has_permission(self, request, view):
        has_key = super().has_permission(request, view)

        if not has_key:
            return False

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith("Api-Key "):
            return False

        try:
            key = self.get_key(request)
            print(f"key: {key}")
            user_api_key = UserAPIKey.objects.get_from_key(key)

            if user_api_key.revoked:
                return False

            return True
        except (UserAPIKey.DoesNotExist, IndexError):
            return False
