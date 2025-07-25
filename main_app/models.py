from django.db import models
from django.contrib.auth.models import User

class UserLogin(models.Model):
    username = models.EmailField(unique=True)
    password = models.CharField(max_length=256)

class SearchRequest(models.Model):
    city = models.CharField(max_length=100)
    pages_count = models.PositiveIntegerField()
    keywords = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city} - {self.pages_count} pages"


class SearchResult(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=500)
    passage = models.TextField()

    region_id = models.CharField(max_length=10)
    keyword = models.CharField(max_length=200)
    page = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.title} ({self.url})'


class Rabota(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    results = models.URLField(max_length=500, blank=True, null=True)
    city = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column='Sity',  # колонка в БД именно с заглавной S
        verbose_name='Город'  # можно добавить удобное название для админки
    )

    class Meta:
        db_table = 'rabota'

    def __str__(self):
        return f"{self.user.username} - {self.city}"
