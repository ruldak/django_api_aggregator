import os
import json
from datetime import datetime, timedelta
from django.conf import settings
import hashlib

class FileCache:
    def __init__(self):
        self.cache_dir = os.path.join(settings.BASE_DIR, 'api_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_file_path(self, key):
        # Hash key untuk nama file yang aman
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")

    def set(self, key, data, timeout=3600):
        file_path = self._get_file_path(key)
        cache_data = {
            'data': data,
            'expires': (datetime.now() + timedelta(seconds=timeout)).timestamp()
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(cache_data, f)
            return True
        except Exception:
            return False

    def get(self, key):
        file_path = self._get_file_path(key)

        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                cache_data = json.load(f)

            # Check expiration
            if datetime.now().timestamp() > cache_data['expires']:
                os.remove(file_path)
                return None

            return cache_data['data']
        except Exception:
            return None

    def delete(self, key):
        file_path = self._get_file_path(key)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False

# Singleton instance
file_cache = FileCache()
