from itertools import chain

from django.core.serializers import json
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.generics import ListCreateAPIView, GenericAPIView, UpdateAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.views import APIView

from serializers import *
from pagination import *

from .models import *

import sys

class PostListView(ListCreateAPIView):
    queryset = Post.objects.filter(visibility="PUBLIC", unlisted=False).order_by('-published')
    serializer_class = PostSerializer
    pagination_class = PostsPagination


class PostDetailView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(self.queryset, id=kwargs['post_id'])
        author = get_object_or_404(Profile, id=request.user.profile.id)
        if is_authenticated_to_read(post, author):
            serializer = self.serializer_class(post)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = GetPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.get_read():
            post = get_object_or_404(self.queryset, id=kwargs['post_id'])
            serializer = self.serializer_class(post)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class PostsAuthorCanSeeView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostsPagination

    def get_queryset(self):
        author = get_object_or_404(Profile, id=self.request.user.profile.id)
        return get_readable_posts(author, self.queryset)


class AuthorPostsView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostsPagination

    def get_queryset(self):
        authorposts = self.queryset.filter(profile=self.kwargs['author_id'])
        author = get_object_or_404(Profile, id=self.request.user.profile.id)
        return get_readable_posts(author, authorposts)


class CommentView(ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentsPagination

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        author = get_object_or_404(Profile, id=self.request.user.profile.id)
        if is_authenticated_to_read(post, author):
            return self.queryset.filter(associated_post__id=self.kwargs['post_id']).order_by("-date_created")
        return self.queryset.none()

    def post(self, request, *args, **kwargs):
        print "METHOD: " + request.method
        print "HERE!" 
        print ("REQUEST DATA: " + str(request.data))
        print ("REQUEST POST: " + str(request.POST.get('query')))
        print ("REQUEST AUTHOR: " + str(request.data.get('comment').get('author').get('id')))

        split = request.data.get('comment').get('author').get('id').split("/")
        actual_id = split[0]

        if len(split) > 1:
            actual_id = split[4]

        print "ACTUAL ID: " + actual_id
        request.data.get('comment').get('author').get('id').__setitem__(actual_id)

        #print ("REQUEST TEXT: " + str(request.text))
        #print ("REQUEST BODY: " + str(request.body))
        print ("POST ID: " + str(kwargs['post_id']))
        print "REQUEST DATA AGAIN: " + request.data

        serializer = AddCommentSerializer(data=request.data, context={'post_id': kwargs['post_id']})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print "SERIALIZER ERRORS: " + str(serializer.errors)

        response = OrderedDict([
            ("query", "addComment"),
            ("success", True),
            ("message", "Comment Added"),
        ])

        return Response(response, status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class FriendViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = FriendSerializer

    def list(self, request, *args, **kwargs):
        author = get_object_or_404(Profile, id=kwargs['author_id'])
        serializer = self.serializer_class(author.friends, many=True)
        friendlist = []
        for ele in serializer.data:
            friendlist.append(ele.get('url'))
        response = OrderedDict([
            ("query", "friends"),
            ("authors", friendlist),
        ])
        return Response(response, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        author = get_object_or_404(Profile, id=kwargs['author_id'])
        friend = get_object_or_404(Profile, id=kwargs['pk'])
        if friend in author.friends.all():
            is_friend = True
        else:
            is_friend = False
        authors = Profile.objects.filter(id=kwargs['author_id']) | Profile.objects.filter(id=kwargs['pk'])
        serializer = self.serializer_class(authors, many=True)
        friendlist = []
        for ele in serializer.data:
            friendlist.append(ele.get('url'))
        response = OrderedDict([
            ("query", "friends"),
            ("authors", friendlist),
            ("friends", is_friend),
        ])
        return Response(response, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(Profile, id=kwargs['author_id'])
        friends = author.friends.all()
        possible_friends_url = request.data.get('authors')
        friendlist = []
        for possible_friend_url in possible_friends_url:
            possible_friend = get_object_or_404(Profile, url=possible_friend_url)
            if possible_friend in friends:
                friendlist.append(possible_friend_url)
        response = OrderedDict([
            ("query", "friends"),
            ("author", kwargs['author_id']),
            ("authors", friendlist),
        ])
        return Response(response, status=status.HTTP_200_OK)


class FriendRequestView(GenericAPIView):
    serializer_class = FriendRequestSerializer
    def post(self, request, *args, **kwargs):
        serializer = FriendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.handle()
        return Response(serializer.data)


def is_authenticated_to_read(post, author):
    if author.user.is_superuser:
        return True

    # Public
    if post.visibility == "PUBLIC":
        return True
    # Server Only
    if post.visibility == "SERVERONLY" and post.associated_author.host == author.host:
        return True
    # Own
    if post.associated_author == author:
        return True
    # Friends
    if post.visibility == "FRIENDS" and author in post.associated_author.friends.all():
        return True
    # FOAF
    if post.visibility == "FOAF":
        if author in post.associated_author.friends.all():
            return True
        for friend in post.associated_author.friends.all():
            if author in friend.friends.all():
                return True
    # Private
    if post.visibility == "PRIVATE" and author.url in post.visibleTo:
        return True

    return False


def get_readable_posts(author, posts):
    if author.user.is_superuser:
        return posts

    queryset = posts.filter(unlisted=False)
    # Public
    public_posts = queryset.filter(visibility="PUBLIC")
    # FOAF
    foaf_posts = queryset.none()
    for friend in author.friends.all():
        foaf_posts = foaf_posts | queryset.filter(associated_author=friend, visibility="FOAF")
        for foaf in friend.friends.all():
            foaf_posts = foaf_posts | queryset.filter(associated_author=foaf, visibility="FOAF")
    # Friends
    friends_posts = queryset.none()
    for friend in author.friends.all():
        friends_posts = friends_posts | queryset.filter(associated_author=friend, visibility="FRIENDS")
    # Private
    private_posts = queryset.filter(visibility="PRIVATE", visibleTo__contains=author.url)
    # Server Only
    serveronly_posts = queryset.filter(visibility="SERVERONLY", associated_author__host=author.host)
    # Own
    own_posts = queryset.filter(associated_author=author)
    posts_author_can_see = public_posts | foaf_posts | friends_posts | private_posts | serveronly_posts | own_posts

    return posts_author_can_see.order_by("-published")
