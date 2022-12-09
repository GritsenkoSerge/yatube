from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.public_urls = [
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
        ]
        cls.authorized_urls = [
            ('/create/', 'posts/create_post.html'),
        ]
        cls.authored_urls = [
            (
                f'/posts/{cls.post.id}/edit/',
                'posts/create_post.html'
            ),
        ]
        cls.nonexistent_url = ('/nonexistent/', 'core/404.html',)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.authorized_client_by_author = Client()
        self.authorized_client_by_author.force_login(PostsURLTests.author)
        cache.clear()

    def test_urls_exists_at_desired_location(self):
        """
        URL-адрес отвечает с соответствующим статусом.
        Неавторизованный клиент.
        """
        for path, _ in PostsURLTests.public_urls:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        Неавторизованный клиент.
        """
        for path, template in PostsURLTests.public_urls:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location_authorized(self):
        """
        URL-адрес отвечает с соответствующим статусом.
        Авторизованный клиент. Не автор поста.
        """
        for path, _ in self.authorized_urls:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_authorized(self):
        """
        URL-адрес использует соответствующий шаблон.
        Авторизованный клиент. Не автор поста.
        """
        for path, template in self.authorized_urls:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location_authorized_by_author(self):
        """
        URL-адрес отвечает с соответствующим статусом.
        Авторизованный клиент. Автор поста.
        """
        for path, _ in PostsURLTests.authored_urls:
            with self.subTest(path=path):
                response = self.authorized_client_by_author.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_authorized_by_author(self):
        """
        URL-адрес использует соответствующий шаблон.
        Авторизованный клиент. Автор поста.
        """
        for path, template in PostsURLTests.authored_urls:
            with self.subTest(path=path):
                response = self.authorized_client_by_author.get(path)
                self.assertTemplateUsed(response, template)

    def test_nonexistent_url_not_found(self):
        """
        Несуществующий URL-адрес выдает статус 404.
        Неавторизованный клиент.
        """
        response = self.client.get(PostsURLTests.nonexistent_url[0])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_nonexistent_url_uses_correct_template(self):
        """
        Несуществующий URL-адрес использует кастомный шаблон.
        Неавторизованный клиент.
        """
        response = self.client.get(PostsURLTests.nonexistent_url[0])
        self.assertTemplateUsed(response, PostsURLTests.nonexistent_url[1])
