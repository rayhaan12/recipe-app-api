from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@mail.com', name='Test Name', password='testpass'):
    """Create a smaple user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'rayhaan@mail.com'
        name = 'Rayhaan'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            name=name,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for the new user has been normalized"""
        email = 'rayhaan@MAIL.COM'
        name = 'Rayhaan'
        user = get_user_model().objects.create_user(email, name, 'password123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Rayhaan', 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'rayhaan@mail.com',
            'Rayhaan',
            'password123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_new_user_invalid_name(self):
        """Test creating a user with no name raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                'rayhaan@mail.com',
                None,
                'test1234'
            )

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)
