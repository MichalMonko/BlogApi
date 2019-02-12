from django.dispatch import receiver
from django.db.models.signals import post_save

from articles_app.models import CustomUser, Author


@receiver(post_save, sender=CustomUser)
def create_author_data_on_user_creation(sender, instance, created, **kwargs):
    if created:
        author = Author(user=instance)
        author.save()
