from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import pagination
import urllib2
import requests

from thebuzz.authorization import is_authorized_to_comment
from .models import *

from rest_framework import serializers

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False)
    github = serializers.CharField(allow_blank=True, required=False)
    class Meta:
        model = Profile
        fields = ("id", "url", "host", "displayName", "github")
        #fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    friends = AuthorSerializer(many=True, source='following')
    class Meta:
        model = Profile
        fields = ("id", "host", "displayName", "url", "friends", "github", "firstName", "lastName",
                  "email", "bio")

class CommentAuthorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False)
    class Meta:
        model = CommentAuthor
        fields = '__all__'
    def create(self, validated_data):
        comment_author, created = CommentAuthor.objects.get_or_create(id=validated_data.get('id'))
        # Update the comment author
        comment_author = self.update(comment_author, validated_data)
        return comment_author

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.UUIDField(read_only=False)
    author = CommentAuthorSerializer()
    published = serializers.DateTimeField(source='date_created')
    class Meta:
        model = Comment
        fields = ('author', 'comment', 'published', 'id')


class AddCommentSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    post = serializers.URLField(required=False)
    comment = CommentSerializer()


    def create(self, validated_data):
        comment_data = validated_data.get('comment')
        author_data = comment_data.pop('author')

        post = get_object_or_404(Post, id=self.context.get('post_id'))
        # author = get_object_or_404(Profile, **author_data)
        comment_author_serializer = CommentAuthorSerializer(data=author_data)
        comment_author_serializer.is_valid()
        comment_author_serializer.save()
        author = CommentAuthor.objects.get(id=author_data.get('id'))
        comment = Comment.objects.create(associated_post=post, author=author, **comment_data)
        return comment


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='associated_author')
    comments = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    visibleTo = serializers.SerializerMethodField()
    

    class Meta:
        model = Post
        fields = ("title", "source", "origin", "description", "contentType", "content",
                  "author", "categories", "count", "size", "next", "comments", "published", "id", "visibility",
                  "visibleTo", "unlisted")

    def get_comments(self, obj):
        comments = obj.comments.order_by("-date_created")[:5]
        serializer = CommentSerializer(comments, many=True)
        return serializer.data

    def get_count(self, obj):
        if obj.comments == None:
            return 0
        return obj.comments.count()

    def get_size(self, obj):
        return 5

    def get_next(self, obj):
        return obj.associated_author.host + 'posts/' + str(obj.id) + '/comments'

    def get_categories(self, obj):
        categories = obj.categories
        split = categories.replace(',',' ').split(' ')
        return [x for x in split if x]

    def get_visibleTo(self, obj):
        visibleTo = obj.visibleTo
        split = visibleTo.replace(',',' ').split(' ')
        return [x for x in split if x]



# Todo
class FriendURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ("url",)

class FriendSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False)
    class Meta:
        model = Friend
        fields = '__all__'
    def create(self, validated_data):
        friend, created = Friend.objects.get_or_create(id=validated_data.get('id'))
        # Update the friend
        friend = self.update(friend, validated_data)
        return friend


# Get request of post from remote hosts
class GetPostSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    postid = serializers.UUIDField()
    url = serializers.URLField()
    author = AuthorSerializer()
    friends = serializers.ListField(child=serializers.URLField())

    def create(self, validated_data):
        pass
    def get_read(self, data):
        requestor_data = data.get('author')
        host = requestor_data.get('host')
        id = requestor_data.get('id')
        post = get_object_or_404(Post, id=data.get('postid'))
        return is_authorized_to_comment(id, post, host)



class FriendRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    author = AuthorSerializer()
    friend = FriendSerializer()

    def handle(self):
        requestor_data = self.validated_data.get('author')
        friend_serializer = FriendSerializer(data=requestor_data)
        friend_serializer.is_valid()
        friend_serializer.save()
        requestor = Friend.objects.get(id=requestor_data.get('id'))

        friend_data = self.validated_data.get('friend')
        friend = get_object_or_404(Profile, id=friend_data.get('id'))
        if requestor not in friend.following.all():
            friend.friend_request.add(requestor)



