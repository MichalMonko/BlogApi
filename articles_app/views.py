from rest_framework import generics, permissions

from articles_app.models import Article, Author
from articles_app.serializers import ArticlesSerializer, AuthorSerializer


class AuthorList(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuthorDetails(generics.RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


# Create your views here.
class ArticlesController(generics.ListCreateAPIView):
    """
    Handle incoming articles related requests. Allows for getting all articles with get() method
    or posting new one with post() method
    """
    queryset = Article.objects.all()
    serializer_class = ArticlesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ArticleDetailsController(generics.RetrieveUpdateDestroyAPIView):
    """
    Get selected article information based on primary ket provided in url, update existing article,
    or delete existing article
    """
    queryset = Article.objects.all()
    serializer_class = ArticlesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
