from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.db.models.query import QuerySet
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Follow, Group, Post

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user2 = User.objects.create_user(username='user2')
        cls.follow_user = User.objects.create_user(username='follow_user')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='title',
            slug='slug2',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 1',
            group=cls.group,
            image='posts/small.gif'
        )
        cls.post2 = Post.objects.create(
            author=cls.user2,
            text='Тестовый пост 2',
            group=cls.group2,
            image='posts/small.gif'
        )
        Follow.objects.create(user=cls.user, author=cls.user2)
        Follow.objects.create(user=cls.user2, author=cls.user)
        cls.pages = [
            (reverse('posts:index'), 'posts/index.html', {
                'page_obj': Page
            }),
            (reverse('posts:group_list',
                     kwargs={'slug': 'slug'}), 'posts/group_list.html', {
                         'page_obj': Page,
                         'group': Group,
            }),
            (reverse('posts:profile',
                     kwargs={'username':
                             cls.user.username}), 'posts/profile.html', {
                                 'page_obj': Page,
                                 'posts_count': int,
                                 'author': User,
            }),
            (reverse('posts:post_detail',
                     kwargs={'post_id':
                             cls.post.id}), 'posts/post_detail.html', {
                                 'post': Post,
                                 'posts_count': int,
                                 'form': CommentForm,
                                 'comments': QuerySet,
            }),
            (reverse('posts:post_create'), 'posts/create_post.html', {
                'form': PostForm,
            }),
            (reverse('posts:post_edit',
                     kwargs={'post_id':
                             cls.post.id}), 'posts/create_post.html', {
                                 'form': PostForm,
                                 'is_edit': bool,
            }),
            (reverse('posts:follow_index'), 'posts/follow.html', {
                'page_obj': Page
            }),
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostsViewsTests.user2)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        Авторизованный клиент.
        """
        for reverse_name, template, _ in PostsViewsTests.pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """
        Страницы принимиают контескт с соответствующим словарем.
        Проверяется наличие, тип и картинка.
        Авторизованный клиент.
        """
        for page, _, context_items in PostsViewsTests.pages:
            response = self.authorized_client.get(page)
            for key, expected in context_items.items():
                with self.subTest(page=page, key=key):
                    self.assertIn(key, response.context)
                    value = response.context[key]
                    self.assertIsInstance(value, expected)
                    if expected == Post:
                        self.assertEqual(
                            value.image,
                            PostsViewsTests.post.image
                        )
                    if expected == Page:
                        self.assertGreater(len(value), 0)
                        self.assertIsInstance(value[0], Post)
                        self.assertEqual(
                            value[0].image,
                            PostsViewsTests.post.image
                        )

    def test_post_create_correct(self):
        post_group2_amount = Post.objects.filter(
            group=PostsViewsTests.group2
        ).count()
        post_user2_amount = Post.objects.filter(
            author=PostsViewsTests.user2
        ).count()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn('page_obj', response.context)
        post_following_amount = len(response.context['page_obj'])
        form_data = {
            'text': 'test_post_create_correct',
            'author': PostsViewsTests.user.id,
            'group': PostsViewsTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # проверяем корректность редиректа
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={
                    'username': PostsViewsTests.user.username
                }
            )
        )
        # проверяем, что первый пост на странице только что добавленный
        self.assertIn('page_obj', response.context)
        self.assertGreaterEqual(len(response.context['page_obj']), 1)
        self.assertEqual(
            response.context['page_obj'][0].text, form_data['text']
        )
        # проверяем, что пост появился на главной странице
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        self.assertGreaterEqual(len(response.context['page_obj']), 1)
        self.assertEqual(
            response.context['page_obj'][0].text, form_data['text']
        )
        # проверяем, что пост появился на странице группы
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                    'slug': PostsViewsTests.group.slug})
        )
        self.assertIn('page_obj', response.context)
        self.assertGreater(len(response.context['page_obj']), 0)
        self.assertEqual(
            response.context['page_obj'][0].text, form_data['text']
        )
        # проверяем, что пост не появился на странице другой группы
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostsViewsTests.group2.slug}))
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), post_group2_amount)
        # проверяем, что пост не появился на странице другого пользователя
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PostsViewsTests.user2.username
                }
            )
        )
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), post_user2_amount)
        # проверяем, что пост появился на странице подписчика
        response = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertIn('page_obj', response.context)
        self.assertGreater(len(response.context['page_obj']), 0)
        self.assertEqual(
            response.context['page_obj'][0].text, form_data['text']
        )
        # проверяем, что пост не появился на странице не подписчика
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn('page_obj', response.context)
        self.assertEqual(
            len(response.context['page_obj']),
            post_following_amount
        )

    def test_post_edit_correct(self):
        form_data = {
            'text': 'test_post_edit_correct',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': PostsViewsTests.post.id
                }
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostsViewsTests.post.id
                }
            )
        )

    def test_add_comment_correct(self):
        # комментировать посты может только авторизованный пользователь
        form_data = {'text': 'test_add_comment_correct', }
        add_comment_url = reverse(
            'posts:add_comment', kwargs={
                'post_id': PostsViewsTests.post.id
            }
        )
        response = self.client.post(
            add_comment_url,
            data=form_data,
            follow=True
        )
        # проверяем корректность редиректа
        self.assertRedirects(
            response, f'{reverse("users:login")}?next={add_comment_url}'
        )
        # создаем комментарий
        form_data = {'text': 'test_add_comment_correct', }
        response = self.authorized_client.post(
            add_comment_url,
            data=form_data,
            follow=True,
        )
        # проверяем корректность редиректа
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostsViewsTests.post.id
                }
            )
        )
        # проверяем, что первый комментарий на странице только что добавленный
        self.assertIn('comments', response.context)
        self.assertGreaterEqual(len(response.context['comments']), 1)
        self.assertEqual(
            response.context['comments'][0].text, form_data['text']
        )

    def test_index_page_cache(self):
        """Проверка работы кеша на главной странице."""
        cached_post = Post.objects.create(
            author=PostsViewsTests.user,
            text='Тестовый пост для проверки кеша',
        )
        # проверим, что пост появился после создания
        response = self.client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        self.assertGreater(len(response.context['page_obj']), 0)
        self.assertEqual(
            response.context['page_obj'][0].text,
            cached_post.text
        )
        # проверим, что у закешированной страницы нет context'а
        # response = self.client.get(reverse('posts:index'))
        # self.assertIsNone(response.context)
        # проверим, что пост остался после удаления
        cached_post.delete()
        response = self.client.get(reverse('posts:index'))
        self.assertContains(response, cached_post.text)
        # проверим, что пост пропал после очистки кеша
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        self.assertGreater(len(response.context['page_obj']), 0)
        self.assertNotEqual(
            response.context['page_obj'][0].text,
            cached_post.text
        )

    def test_profile_follow_correct(self):
        # неавторизованный пользователь не может подписаться
        profile_follow_url = reverse(
            'posts:profile_follow',
            kwargs={'username': PostsViewsTests.follow_user.username}
        )
        response = self.client.post(profile_follow_url, follow=True)
        self.assertRedirects(
            response, f'{reverse("users:login")}?next={profile_follow_url}'
        )
        # авторизованный пользователь может подписаться
        response = self.authorized_client.post(profile_follow_url)
        self.assertTrue(Follow.objects.filter(
            user=PostsViewsTests.user,
            author=PostsViewsTests.follow_user
        ).exists())
        # авторизованный пользователь не может подписаться второй раз
        response = self.authorized_client.post(profile_follow_url)
        self.assertEqual(Follow.objects.filter(
            user=PostsViewsTests.user,
            author=PostsViewsTests.follow_user
        ).count(), 1)
        # авторизованный пользователь не может подписаться на себя
        profile_follow_url = reverse(
            'posts:profile_follow',
            kwargs={'username': PostsViewsTests.user.username}
        )
        response = self.authorized_client.post(profile_follow_url)
        self.assertEqual(Follow.objects.filter(
            user=PostsViewsTests.user,
            author=PostsViewsTests.user
        ).count(), 0)

    def test_profile_unfollow_correct(self):
        # неавторизованный пользователь не может отписаться
        profile_unfollow_url = reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostsViewsTests.user.username}
        )
        response = self.client.post(profile_unfollow_url, follow=True)
        self.assertRedirects(
            response, f'{reverse("users:login")}?next={profile_unfollow_url}'
        )
        # авторизованный пользователь может отписаться если подписан
        response = self.authorized_client2.post(profile_unfollow_url)
        self.assertEqual(Follow.objects.filter(
            user=PostsViewsTests.user2,
            author=PostsViewsTests.user
        ).count(), 0)
        # авторизованный пользователь не может отписаться если не подписан
        follows_amount = Follow.objects.count()
        response = self.authorized_client2.post(
            profile_unfollow_url,
            follow=True
        )
        self.assertEqual(Follow.objects.count(), follows_amount)


class PaginatorViewsTest(TestCase):
    GROUP_LIST_POST_AMOUNT = 12
    PROFILE_POST_AMOUNT = 18

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create([
            # Посты с группой slug
            *(Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            ) for i in range(cls.GROUP_LIST_POST_AMOUNT)),
            # Посты с автором user2, без группы
            *(Post(
                author=cls.user2,
                text=f'Тестовый пост {i}',
            ) for i in range(cls.PROFILE_POST_AMOUNT)),
        ])
        cls.pages = [(
            reverse('posts:index'),
            (cls.GROUP_LIST_POST_AMOUNT + cls.PROFILE_POST_AMOUNT - 1)
            // settings.ITEMS_PER_PAGE + 1,
            (cls.GROUP_LIST_POST_AMOUNT + cls.PROFILE_POST_AMOUNT)
            - settings.ITEMS_PER_PAGE
            * ((cls.GROUP_LIST_POST_AMOUNT + cls.PROFILE_POST_AMOUNT - 1)
               // settings.ITEMS_PER_PAGE)
        ), (
            reverse('posts:group_list', kwargs={'slug': 'slug'}),
            (cls.GROUP_LIST_POST_AMOUNT - 1) // settings.ITEMS_PER_PAGE + 1,
            cls.GROUP_LIST_POST_AMOUNT - settings.ITEMS_PER_PAGE
            * ((cls.GROUP_LIST_POST_AMOUNT - 1) // settings.ITEMS_PER_PAGE)
        ), (
            reverse(
                'posts:profile', kwargs={
                    'username': cls.user2.username
                }
            ),
            (cls.PROFILE_POST_AMOUNT - 1) // settings.ITEMS_PER_PAGE + 1,
            cls.PROFILE_POST_AMOUNT - settings.ITEMS_PER_PAGE
            * ((cls.PROFILE_POST_AMOUNT - 1) // settings.ITEMS_PER_PAGE)
        )]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_paginator_first_page(self):
        """
        Паджинатор выдает нужное количество записей на первой странице.
        """
        for page, _, _ in PaginatorViewsTest.pages:
            response = self.authorized_client.get(page)
            with self.subTest(page=page):
                self.assertIn('page_obj', response.context)
                page_obj = response.context['page_obj']
                self.assertEqual(len(page_obj), settings.ITEMS_PER_PAGE)

    def test_paginator_last_page(self):
        """
        Паджинатор выдает соответствующее количество записей
        на последней странице.
        """
        for page, page_number, posts_count in PaginatorViewsTest.pages:
            response = self.authorized_client.get(
                page + f'?page={page_number}'
            )
            with self.subTest(page=page):
                self.assertIn('page_obj', response.context)
                page_obj = response.context['page_obj']
                self.assertEqual(len(page_obj), posts_count)
