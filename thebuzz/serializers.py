from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import pagination
import urllib2

from .models import *

from rest_framework import serializers

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False)
    github = serializers.CharField(required=False)
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

class CommentAuthorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False)
    class Meta:
        model = CommentAuthor
        fields = '__all__'

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = CommentAuthorSerializer()
    published = serializers.DateTimeField(source='date_created')
    comment = serializers.CharField(source='content')
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

        self.comment = CommentSerializer(data=author_data)
        post = get_object_or_404(Post, id=self.context.get('post_id'))
        # author = get_object_or_404(Profile, **author_data)
        author, created = CommentAuthor.objects.get_or_create(**author_data)
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
        return obj.associated_author.host + 'posts/' + str(obj.id) + '/comments'

# Todo
class FriendURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile 
        fields = ("url",)

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'

# Get request of post from remote hosts
# Todo: test needed. Works on local
class GetPostSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    postid = serializers.UUIDField()
    url = serializers.URLField()
    author = AuthorSerializer()
    friends = serializers.ListField(child=serializers.URLField())

    def get_read(self):
        requestor_data = self.validated_data.get('author')
        host = requestor_data.get('host')
        id = requestor_data.get('id')
        requestor_url = requestor_data.get('url')
        request_friends_urllist = self.validated_data.get('friends')

        # Query the requestor's server to verify provided friends list
        result = urllib2.urlopen(host + 'api/author/' + str(id))
        friends_of_requestor = json.loads(result.read()).get('friends')
        true_friends_urllist = list()
        for friend in friends_of_requestor:
            true_friends_urllist.append(friend.get('url'))

        for friend in request_friends_urllist:
            if friend not in true_friends_urllist:
                return False # lying on the friend list

        # Info of the post
        post = get_object_or_404(Post, id=self.validated_data.get('postid'))
        author_friends_urllist = list()
        for friend in post.associated_author.friends.all():
            author_friends_urllist.append(friend.url)

        # Authentication
        visibility = post.visibility
        # Public
        if visibility == "PUBLIC":
            return True
        # Server Only
        if visibility == "SERVERONLY" :
            return False
        # Friends - Check both friendlist
        if visibility == "FRIENDS" or visibility == "FOAF":
            if post.visibility and post.associated_author.url in request_friends_urllist and requestor_url in author_friends_urllist:
                return True
        # Private
        if post.visibility == "PRIVATE" and requestor_url in post.visibileTo:
            return True
        # FOAF
        if post.visibility == "FOAF":
            for friend in request_friends_urllist:
                # Verify the middle friend is a friend of post's author
                if friend not in author_friends_urllist:
                    continue
                # Verify that one of friends in friendlist has both requestor and post's author as friends
                l = friend.split('author/')
                host = l[0]
                id = l[1]
                result = urllib2.urlopen(host + 'api/author/' + id)
                middle_friends = json.loads(result.read()).get('friends')
                middle_friends_urllist = list()
                for middle_friend in middle_friends:
                    middle_friends_urllist.append(middle_friend.get('url'))
                if requestor_url in middle_friends_urllist and post.associated_author.url in middle_friends_urllist:
                    return True

        return False # Not a foaf



class FriendRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    author = AuthorSerializer()
    friend = FriendSerializer()

    def handle(self):
        author_data = self.validated_data.get('author')
        friend_data = self.validated_data.get('friend')
        author, remote_requestor = Friend.objects.get_or_create(**author_data)
        friend = get_object_or_404(Profile, **friend_data)

        friend.follow(author)

            # If the friend is on the remote server, send another friend request to the remote server
        # Todo: test needed. Local friend request works
        # if remote_friend:
        #     remote_host = friend.host
        #     request = urllib2.Request(remote_host+'friendrequest', headers={"Content-Type": "application/json"})
        #     response = urllib2.urlopen(request, self.validated_data)
        # if friend in author.followers.all():
        #     author.friends.add(friend)
        #     author.followers.remove(friend)
        #     friend.following.remove(author)
        # else:
        #     author.following.add(friend)
        #     friend.followers.add(author)


