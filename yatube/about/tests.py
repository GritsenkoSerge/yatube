from http import HTTPStatus

from django.test import TestCase


class AboutURLTests(TestCase):
    def test_urls_exists_at_desired_location(self):
        """URL-адрес отвечает со статусом HTTPStatus.OK."""
        addresses = [
            '/about/author/',
            '/about/tech/',
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
