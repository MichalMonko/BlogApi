from django.utils import timezone
from django.utils.datetime_safe import datetime
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from articles_app.models import Article, Author, get_author_data_related_to_user

# Create your views here.
from articles_app.serializers import ArticlesPostSerializer, ArticlesGetSerializer


class ArticlesController(generics.ListCreateAPIView):
    """
    Handle incoming articles related requests. Allows for getting all articles with get() method
    or posting new one with post() method
    """
    queryset = Article.objects.all()
    serializer_class = ArticlesGetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticlesPostSerializer
        elif self.request.method == 'GET':
            return ArticlesGetSerializer

    def perform_create(self, serializer):
        related_author = get_author_data_related_to_user(self.request.user)
        current_date = datetime.now()
        serializer.save(author=related_author, publication_date=current_date)


class ArticleDetailsController(generics.RetrieveUpdateDestroyAPIView):
    """
    Get selected article information based on primary ket provided in url, update existing article,
    or delete existing article
    """
    queryset = Article.objects.all()
    serializer_class = ArticlesGetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ArticlesGetSerializer
        else:
            return ArticlesPostSerializer
