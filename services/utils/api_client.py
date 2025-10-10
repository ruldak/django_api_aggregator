# services/api_client.py
import requests
from datetime import datetime
import time
import logging
from .cache_service import file_cache
from services.models import APIRequestLog, ThirdPartyService

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        # Setup retry strategy
        self.retry_status_codes = [429, 500, 502, 503, 504]

    def make_request(self, service_name, endpoint, params=None, user=None, use_cache=True, timeout=15):
        # Generate cache key yang lebih robust
        cache_params = params.copy() if params else {}
        # Remove sensitive data dari cache key
        cache_params.pop('api_key', None)
        cache_params.pop('token', None)

        param_string = str(sorted(cache_params.items())) if cache_params else ""
        cache_key = f"{service_name}_{endpoint}_{hash(param_string)}"

        # Check cache first
        if use_cache:
            cached_data = file_cache.get(cache_key)
            if cached_data:
                self._log_request(service_name, endpoint, 200, 0, user, cached=True)
                return cached_data

        # Get service config dengan encrypted key
        try:
            service = ThirdPartyService.objects.get(name=service_name, is_active=True)
            decrypted_api_key = service.get_api_key()

            if not decrypted_api_key:
                return {"error": f"API key untuk {service_name} tidak valid atau tidak bisa didecrypt"}

        except ThirdPartyService.DoesNotExist:
            return {"error": f"Service {service_name} tidak ditemukan atau tidak aktif"}

        start_time = time.time()

        try:
            # Prepare headers dengan decrypted API key
            headers = {
                'User-Agent': 'API-Gateway/1.0',
                'Accept': 'application/json'
            }

            params = params or {}

            if service_name == 'openweather':
                params['appid'] = decrypted_api_key
            elif service_name == 'newsapi':
                headers['X-Api-Key'] = decrypted_api_key
            elif service_name == 'coingecko':
                params['x_cg_demo_api_key'] = decrypted_api_key
            elif service_name == 'exchangeRate':
                endpoint = f"/{decrypted_api_key}{endpoint}"
            elif service_name == 'github':
                if decrypted_api_key and decrypted_api_key != 'YOUR_GITHUB_TOKEN':
                    headers['Authorization'] = f'token {decrypted_api_key}'

            response = self._make_request_with_retry(
                service.api_endpoint + endpoint,
                params=params,
                headers=headers,
                timeout=timeout
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            # Transform response berdasarkan service
            # transformed_data = self._transform_response(service_name, response.json())

            # Cache dengan timeout yang appropriate
            cache_timeout = self._get_cache_timeout(service_name)
            file_cache.set(cache_key, response, cache_timeout)

            # Log successful request
            self._log_request(service_name, endpoint, response.status_code, response_time_ms, user)

            return response.json()

        except requests.Timeout:
            response_time_ms = int((time.time() - start_time) * 1000)
            self._log_request(service_name, endpoint, 408, response_time_ms, user)
            return {"error": f"Request timeout untuk {service_name}"}

        except requests.RequestException as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            self._log_request(service_name, endpoint, 500, response_time_ms, user)
            logger.error(f"API request failed untuk {service_name}: {str(e)}")
            if 'url' in str(e):
                return {"error": f"API request failed: Client Error"}
            return {"error": f"API request failed: {str(e)}"}

    def _get_cache_timeout(self, service_name):
        """Return cache timeout berdasarkan jenis service"""
        timeouts = {
            'openweather': 600,
            'newsapi': 300,
            'github': 1800,
            'coingecko': 1800,
        }
        return timeouts.get(service_name, 300)

    def _make_request_with_retry(self, url, params=None, headers=None, timeout=15, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )

                if response.status_code in self.retry_status_codes:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response

            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) + 1
                time.sleep(wait_time)


    def _log_request(self, service_name, endpoint, status_code, response_time, user, cached=False):
        try:
            service = ThirdPartyService.objects.get(name=service_name)
            APIRequestLog.objects.create(
                service=service,
                user=user,
                endpoint_called=endpoint,
                response_status=status_code,
                response_time_ms=response_time,
                cached=cached
            )
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")
