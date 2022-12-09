from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewsTests(TestCase):
    def test_signup_url_uses_correct_template(self):
        response = self.client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')
