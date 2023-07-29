from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = "admin"
    USER = "user"
    USER_ROLES = (
        (USER, "user"),
        (ADMIN, "admin"),
    )
    role = models.CharField(
        'Роль',
        max_length=max(len(role[0]) for role in USER_ROLES),
        choices=USER_ROLES,
        default=USER
    )
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )
    email = models.EmailField(
        'Почта',
        max_length=254,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name="pair username/email should be unique"),
        ]

    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    def __str__(self):
        return self.username

    # def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='subscribing'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name="unique_subscriptions"),
        ]

    def __str__(self):
        return f'{self.user}, {self.author}'
