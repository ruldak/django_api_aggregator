from django.core.management.base import BaseCommand
import os
import glob
from datetime import datetime
from gateway.services.cache_service import FileCache

class Command(BaseCommand):
    help = 'Clean up expired cache files'

    def handle(self, *args, **options):
        cache = FileCache()
        cache_dir = cache.cache_dir

        deleted_count = 0
        for cache_file in glob.glob(os.path.join(cache_dir, "*.cache")):
            try:
                # Coba baca file untuk check expiration
                with open(cache_file, 'rb') as f:
                    import pickle
                    cache_data = pickle.load(f)

                if datetime.now().timestamp() > cache_data['expires']:
                    os.remove(cache_file)
                    deleted_count += 1
            except:
                # Jika file corrupt, delete saja
                try:
                    os.remove(cache_file)
                    deleted_count += 1
                except:
                    pass

        self.stdout.write(f"Deleted {deleted_count} expired cache files")
