from django.db import models

from django.contrib.auth import get_user_model


User = get_user_model()

POSTS_ON_THE_PAGE = 10


class Post(models.Model):
    text = models.TextField(verbose_name='Название публикации')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        'Group', blank=True,
        on_delete=models.SET_NULL, null=True,
        related_name='group_posts',
        verbose_name='Группа',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Адрес')
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title


class Meta:
    ordering = ['-order_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации комментария'
    )

    def __str__(self) -> str:
        return self.title


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
