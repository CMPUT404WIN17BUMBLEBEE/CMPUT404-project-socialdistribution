from django.test import TestCase
import unittest
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from thebuzz.models import Profile, Friend
from django.core import serializers
from thebuzz.serializers import *

class FriendsTestCase(TestCase):

    def setUp(self):
        global author1, author2, author3, author4, author5
        #Setting up some users to use for friending and unfriending
        password = make_password("password123")
        user1 = User.objects.create(username="TestUser1", password=password)
        author1 = Profile.objects.get(user_id = user1.id)
        author1.displayName="TestUser1"
        author1.url="http://author1.com/"
        author1.host="http://author1.com/"
        author1.save()
        user2 = User.objects.create(username="TestUser2", password=password)
        author2 = Profile.objects.get(user_id = user2.id)
        author2.displayName="TestUser2"
        author2.url="http://author2.com/"
        author2.host="http://author2.com/"
        author2.save()
        user3 = User.objects.create(username="TestUser3", password=password)
        author3 = Profile.objects.get(user_id = user3.id)
        author3.displayName="TestUser3"
        author3.url="http://author3.com/"
        author3.host="http://author3.com/"
        author3.save()
        user4 = User.objects.create(username="TestUser4", password=password)
        author4 = Profile.objects.get(user_id = user4.id)
        author4.displayName="TestUser4"
        author4.url="http://author4.com/"
        author4.host="http://author4.com/"
        author4.save()
        user5 = User.objects.create(username="TestUser5", password=password)
        author5 = Profile.objects.get(user_id = user5.id)
        author5.displayName="TestUser5"
        author5.url="http://author5.com/"
        author5.host="http://author5.com/"
        author5.save()

    def test_following(self):
        self.assertFalse(author1.following.all().exists(), "author1 should not be following anyone")

        friend = Friend.objects.create(
            id=author2.id,
            displayName=author2.displayName,
            host=author2.host,
            url=author2.url
        )

        author1.following.add(friend)

        self.assertTrue(author1.following.all().exists(), "author1 should be following someone")
        self.assertEqual(len(author1.following.all()), 1, "author1 should only be following 1 person")
        self.assertEqual(author1.following.all()[0].displayName, author2.displayName, "author1 should be folloing author2")

        friend = Friend.objects.create(
            id=author3.id,
            displayName=author3.displayName,
            host=author3.host,
            url=author3.url
        )

        author1.following.add(friend)

        self.assertTrue(author1.following.all().exists(), "author1 should be following someone")
        self.assertEqual(len(author1.following.all()), 2, "author1 should only be following 2 people")

        following = author1.following.all()
        self.assertTrue(following.filter(displayName=author2.displayName), "author1 should be following author2")
        self.assertTrue(following.filter(displayName=author3.displayName), "author1 should be following author3")


    def test_friend_request(self):
        self.assertFalse(author1.friend_request.all().exists(), "author1 should not be following anyone")

        friend = Friend.objects.create(
            id=author2.id,
            displayName=author2.displayName,
            host=author2.host,
            url=author2.url
        )

        author1.friend_request.add(friend)

        self.assertTrue(author1.friend_request.all().exists(), "author1 should not have friend requests")
        self.assertEqual(len(author1.friend_request.all()), 1, "author1 should have 1 friend requests")
        self.assertEqual(author1.friend_request.all()[0].displayName, author2.displayName, "author1 should have author2 as friend request")

        friend = Friend.objects.create(
            id=author3.id,
            displayName=author3.displayName,
            host=author3.host,
            url=author3.url
        )

        author1.friend_request.add(friend)

        self.assertTrue(author1.friend_request.all().exists(), "author1 should have friend requests")
        self.assertEqual(len(author1.friend_request.all()), 2, "author1 should have 2 friend requests")

        friend_request = author1.friend_request.all()

        self.assertTrue(friend_request.filter(displayName=author3.displayName), "author1 should have author2 as friend request")
        self.assertTrue(friend_request.filter(displayName=author3.displayName), "aauthor1 should have author3 as friend request")
