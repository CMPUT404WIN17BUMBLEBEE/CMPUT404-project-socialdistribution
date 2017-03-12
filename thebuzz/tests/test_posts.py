from thebuzz.models import Comment, Post, Profile
from django.test import TestCase
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class post_tests(TestCase):
    user_id = 0

    def setUp(self):
        global user_id
        password = make_password("password123")
        user = User.objects.create(username="TestUser", password=password)
        user_id = user.id

    def test_create_post(self):
        global user_id
        user = User.objects.get(id=user_id)

        title = "Test Title"
        source = "http://lastplaceigotthisfrom.com/post/yyyy"
        origin = "http://whereitcamefrom.com/post/zzzzz"
        description = "Test Description"
        content = "Test content"
        published = datetime.now()

        post = Post.objects.create(
            title = title,
            source = source,
            origin = origin,
            description = description,
            content = content,
            published = published,
            associated_author = user
        )

        self.assertTrue(post, "post is empty")
        self.assertEqual(post.title, title, "title does not match")
        self.assertEqual(post.source, source, "source does not match")
        self.assertEqual(post.origin, origin, "origin does not match")
        self.assertEqual(post.description, description, "description does not match")
        self.assertEqual(post.content, content, "conent does not match")
        self.assertFalse(post.image, "image not blank")
        self.assertEqual(post.contentType, "text/plain", "default contentType not set")
        self.assertIsInstance(post.published, datetime, "published is not a datetime instance")
        self.assertEqual(post.visibility, "PUBLIC", "default visibility not set")
        self.assertEqual(post.associated_author, user, "associated_author does not match")


    def test_create_comment(self):
        global user_id

        post = Post.objects.create(
            content = "test post text",
            published = datetime.now(),
            associated_author = User.objects.get(id=user_id)
        )

        author = Profile.objects.get(user_id=user_id)

        comment = Comment.objects.create(
            associated_post = post,
            content = 'test comment text',
            author = author
        )

        self.assertEqual(comment.content, "test comment text", "comment content not equal")
        self.assertIsInstance(comment.date_created, datetime, "created date is not a datetime instance")
        self.assertEqual(comment.associated_post, post, "associated with the correct post")
        self.assertIsInstance(comment, Comment, "Not a comment object")
