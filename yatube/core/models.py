from django.db import models


class CreatedModel(models.Model):
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        help_text='Автоматически устанавливается текущая дата и время'
    )

    class Meta:
        abstract = True
