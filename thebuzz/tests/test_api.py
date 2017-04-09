import json
import dateutil.parser
from django.utils import timezone
from thebuzz.models import *
from django.test import TestCase, Client
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from ..authorization import is_following
from rest_framework.test import APIClient


class post_tests(TestCase):
    def setUp(self):
        password = make_password('test')
        user = User.objects.create(username='test', password=password)
        author = Profile.objects.get(user=user)
        author.host = "http://testserver.com/"
        author.url = author.host + str(author.id)
        author.save()
        self.client = APIClient()
        self.client.force_authenticate(user)

        post = Post.objects.create(
            title='test',
            source='test',
            origin='test',
            description='test',
            content='test',
            published=datetime.now(),
            associated_author=author,
            contentType='text/plain'
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
        self.assertIsInstance(dateutil.parser.parse(response['published']), datetime,
                              "Published is not in datetime format")
        self.assertEqual(response['visibility'], "PUBLIC", "Default visibility not set")
        self.assertEqual(response['author']['id'], str(Profile.objects.get(user__username='test').id),
                         "Associated author does not match")

    def test_get_author_posts(self):
        author_id = Profile.objects.get(user__username='test').id
        response = self.client.get('/api/author/' + str(author_id) + '/posts/')
        response = json.loads(response.content)
        self.assertIsInstance(dateutil.parser.parse(response['posts'][0]['published']), datetime, "Published is not in datetime format")
        self.assertEqual(response['posts'][0]['visibility'], "PUBLIC", "Default visibility not set")
        self.assertEqual(response['posts'][0]['author']['id'], str(Profile.objects.get(user__username='test').id), "Associated author does not match")

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

    def logout(self):
        self.client.logout()


class profile_tests(TestCase):
    def setUp(self):
        password = make_password('test')
        user = User.objects.create(username='test', password=password)
        self.author = Profile.objects.get(user=user)
        self.author.host = "http://testserver.com/"
        self.author.url = self.author.host + str(self.author.id)
        self.author.firstName = "testuser"
        self.author.save()
        self.client = APIClient()
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/author/' + str(self.author.id) + '/')
        self.responseCode = response.status_code
        self.response = json.loads(response.content)

    def test_profile_exist(self):
        self.assertEqual(self.responseCode, 200, 'Profile does not exist')

    def test_id(self):
        self.assertEqual(self.response['id'], str(self.author.id), 'Author ID does not match')

    def test_displayname(self):
        self.assertEqual(self.response['displayName'], 'test', 'DisplayName does not match')

    def test_firstname(self):
        self.assertEqual(self.response['firstName'], 'testuser', 'firstName does not match')

    def test_user_host(self):
        self.assertEqual(self.response['host'], 'http://testserver.com/', 'host does not match')

    def test_url(self):
        self.assertEqual(self.response['url'], 'http://testserver.com/' + str(self.author.id), 'Authors url does not match')

    def logout(self):
        self.client.logout()


class friend_tests(TestCase):
    def setUp(self):
        # does it remember other users between tests? Ans: no.
        password = make_password('test')
        user = User.objects.create(username='test_1', password=password)
        author = Profile.objects.get(user=user)
        author.host = "http://testserver.com/"
        author.url = author.host+str(author.id)
        author.save()

        # second person
        password = make_password('test')
        user2 = User.objects.create(username='test_2', password=password)
        author = Profile.objects.get(user=user)
        author.host = "http://testserver.com/"
        author.url = author.host+str(author.id)
        author.save()

        self.client1 = APIClient()
        self.client1.force_authenticate(user=user)
        #self.client.login(username='test_1', password='test')
        #self.client2 = APIClient()
        #self.client2.force_authenticate(user=user2)

    def test_friend_request(self):
        user_id = User.objects.get(username='test_1').id
        friend_id = User.objects.get(username='test_2').id
        author = Profile.objects.get(user=user_id)
        friend = Profile.objects.get(user=friend_id)
        Aid = str(author.id)
        Aurl = author.host + 'api/author/' + str(author.id)
        Bid = str(friend.id)
        Burl = author.host + 'api/author/' + str(author.id)

        data = {"query": "friendrequest",
            "author": {
                "id": Aid,
                "url": Aurl,
                "host": "http://testserver.com",
                "displayName": author.displayName,
            },
            "friend": {
                "id": Bid,
                "url": Burl,
                "host": "http://testserver.com",
                "displayName": friend.displayName,
            }
        }
        response = self.client.post('/api/friendrequest/', content_type='application/json', data=json.dumps(data))
        self.assertEquals(response.status_code, 200, 'Failed to make a friend request')

        # Check if user2 has received user1's friend request
        author_following = author.following.all()
        friend_following = friend.following.all()
        print author_following
        print friend_following

        #self.assertEqual(author_following[0].id, friend.id, 'user2 didnt receive the friend request')
        #self.assertEqual(friend_pending_req[0].id, author.id, 'user1 is not a pending friend request')
