from django.core.management.base import BaseCommand
import os
import glob
import json
import pickle
from datetime import datetime
from services.utils.cache_service import FileCache

class Command(BaseCommand):
    help = 'Clean up expired cache files'

    def handle(self, *args, **options):
        cache = FileCache()
        cache_dir = cache.cache_dir

        deleted_count = 0
        # Handle new json cache files
        for cache_file in glob.glob(os.path.join(cache_dir, "*.json")):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)

                if datetime.now().timestamp() > cache_data['expires']:
                    os.remove(cache_file)
                    deleted_count += 1
            except (json.JSONDecodeError, KeyError):
                # If file is corrupt or doesn't have expires key, delete it
                try:
                    os.remove(cache_file)
                    deleted_count += 1
                except OSError:
                    pass
            except OSError:
                pass

        # Handle old pickle cache files
        for cache_file in glob.glob(os.path.join(cache_dir, "*.cache")):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)

                if datetime.now().timestamp() > cache_data['expires']:
                    os.remove(cache_file)
                    deleted_count += 1
            except (pickle.UnpicklingError, KeyError, EOFError):
                # If file is corrupt or doesn't have expires key, delete it
                try:
                    os.remove(cache_file)
                    deleted_count += 1
                except OSError:
                    pass
            except OSError:
                pass

        self.stdout.write(f"Deleted {deleted_count} expired cache files")
