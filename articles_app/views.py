from django.http import Http404
from django.utils.datetime_safe import datetime
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from articles_app.pagination import ArticlesPagination
from articles_app.permissions import IsAuthorOrReadOnly

from articles_app.models import Article, Author, get_author_data_related_to_user, Comment

# Create your views here.
from articles_app.serializers import ArticlesPostSerializer, ArticlesGetSerializer, CommentPostSerializer


class ArticlesController(generics.ListCreateAPIView):
    """
    Handle incoming articles related requests. Allows for getting all articles with get() method
    or posting new one with post() method
    """
    queryset = Article.objects.all()
    serializer_class = ArticlesGetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = ArticlesPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticlesPostSerializer
        elif self.request.method == 'GET':
            return ArticlesGetSerializer

    def get_queryset(self):
        tags = self.request.query_params.get('tags', None)
        if tags is not None:
            tags = str(tags).split(',')
            queryset = Article.objects.filter(tags__name__in=tags)
        else:
            queryset = Article.objects.order_by('-publication_date')

        return queryset

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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ArticlesGetSerializer
        else:
            return ArticlesPostSerializer


class CommentController(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            article = get_object_or_404(Article, pk=pk)
            comment_author = get_author_data_related_to_user(request.user)
            current_date = datetime.now()
            comment = Comment(article=article, author=comment_author, publication_date=current_date)
        except Author.DoesNotExist:
            raise Http404("User doesn't have author data associated")
        serializer = CommentPostSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
