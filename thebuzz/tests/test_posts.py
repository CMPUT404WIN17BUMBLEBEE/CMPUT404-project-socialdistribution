from thebuzz.models import Comment, Post

from django.test import TestCase
import datetime

class post_tests(TestCase):

    def test_create_comment(self):
        post = Post.objects.create(
            posted_text = "test post text"
        )

        print "POST: " + str(post.id)
        comment = Comment.objects.create()
        comment.associated_post = post.id
        comment.content = 'test comment text'

        self.assertEqual(comment.content, "test comment text", "comment content not equal")
        self.assertEqual(comment.date_created, models.DateTimeField(auto_add_now=True), "created dates are not equal")
        self.assertEqual(comment.associated_post, post.id, "associated with the correct post")
