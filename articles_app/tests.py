from django.test import Client
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework.utils import json

from articles_app.models import CustomUser, Author, Article, Comment


# Create your tests here.


class ArticleTestCase(APITestCase):
    def setUp(self):
        self.mock_credentials1 = {'username': 'mock_user1', 'password': 'mock_password1'}
        self.mock_credentials2 = {'username': 'mock_user2', 'password': 'mock_password2'}
        self.redactor_credentials = {'username': 'mock_redactor', 'password': 'mock_password3'}

        self.custom_user = CustomUser.objects.create_user(username='default_author_user', email='none@mock.org',
                                                          password='password')
        mock_user = CustomUser.objects.create_user(**self.mock_credentials1, email='user1@mock.com')
        self.mock_author1 = Author.objects.get(user=mock_user)
        self.mock_author1.first_name = 'mock_author_name1'
        self.mock_author1.last_name = 'mock_author_last_name1'
        self.mock_author1.nickname = 'mock_author_nickname1'
        self.mock_author1.save()

        mock_user = CustomUser.objects.create_user(**self.mock_credentials2, email='user2@mock.com')
        self.mock_author2 = Author.objects.get(user=mock_user)
        self.mock_author2.first_name = 'mock_author_name2'
        self.mock_author2.last_name = 'mock_author_last_name2'
        self.mock_author2.nickname = 'mock_author_nickname2'
        self.mock_author2.save()

        mock_user = CustomUser.objects.create_user(**self.redactor_credentials, email='redactor@mock.com',
                                                   is_redaction=True)
        self.mock_redactor = Author.objects.get(user=mock_user)
        self.mock_redactor.first_name = 'mock_redactor_name'
        self.mock_redactor.last_name = 'mock_redactor_last_name'
        self.mock_redactor.nickname = 'mock_redactor_nickname'
        self.mock_redactor.save()

        mock_article_data = {'title': 'Explicit Mock Article', 'content': 'Mock article content'}
        self.mock_article = Article.objects.create(**mock_article_data, author=self.mock_redactor,
                                                   publication_date=timezone.now())
        self.mock_article.save()

        self.client = Client()

    def test_default_author_data_associated_with_user_upon_creation(self):
        author = Author.objects.get(user=self.custom_user)
        self.assertIsNotNone(author)
        self.assertEqual(author.first_name, 'Anonymous')

    def test_author_can_be_changed_after_user_creation(self):
        author = self.mock_author1
        self.assertIsNotNone(author)
        self.assertEqual(author.first_name, 'mock_author_name1')

    def test_user_not_in_redaction_cannot_create_article(self):
        data = {'title': 'Mock Article',
                'content': 'To Mock or not to Mock that is the question',
                'tags': ['tag1', 'tag2']}
        json_data = json.dumps(data)
        self.assertTrue(self.client.login(**self.mock_credentials1))
        response = self.client.post('http://testserver/articles/', data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_can_get_list_of_articles(self):
        response = self.client.get('http://testserver/articles/')
        received_data = json.loads(response.content)
        article_list = received_data['results']
        article_titles = [article['title'] for article in article_list]
        self.assertIn(self.mock_article.title, article_titles)

    def test_unauthenticated_user_can_get_article_details(self):
        response = self.client.get('http://testserver/articles/{}'.format(self.mock_article.id))
        received_data = json.loads(response.content)
        self.assertEqual(received_data['id'], self.mock_article.id)
        self.assertEqual(received_data['title'], self.mock_article.title)
        self.assertEqual(received_data['content'], self.mock_article.content)

    def test_user_in_redaction_can_create_article(self):
        data = {'title': 'Mock Article',
                'content': 'To Mock or not to Mock that is the question',
                'tags': ['tag1', 'tag2']}
        json_data = json.dumps(data)
        self.assertTrue(self.client.login(**self.redactor_credentials))
        response = self.client.post('http://testserver/articles/', data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        received_data = json.loads(response.content)
        created_article = Article.objects.get(pk=received_data['id'])
        self.assertIsNotNone(created_article)
        self.assertEqual(created_article.title, data['title'])

    def test_article_owner_can_edit_article(self):
        data = {'title': 'Brand New Mock Article Title',
                'content': 'Brand new content',
                'tags': ['newTag1', 'newTag2']}
        json_data = json.dumps(data)
        self.assertTrue(self.client.login(**self.redactor_credentials))
        response = self.client.put('http://testserver/articles/{}'.format(self.mock_article.id), data=json_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        received_data = json.loads(response.content)
        article = Article.objects.get(pk=received_data['id'])
        self.assertEqual(article.title, data['title'])
        self.assertEqual(article.content, data['content'])

        edited_tags = article.tags.filter(name__in=data['tags'])
        self.assertEqual(len(edited_tags), 2)

    def test_404_when_invalid_article_id_provided(self):
        response = self.client.get('http://testserver/articles/10000')
        self.assertEqual(response.status_code, 404)

    def test_cannot_edit_article_if_not_owner(self):
        data = {'title': 'Brand New Mock Article Title',
                'content': 'Brand new content',
                'tags': ['newTag1', 'newTag2']}
        json_data = json.dumps(data)
        self.assertTrue(self.client.login(**self.mock_credentials1))
        response = self.client.put('http://testserver/articles/{}'.format(self.mock_article.id), data=json_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_create_comment(self):
        data = {'content': 'This is a comment'}
        article_id = self.mock_article.id
        self.assertTrue(self.client.login(**self.mock_credentials2))
        response = self.client.post('http://testserver/articles/{}/comment'.format(article_id), data=data,
                                    format='json')
        self.assertEqual(response.status_code, 201)

        received_data = json.loads(response.content)
        created_comment = Comment.objects.get(pk=received_data['id'])
        self.assertEqual(created_comment.content, data['content'])
        self.assertEqual(created_comment.article.id, article_id)
        self.assertEqual(created_comment.author.first_name, self.mock_author2.first_name)

    def test_unauthenticated_user_cannot_create_article(self):
        data = {'title': 'Mock Article',
                'content': 'To Mock or not to Mock that is the question',
                'tags': ['tag1', 'tag2']}
        response = self.client.post('http://testserver/articles/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_add_comment(self):
        data = {'content': 'This is a comment'}
        article_id = self.mock_article.id
        response = self.client.post('http://testserver/articles/{}/comment'.format(article_id), data=data,
                                    format='json')
        self.assertEqual(response.status_code, 403)
