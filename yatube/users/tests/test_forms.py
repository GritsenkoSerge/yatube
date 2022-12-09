from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UsersFormsTests(TestCase):
    def test_user_create_correct(self):
        users_count = User.objects.count()
        form_data = {
            'username': 'username',
            'password1': 'ltD9vVjF',
            'password2': 'ltD9vVjF',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        # проверяем корректность редиректа
        self.assertRedirects(response, reverse('posts:index'))
        # проверяем, что кол-во пользователей увеличилось
        self.assertEqual(User.objects.count(), users_count + 1)
        # проверяем, что создался пользователь с заданным именем
        self.assertTrue(
            User.objects.filter(username=form_data['username']).exists()
        )
