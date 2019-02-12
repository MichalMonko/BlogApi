from django.apps import AppConfig


class ArticlesAppConfig(AppConfig):
    name = 'articles_app'

    def ready(self):
        import articles_app.signals
