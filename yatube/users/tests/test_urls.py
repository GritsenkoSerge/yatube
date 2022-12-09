from http import HTTPStatus

from django.test import TestCase


class UsersURLTests(TestCase):
    def test_signup_url_exists_at_desired_location(self):
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_url_uses_correct_template(self):
        response = self.client.get('/auth/signup/')
        self.assertTemplateUsed(response, 'users/signup.html')
