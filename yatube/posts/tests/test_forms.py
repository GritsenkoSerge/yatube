import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFormsTests.user)

    def test_post_create_correct(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostsFormsTests.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test_post_create_correct',
            'group': PostsFormsTests.group.id,
            'author': PostsFormsTests.user.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # проверяем корректность редиректа
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': PostsFormsTests.user.username
        }))
        # проверяем, что кол-во постов увеличилось
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # проверяем, что создался пост с заданным текстом, группой и картинкой
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=form_data['author'],
                image='posts/small.gif',
            ).exists()
        )

    def test_post_edit_correct(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small_edit.gif',
            content=PostsFormsTests.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test_post_edit_correct',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': PostsFormsTests.post.id
            }),
            data=form_data,
            follow=True,
        )
        # проверяем корректность редиректа
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': PostsFormsTests.post.id
        }))
        # проверяем, что кол-во постов не изменилось
        self.assertEqual(Post.objects.count(), posts_count)
        # проверяем, что у поста изменился текст и картинка на заданные
        self.assertTrue(
            Post.objects.filter(
                id=PostsFormsTests.post.id,
                text=form_data['text'],
                image='posts/small_edit.gif',
            ).exists()
        )
