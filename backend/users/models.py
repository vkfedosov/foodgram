from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Exists, OuterRef


class SubscriptionQuerySet(models.QuerySet):
    """Subscription QuerySet."""

    def add_user_annotations(self, user_id):
        return self.annotate(
            is_subscribed=Exists(
                Subscription.objects.filter(
                    author__pk=OuterRef('pk'),
                    user_id=user_id,
                )
            ),
        )


CustomUserManger = UserManager.from_queryset(SubscriptionQuerySet)


class User(AbstractUser):
    """Custom User model."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    GUEST = 'guest'
    AUTHORIZED = 'authorized'
    ADMIN = 'admin'

    USER_ROLES = [
        (GUEST, 'guest'),
        (AUTHORIZED, 'authorized'),
        (ADMIN, 'admin'),
    ]

    objects = CustomUserManger()

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email',
    )
    username = models.CharField(
        blank=False,
        max_length=150,
        unique=True,
        verbose_name='Username',
    )
    first_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='First Name',
    )
    last_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Last Name',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Password',
    )
    role = models.CharField(
        default='guest',
        choices=USER_ROLES,
        max_length=10,
        verbose_name='User Role',
    )

    @property
    def is_guest(self):
        """Checking for unauthorized user rights (guest)."""
        return self.role == self.GUEST

    @property
    def is_authorized(self):
        """Checking for authorized user rights."""
        return self.role == self.AUTHORIZED

    @property
    def is_admin(self):
        """Checking for administrator rights."""
        return self.role == self.ADMIN or self.is_superuser

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Subscription to author of recipe model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Subscriber',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Recipe Author',
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.user} subscribed on {self.author}'
