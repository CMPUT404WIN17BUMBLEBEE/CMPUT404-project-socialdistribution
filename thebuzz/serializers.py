from .models import Post, Comment
from rest_framework import serializers


# Based on http://www.django-rest-framework.org/tutorial/quickstart/

class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        # fields = ("title",
        #           "source",
        #           "origin",
        #           "description",
        #           "contentType",
        #           "content",
        #           "author",
        #           "categories",
        #           "count",
        #           "size",
        #           "next",
        #           "comments",
        #           "published",
        #           "id",
        #           "visibility",
        #           "visibleTo",
        #           "unlisted")
        fields = ("posted_text", "date_created", "post_privacy")


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ("associated_post", "comment", "date_created")
