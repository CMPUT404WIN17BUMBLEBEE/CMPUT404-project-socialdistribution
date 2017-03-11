from .models import Comment, Post, Profile

from django.test import TestCase
from datetime import datetime
from django.contrib.auth.models import User

class post_tests(TestCase):
    

    def test_create_comment(self):
        post = Post.objects.create(
            posted_text = "test post text",
            date_created = datetime.now()
        )

        user = User.objects.create(username='user1', password='password1')
        author = Profile.objects.create(user_id=123)
    
        print "POST: " + str(post.id)
        comment = Comment.objects.create(
            associated_post = post,
            content = 'test comment text',
            author = author
        )

        self.assertEqual(comment.content, "test comment text", "comment content not equal")
        self.assertIsInstance(comment.date_created, datetime, "created date is not a datetime instance")
        self.assertEqual(comment.associated_post, post, "associated with the correct post")
        self.assertIsInstance(comment, Comment, "Not a comment object")

