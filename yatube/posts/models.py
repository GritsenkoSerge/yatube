from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    # Имя (title) — название группы.
    title = models.TextField()
    # Адрес (slug) — уникальный адрес группы, часть URL
    # (например, для группы любителей котиков
    # slug будет равен cats: group/cats).
    slug = models.TextField()
    # Описание (description) — текст, описывающий сообщество.
    # Этот текст будет отображаться на странице сообщества.
    description = models.TextField()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
