from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Group(CreatedModel):
    title = models.CharField(max_length=200, verbose_name="Имя группы")
    slug = models.SlugField(unique=True, verbose_name="slug группы")
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(null=True, verbose_name="Текст поста")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор поста",
    )

    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(CreatedModel):
    text = models.TextField('Текст', help_text='Текст нового комментария')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор комментария",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Коментарии к посту",
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(CreatedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="автор",
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Подписки'
