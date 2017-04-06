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
        author.url = author.host+str(author.id)
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


class profile_tests(TestCase):
    def setUp(self):
        password = make_password('test')
        user = User.objects.create(username='test', password=password)
        self.author = Profile.objects.get(user=user)
        self.author.host = "http://testserver.com/"
        self.author.url = self.author.host + str(self.author.id)
        self.author.firstName = "testuser"
        self.author.save()
        response = self.client.get('/api/author/' + str(self.author.id) + '/')
        self.responseCode = response.status_code
        self.response = json.loads(response.content)

    def test_profile_exist(self):
        self.assertEqual(self.responseCode, 200, 'Profile does not exist')

    def test_id(self):
        self.assertEqual(self.response['id'], str(self.author.id))

    def test_displayname(self):
        self.assertEqual(self.response['displayName'], 'test')

    def test_firstname(self):
        self.assertEqual(self.response['firstName'], 'testuser')

    def test_user_host(self):
        self.assertEqual(self.response['host'], 'http://testserver.com/')

    def test_url(self):
        self.assertEqual(self.response['url'], 'http://testserver.com/' + str(self.author.id))


class friend_tests(TestCase):
    def setUp(self): #does it remember other users between tests? Ans: no.
	    password = make_password('test')
            user = User.objects.create(username='test_1', password=password)
            author = Profile.objects.get(user=user)
            author.host = "http://testserver.com/"
            author.url = author.host+str(author.id)
            author.save()

	    #second person
	    password = make_password('test')
            user = User.objects.create(username='test_2', password=password)
            author = Profile.objects.get(user=user)
            author.host = "http://testserver.com/"
            author.url = author.host+str(author.id)
            author.save()
            self.client.login(username='test_1', password='test')

    def test_friend_request(self):
        user_id = User.objects.get(username='test_1').id
        friend_id = User.objects.get(username='test_2').id
        author = Profile.objects.get(user=user_id)
        friend = Profile.objects.get(user=friend_id)
        Aid = author.host + str(author.id)
        Aurl = author.host + 'author/' + str(author.id)
        Bid = friend.host + str(friend.id)
        Burl = author.host + 'author/' + str(author.id)

        data = {"query":"friendrequest",
		    "author": {
				"id": Aid,
				"host": author.host,
				"displayName": author.displayName,
                		"url": Aurl,
			  },
		    "friend": {
			    "id": Bid,
			    "host": friend.host,
			    "displayName": friend.displayName,
	               	    "url": Burl,
			}
       	}
        response = self.client.post('/api/friendrequest', content_type='application/json', data=json.dumps(data))
        self.assertEquals(response.status_code, 200, 'Failed to make a friend request')

        # Check if user2 has received user1's friend request
        friend_follower = friend.get_all_followers()
        author_following = author.get_all_following()

    def test_FOAF(self):
        # Basically check if user1 is user2's friend
        user2_id = User.objects.get(username='test_2').id
        url = '/api/author/' + str(user2_id) + '/friends'
        response = self.client.get(url, content_type='application/json')
