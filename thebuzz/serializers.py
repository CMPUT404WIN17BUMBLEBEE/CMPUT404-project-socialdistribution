from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import pagination

from .models import *

from rest_framework import serializers

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile 
        fields = ("id", "url", "host", "displayName", "github")
        #fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    friends = AuthorSerializer(many=True)
    class Meta:
        model = Profile 
        fields = ("id", "host", "displayName", "url", "friends", "github", "firstName", "lastName",
                  "email", "bio")


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = AuthorSerializer()
    class Meta:
        model = Comment
        fields = ('author', 'content', 'date_created', 'id')


class AddCommentSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    post = serializers.URLField(required=False)
    comment = CommentSerializer()

    def create(self, validated_data):
        comment_data = validated_data.get('comment')
        author_data = comment_data.pop('author')
        self.comment = CommentSerializer(data=author_data)
        post = get_object_or_404(Post, id=self.context.get('post_id'))
        author = get_object_or_404(Profile, **author_data)
        comment = Comment.objects.create(associated_post=post, author=author, **comment_data)
        return comment


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='associated_author')
    comments = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()


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
        return obj.associated_author.host + '/posts/' + str(obj.id) + '/comments'


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile 
        fields = ("url",)


class GetPostSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    postid = serializers.UUIDField()
    url = serializers.URLField()
    author = AuthorSerializer()
    friends = serializers.ListField(child=serializers.URLField())

    def get_read(self):
        post = get_object_or_404(Post, id=self.data.get('postid'))
        friends_list = self.data.get('friends')

        for friend in post.author.friends.all():
            if friend.url in friends_list:
                return True
        return False


class FriendRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    author = AuthorSerializer()
    friend = AuthorSerializer()

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        friend_data = validated_data.pop('friend')
        author = get_object_or_404(Profile, **author_data)
        friend = get_object_or_404(Profile, **friend_data)
        author.following.add(friend)
        friend.followers.add(author)
        if friend in author.followers:
            author.friends.add(friend)


