
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from user.models import UserAPIKey

class UserViewsIntegrationTests(APITestCase):

    def test_register_user_success(self):
        """Uji registrasi user berhasil."""
        url = reverse('register_user')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newuser')

    def test_register_user_username_exists(self):
        """Uji registrasi user dengan username yang sudah ada."""
        User.objects.create_user(username='existinguser', password='password123')
        url = reverse('register_user')
        data = {
            'username': 'existinguser',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_api_key_authenticated(self):
        """Uji pembuatan API key untuk user yang terotentikasi."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=user)
        url = reverse('create-api-key')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('api_key', response.data)
        self.assertTrue(UserAPIKey.objects.filter(user=user).exists())

    def test_create_api_key_unauthenticated(self):
        """Uji pembuatan API key untuk user yang tidak terotentikasi."""
        url = reverse('create-api-key')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
