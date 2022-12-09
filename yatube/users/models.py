from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Выберите аватар',
    )

    def get_name(self):
        return self.get_full_name() or self.get_username()

    class Meta:
        db_table = 'auth_user'
