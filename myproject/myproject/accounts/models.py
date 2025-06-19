from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Добавлено поле баланса

    def __str__(self):
        return f"Профиль пользователя {self.user.username} (Баланс: {self.balance} ₽)"


# Автоматическое создание профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)


class Game(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    genre = models.CharField(max_length=50)
    developer = models.CharField(max_length=100)
    release_date = models.DateTimeField()
    icon = models.CharField(max_length=10)

    def __str__(self):
        return self.title


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"

    class Meta:
        ordering = ['-date']


class CommunityPost(models.Model):
    CATEGORY_CHOICES = [
        ('solution', 'Решение проблемы'),
        ('discussion', 'Обсуждение'),
        ('news', 'Новости'),
        ('tutorial', 'Обучение'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class PaymentMethod(models.Model):
    TYPE_CHOICES = [
        ('card', 'Банковская карта'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('qiwi', 'QIWI'),
        ('yoomoney', 'ЮMoney'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    details = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} ({self.details})"

    class Meta:
        ordering = ['-is_default', '-created_at']


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    ]

    TYPE_CHOICES = [
        ('deposit', 'Пополнение'),
        ('purchase', 'Покупка игры'),
        ('refund', 'Возврат средств'),
        ('withdrawal', 'Вывод средств'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)  # Ссылка на игру для покупок
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.amount} ₽ ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']