
from django.test import TestCase
from django.contrib.auth.models import User
from user.serializers import RegisterSerializer

class RegisterSerializerTests(TestCase):

    def test_register_serializer_valid(self):
        """Uji serializer registrasi dengan data yang valid."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, data['username'])

    def test_register_serializer_invalid_password(self):
        """Uji serializer registrasi dengan password yang terlalu pendek."""
        data = {
            'username': 'testuser',
            'password': '123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_password_is_write_only(self):
        """Uji bahwa field password adalah write-only."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        # Dapatkan representasi serializer dari user instance
        user_serializer = RegisterSerializer(instance=user)
        self.assertNotIn('password', user_serializer.data)
