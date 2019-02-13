from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from articles import settings


class CustomUser(AbstractUser):
    is_redaction = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=64, blank=True, default='Anonymous')
    last_name = models.CharField(max_length=64, blank=True, default='')
    nickname = models.CharField(max_length=64, blank=True, default='')

    def __str__(self):
        return "{} '{}' {}".format(self.first_name, self.nickname, self.last_name)


def get_author_data_related_to_user(user: CustomUser):
    return Author.objects.get(user_id=user.id)


class TagManager(models.Manager):
    def create_tag(self, name):
        tag = self.get_or_create(name=name)
        return tag


class Tag(models.Model):
    name = models.CharField(max_length=32)
    objects = TagManager()


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING)
    tags = models.ManyToManyField(Tag, blank=True, default='')
    publication_date = models.DateField()
    rating = models.IntegerField(default=0)


class Comment(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    publication_date = models.DateTimeField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
