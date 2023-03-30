from django.db import models
from core.models import CreatedModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title: str = models.CharField(max_length=200)
    slug: str = models.SlugField(unique=True)
    description: str = models.TextField()

    def __str__(models) -> str:
        return models.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text: str = models.TextField(
        'Введи текст',
        help_text='Поделись своим рецептом!')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор')
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name='posts',
        verbose_name='Выбери группу',
        help_text='К какой категории отнесем рецепт?')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор')
    text: str = models.TextField(
        'Текст комментария',
        help_text='Поделись своим мнением!')

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique key')]
