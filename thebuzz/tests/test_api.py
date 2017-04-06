import json
import dateutil.parser
from django.utils import timezone

from thebuzz.models import *
from django.test import TestCase, Client
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class post_tests(TestCase):
    def setUp(self):
        password = make_password('test')
        user = User.objects.create(username='test', password=password)
        author = Profile.objects.get(user=user)
        author.host = "http://testserver.com/"
        author.url = author.host + str(author.id)
        author.save()
        self.client.login(username='test', password='test')

        post = Post.objects.create(
            title='test',
            source='test',
            origin='test',
            description='test',
            content='test',
            published=datetime.now(),
            associated_author=author
        )

    def test_get_public_posts(self):
        response = self.client.get('/api/posts/')
        self.assertEquals(response.status_code, 200, 'Failed to get the public posts')
        response = json.loads(response.content)
        self.assertEqual(response['size'], 50, 'Pagination size is wrong')
        self.assertEqual(response['count'], 1, 'Count is wrong')

    def test_get_post_detail(self):
        post_id = Post.objects.get(title='test').id
        response = self.client.get('/api/posts/'+str(post_id)+'/')
        self.assertEquals(response.status_code, 200, 'Failed to get the post detail')

        response = json.loads(response.content)
        self.assertEqual(response['title'], 'test', 'Title does not match')
        self.assertEqual(response['source'], 'test', "Source does not match")
        self.assertEqual(response['origin'], 'test', "Origin does not match")
        self.assertEqual(response['description'], 'test', "Description does not match")
        self.assertEqual(response['content'], 'test', "Content does not match")
        self.assertEqual(response['contentType'], "text/plain", "Default contentType not set")
<<<<<<< HEAD
        self.assertIsInstance(dateutil.parser.parse(response['published']), datetime,
                              "Published is not in datetime format")
        self.assertEqual(response['visibility'], "PUBLIC", "Default visibility not set")
        self.assertEqual(response['author']['id'], str(Profile.objects.get(user__username='test').id),
                         "Associated author does not match")

    def test_get_author_posts(self):
        author_id = Profile.objects.get(user__username='test').id
        response = self.client.get('/api/author/' + str(author_id) + '/posts/')
=======
        self.assertIsInstance(dateutil.parser.parse(response['published']), datetime, "Published is not in datetime format")
        self.assertEqual(response['visibility'], "PUBLIC", "Default visibility not set")
        self.assertEqual(response['author']['id'], str(Profile.objects.get(user__username='test').id), "Associated author does not match")

    def test_get_author_posts(self):
        author_id = Profile.objects.get(user__username='test').id
        response = self.client.get('/api/author/'+str(author_id)+'/posts/')
        self.assertEquals(response.status_code, 200, 'Failed to get the author posts')

        response = json.loads(response.content)
        self.assertEqual(response['size'], 50, 'Pagination size is wrong')
        self.assertEqual(response['count'], 1, 'Count is wrong')

    def test_get_posts_author_can_see(self):
        response = self.client.get('/api/author/posts/')
        self.assertEquals(response.status_code, 200, 'Failed to get all the posts author can see')

        response = json.loads(response.content)
        self.assertEqual(response['size'], 50, 'Pagination size is wrong')
        self.assertEqual(response['count'], 1, 'Count is wrong')

    def test_comment(self):
        post_id = Post.objects.get(title='test').id
        author = Profile.objects.get(user__username='test')
        comment_id = uuid.uuid4()
        data = {
            "query": "addComment",
            "post": "http://test.com/p",
            "comment": {
                "author": {
                    "id": str(author.id),
                    "url": author.url,
                    "host": author.host,
                    "displayName": author.displayName,
                    "github": author.github
                },
                "comment": 'test',
                "published": str(timezone.now()),
                "id": str(comment_id)
            }
        }
        response = self.client.post('/api/posts/'+str(post_id)+'/comments/', content_type='application/json', data=json.dumps(data))
        self.assertEquals(response.status_code, 200, 'Failed to add the comments')

        response = self.client.get('/api/posts/'+str(post_id)+'/comments/')
        self.assertEquals(response.status_code, 200, 'Failed to get the comments')

        response = json.loads(response.content)
        self.assertEqual(response['size'], 50, 'Pagination size is wrong')
        self.assertEqual(response['count'], 1, 'Count is wrong')
        comment = response['comments'][0]
        self.assertEqual(comment['comment'], 'test', 'Comment does not match')
        self.assertIsInstance(dateutil.parser.parse(comment['published']), datetime, "Published is not in datetime format")
        self.assertEqual(comment['author']['id'], str(Profile.objects.get(user__username='test').id), "Associated author does not match")
