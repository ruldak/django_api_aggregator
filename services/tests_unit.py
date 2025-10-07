
import os
import json
import time
import requests
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from services.utils.cache_service import FileCache
from services.utils.encryption_service import encryption_service
from services.models import ThirdPartyService, APIRequestLog
from services.utils.api_client import APIClient

# Gunakan direktori cache sementara untuk pengujian
TEST_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'test_cache')

@override_settings(BASE_DIR=os.path.dirname(os.path.dirname(__file__)))
class FileCacheTests(TestCase):
    def setUp(self):
        # Pastikan direktori cache pengujian ada dan kosong
        os.makedirs(TEST_CACHE_DIR, exist_ok=True)
        self.clear_cache_dir()
        
        # Ganti cache_dir pada instance FileCache
        self.cache = FileCache()
        self.cache.cache_dir = TEST_CACHE_DIR

    def tearDown(self):
        # Bersihkan direktori cache setelah pengujian
        self.clear_cache_dir()
        os.rmdir(TEST_CACHE_DIR)

    def clear_cache_dir(self):
        for filename in os.listdir(TEST_CACHE_DIR):
            os.remove(os.path.join(TEST_CACHE_DIR, filename))

    def test_set_and_get_cache(self):
        """Uji menyimpan dan mengambil data dari cache."""
        key = "test_key"
        data = {"message": "Hello, World!"}
        
        # Set data ke cache
        self.assertTrue(self.cache.set(key, data, timeout=60))
        
        # Verifikasi file cache dibuat
        file_path = self.cache._get_file_path(key)
        self.assertTrue(os.path.exists(file_path))
        
        # Get data dari cache
        cached_data = self.cache.get(key)
        self.assertEqual(cached_data, data)

    def test_get_non_existent_key(self):
        """Uji mengambil data untuk kunci yang tidak ada."""
        cached_data = self.cache.get("non_existent_key")
        self.assertIsNone(cached_data)

    def test_cache_expiration(self):
        """Uji bahwa cache kedaluwarsa dengan benar."""
        key = "expired_key"
        data = {"message": "This will expire"}
        
        # Set cache dengan timeout 1 detik
        self.cache.set(key, data, timeout=1)
        
        # Tunggu hingga kedaluwarsa
        time.sleep(1.1)
        
        # Coba get data, harusnya None dan file dihapus
        cached_data = self.cache.get(key)
        self.assertIsNone(cached_data)
        
        file_path = self.cache._get_file_path(key)
        self.assertFalse(os.path.exists(file_path))

    def test_delete_cache(self):
        """Uji menghapus item dari cache."""
        key = "delete_key"
        data = {"message": "Data to be deleted"}
        
        self.cache.set(key, data)
        file_path = self.cache._get_file_path(key)
        self.assertTrue(os.path.exists(file_path))
        
        # Hapus cache
        self.assertTrue(self.cache.delete(key))
        
        # Verifikasi file tidak ada lagi
        self.assertFalse(os.path.exists(file_path))
        self.assertIsNone(self.cache.get(key))


class EncryptionServiceTests(TestCase):
    def test_encrypt_decrypt(self):
        """Uji enkripsi dan dekripsi teks."""
        original_text = "my_secret_api_key"
        
        # Enkripsi
        encrypted_text = encryption_service.encrypt(original_text)
        self.assertIsNotNone(encrypted_text)
        self.assertNotEqual(original_text, encrypted_text)
        
        # Dekripsi
        decrypted_text = encryption_service.decrypt(encrypted_text)
        self.assertEqual(original_text, decrypted_text)

    def test_decrypt_invalid_token(self):
        """Uji dekripsi dengan token yang tidak valid."""
        invalid_token = "invalid_token_string"
        decrypted_text = encryption_service.decrypt(invalid_token)
        self.assertIsNone(decrypted_text)

    def test_encrypt_empty_string(self):
        """Uji enkripsi string kosong."""
        encrypted = encryption_service.encrypt("")
        self.assertIsNone(encrypted)
        
    def test_decrypt_none(self):
        """Uji dekripsi nilai None."""
        self.assertIsNone(encryption_service.decrypt(None))


@patch('services.models.encryption_service')
class ThirdPartyServiceModelTests(TestCase):
    def test_set_and_get_api_key(self, mock_encryption_service):
        """Uji set_api_key mengenkripsi dan get_api_key mendekripsi."""
        service = ThirdPartyService(name="Test Service")
        plain_key = "plain_text_key_123"
        encrypted_key = "encrypted_key_abc"

        mock_encryption_service.encrypt.return_value = encrypted_key
        mock_encryption_service.decrypt.return_value = plain_key

        service.set_api_key(plain_key)
        
        mock_encryption_service.encrypt.assert_called_once_with(plain_key)
        self.assertEqual(service.api_key, encrypted_key)

        decrypted_key = service.get_api_key()

        mock_encryption_service.decrypt.assert_called_once_with(encrypted_key)
        self.assertEqual(decrypted_key, plain_key)

    def test_save_encrypts_raw_api_key(self, mock_encryption_service):
        """Uji bahwa metode save() mengenkripsi api_key yang mentah."""
        plain_key = "raw_key_to_be_saved"
        encrypted_key = "encrypted_version_of_raw_key"

        mock_encryption_service.decrypt.side_effect = Exception("Invalid Token")
        mock_encryption_service.encrypt.return_value = encrypted_key

        service = ThirdPartyService(
            name="Saving Test",
            api_endpoint="http://example.com",
            api_key=plain_key
        )
        service.save()

        mock_encryption_service.decrypt.assert_called_once_with(plain_key)
        mock_encryption_service.encrypt.assert_called_once_with(plain_key)
        self.assertEqual(service.api_key, encrypted_key)

    def test_save_does_not_reencrypt(self, mock_encryption_service):
        """Uji bahwa metode save() tidak mengenkripsi ulang kunci yang sudah terenkripsi."""
        encrypted_key = "already_encrypted_key"

        mock_encryption_service.decrypt.side_effect = None
        mock_encryption_service.decrypt.return_value = "some_decrypted_value"

        service = ThirdPartyService(
            name="No Re-encrypt Test",
            api_endpoint="http://example.com",
            api_key=encrypted_key
        )
        service.save()

        mock_encryption_service.decrypt.assert_called_once_with(encrypted_key)
        mock_encryption_service.encrypt.assert_not_called()
        self.assertEqual(service.api_key, encrypted_key)


@patch('services.utils.api_client.APIRequestLog')
@patch('requests.Session.get')
@patch('services.utils.api_client.file_cache')
@patch('services.utils.api_client.ThirdPartyService')
class APIClientTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser')

    def test_make_request_returns_cached_data(self, mock_service_model, mock_cache, mock_session_get, mock_log):
        """Uji bahwa make_request mengembalikan data dari cache jika tersedia."""
        mock_cache.get.return_value = {'data': 'cached_response'}
        
        response = self.client.make_request('test_service', '/endpoint', user=self.user)
        
        self.assertEqual(response, {'data': 'cached_response'})
        mock_cache.get.assert_called_once()
        mock_session_get.assert_not_called()
        mock_log.objects.create.assert_called_once()

    def test_make_request_fetches_from_api_and_caches(self, mock_service_model, mock_cache, mock_session_get, mock_log):
        """Uji permintaan API ketika data tidak ada di cache."""
        mock_cache.get.return_value = None
        
        mock_service = MagicMock()
        mock_service.api_endpoint = 'http://api.example.com'
        mock_service.get_api_key.return_value = 'decrypted_key'
        mock_service_model.objects.get.return_value = mock_service
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'live_response'}
        mock_session_get.return_value = mock_response

        response = self.client.make_request('openweather', '/weather', params={'city': 'London'}, user=self.user)

        self.assertEqual(response, {'data': 'live_response'})
        mock_cache.get.assert_called_once()
        mock_service_model.objects.get.assert_any_call(name='openweather', is_active=True)
        mock_session_get.assert_called_once()
        mock_cache.set.assert_called_once()
        mock_log.objects.create.assert_called_once()

    def test_service_not_found(self, mock_service_model, mock_cache, mock_session_get, mock_log):
        """Uji penanganan ketika service tidak ditemukan."""
        mock_cache.get.return_value = None
        
        class MockDoesNotExist(Exception): pass
        mock_service_model.DoesNotExist = MockDoesNotExist
        mock_service_model.objects.get.side_effect = mock_service_model.DoesNotExist

        response = self.client.make_request('unknown_service', '/endpoint')
        
        self.assertEqual(response, {"error": "Service unknown_service tidak ditemukan atau tidak aktif"})
        mock_session_get.assert_not_called()

    def test_request_timeout(self, mock_service_model, mock_cache, mock_session_get, mock_log):
        """Uji penanganan timeout request."""
        mock_cache.get.return_value = None
        
        mock_service = MagicMock()
        mock_service.api_endpoint = 'http://api.example.com'
        mock_service.get_api_key.return_value = 'decrypted_key'
        mock_service_model.objects.get.return_value = mock_service
        
        mock_session_get.side_effect = requests.Timeout

        response = self.client.make_request('github', '/users/test', user=self.user)

        self.assertEqual(response, {"error": "Request timeout untuk github"})
        mock_log.objects.create.assert_called_once()
