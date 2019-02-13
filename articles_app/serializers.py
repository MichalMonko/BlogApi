from rest_framework import serializers
from articles_app.models import Article, Author, Tag, Comment


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'nickname']


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Tag
        fields = ['name']


class StringToTagSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    def to_internal_value(self, data):
        return {'name': data}

    class Meta:
        model = Tag
        fields = ['name']


class CommentGetSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Comment
        fields = ['author', 'content', 'publication_date']


class CommentPostSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(required=False)

    class Meta:
        model = Comment
        fields = ['id', 'content']


class ArticlesPostSerializer(serializers.ModelSerializer):
    tags = StringToTagSerializer(many=True, required=False)
    id = serializers.ReadOnlyField(required=False)

    def create(self, validated_data):
        tags_list = list()
        try:
            tags_list = validated_data.pop('tags')
        except Tag.DoesNotExist:
            pass

        article = Article.objects.create(**validated_data)
        for tag in tags_list:
            article.tags.create(**tag)

        return article

    def update(self, instance, validated_data):
        tags_list = list()
        try:
            tags_list = validated_data.pop('tags')
        except KeyError:
            pass

        for tag in tags_list:
            instance.tags.create(**tag)

        instance.title = validated_data.pop('title')
        instance.content = validated_data.pop('content')
        instance.save()
        return instance

    class Meta:
        model = Article
        fields = ['id', 'title', 'tags', 'content']


class ArticlesGetSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    tags = TagSerializer(many=True)
    comments = CommentGetSerializer(source='comment_set', many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'author', 'tags', 'content', 'comments', 'publication_date', 'rating']
