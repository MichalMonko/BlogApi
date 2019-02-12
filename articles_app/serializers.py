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


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Comment
        fields = ['author', 'content', 'publication_date']


class ArticlesSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(source='comment_set', many=True)

    def validate_rating(self, value):
        if 0 <= value <= 5:
            return value
        raise serializers.ValidationError("Rating must be in range 0 to 5")

    class Meta:
        model = Article
        fields = ['title', 'author', 'tags', 'content', 'comments', 'publication_date', 'rating']
