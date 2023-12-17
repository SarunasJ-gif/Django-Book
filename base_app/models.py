
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    avatar = models.ImageField(null=True, default="avatar.jpg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    picture = models.ImageField(null=True, default="book.png")

    class Meta:
        ordering = ['-added']
    
    def __str__(self):
        return self.name
    


