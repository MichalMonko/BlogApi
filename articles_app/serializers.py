from rest_framework import serializers
from articles_app.models import Article, Author, Tag, Comment


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'nickname']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class CommentGetSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Comment
        fields = ['author', 'content', 'publication_date']


class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']


class ArticlesPostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Article
        fields = ['title', 'tags', 'content']


class ArticlesGetSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    tags = TagSerializer(many=True)
    comments = CommentGetSerializer(source='comment_set', many=True)

    class Meta:
        model = Article
        fields = ['title', 'author', 'tags', 'content', 'comments', 'publication_date', 'rating']
