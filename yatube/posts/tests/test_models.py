from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Ч' * 100,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.post,
        )
        cls.model_spec = [(
            Group, [
                (
                    'title',
                    [
                        ('verbose_name', 'Имя',),
                        ('help_text', 'Введите имя сообщества',)
                    ]
                ),
                (
                    'slug',
                    [
                        ('verbose_name', 'Адрес',),
                        ('help_text', 'Введите адрес (код) сообщества',)
                    ]
                ),
                (
                    'description',
                    [
                        ('verbose_name', 'Описание',),
                        ('help_text', 'Введите описание сообщества',)
                    ]
                )
            ],
        ), (
            Post, [
                (
                    'text',
                    [
                        ('verbose_name', 'Текст поста',),
                        ('help_text', 'Введите текст нового поста',)
                    ]
                ),
                (
                    'created',
                    [
                        ('verbose_name', 'Дата создания',),
                        (
                            'help_text',
                            (
                                'Автоматически устанавливается '
                                'текущая дата и время'
                            ),
                        )
                    ]
                ),
                (
                    'author',
                    [
                        ('verbose_name', 'Автор',),
                        ('help_text', 'Выберите из списка автора публикации',)
                    ]
                ),
                (
                    'group',
                    [
                        ('verbose_name', 'Группа',),
                        (
                            'help_text',
                            'Выберите группу, к которой будет относиться пост',
                        )
                    ]
                ),
                (
                    'image',
                    [
                        ('verbose_name', 'Картинка',),
                        ('help_text', 'Выберите картинку',)
                    ]
                )
            ],
        ), (
            Comment, [
                (
                    'post',
                    [
                        ('verbose_name', 'Пост',),
                        (
                            'help_text',
                            'Выберите пост, к которому относится комментарий',
                        )
                    ]
                ),
                (
                    'created',
                    [
                        ('verbose_name', 'Дата создания',),
                        (
                            'help_text',
                            (
                                'Автоматически устанавливается '
                                'текущая дата и время'
                            ),
                        )
                    ]
                ),
                (
                    'author',
                    [
                        ('verbose_name', 'Автор',),
                        ('help_text', 'Выберите из списка автора комментария',)
                    ]
                ),
                (
                    'text',
                    [
                        ('verbose_name', 'Текст комментария',),
                        ('help_text', 'Введите текст комментария',)
                    ]
                )
            ],
        )]

    def test_meta_attrs(self):
        """verbose_name и help_text в полях совпадают с ожидаемыми."""
        for model_type, fields in PostModelTest.model_spec:
            for field, specs in fields:
                for spec, value in specs:
                    with self.subTest(field=field, spec=spec):
                        self.assertEqual(
                            getattr(
                                model_type._meta.get_field(field), spec
                            ), value
                        )

    def test_text_convert_to_slug(self):
        """Проверяем, что содержимое поля группы title преобразуется в slug."""
        group = PostModelTest.group
        slug = group.slug
        self.assertEqual(slug, 'ch' * 50)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
