from itertools import chain

from django.core.serializers import json
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.generics import ListCreateAPIView, GenericAPIView, UpdateAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required


from serializers import *
from pagination import *


class PostListView(ListCreateAPIView):
    queryset = Post.objects.filter(visibility="PUBLIC", unlisted=False).order_by('-published')
    serializer_class = PostSerializer
    pagination_class = PostsPagination


class PostDetailView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(self.queryset, id=kwargs['post_id'])
        author = get_object_or_404(Profile, id=request.user.profile.id)
        if is_authenticated_to_read(author, post):
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
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        author = get_object_or_404(Profile, id=self.request.user.profile.id)
        return get_readable_posts(author, self.queryset)


class AuthorPostsView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostsPagination
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        authorposts = self.queryset.filter(associated_author__id=self.kwargs['author_id'])
        author = get_object_or_404(Profile, id=self.request.user.profile.id)
        return get_readable_posts(author, authorposts)


class CommentView(ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentsPagination
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        author = get_object_or_404(Profile, id=self.request.user.profile.id)
        if is_authenticated_to_read(author, post):
            return self.queryset.filter(associated_post__id=self.kwargs['post_id']).order_by("-date_created")
        return self.queryset.none()

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=kwargs['post_id'])
        # author = get_object_or_404(Profile, id=request.user.profile.id)
        # if is_authenticated_to_read(author, post):
        #     serializer = AddCommentSerializer(data=request.data, context={'post_id': kwargs['post_id']})
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()
        #     response = OrderedDict([
        #         ("query", "addComment"),
        #         ("success", True),
        #         ("message", "Comment Added"),
        #     ])
        #     return Response(response, status=status.HTTP_200_OK)
        # else:
        #     response = OrderedDict([
        #         ("query", "addComment"),
        #         ("success", False),
        #         ("message", "Comment not allowed"),
        #     ])
        #     return Response(response, status=status.HTTP_403_FORBIDDEN)
        serializer = AddCommentSerializer(data=request.data, context={'post_id': kwargs['post_id']})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = OrderedDict([
            ("query", "addComment"),
            ("success", True),
            ("message", "Comment Added"),
        ])
        return Response(response, status=status.HTTP_200_OK)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)



class FriendViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = FriendURLSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    # GET http://service/author/<authorid>/friends/
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

    # GET http://service/author/<authorid>/friends/<authorid2>
    def retrieve(self, request, *args, **kwargs):
        author = get_object_or_404(Profile, id=kwargs['author_id'])

        is_friend = False
        for friend in author.friends.all():
            if friend.id == kwargs['pk']:
                is_friend = True
                break

        try:
            friend = Friend.objects.get(id=kwargs['pk'])
        except Friend.DoesNotExist:
            response = OrderedDict([
                ("query", "friends"),
                ("friends", is_friend),
            ])
        else:
            friendlist = list()
            friendlist.append(author.url)
            friendlist.append(friend.url)
            response = OrderedDict([
                ("query", "friends"),
                ("authors", friendlist),
                ("friends", is_friend),
            ])

        return Response(response, status=status.HTTP_200_OK)

    # ask a service if anyone in the list is a friend
    # POST http://service/author/<authorid>/friends
    def create(self, request, *args, **kwargs):
        author = get_object_or_404(Profile, id=kwargs['author_id'])
        friends = author.friends.all()
        possible_friends_url = request.data.get('authors')
        friendlist = []
        for possible_friend_url in possible_friends_url:
            try:
                possible_friend = Friend.objects.get(url=possible_friend_url)
            except Friend.DoesNotExist:
                pass
            else:
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


def is_authenticated_to_read(requestor, post):
    # admin
    if requestor.user.is_superuser:
        return True

    # Public
    if post.visibility == "PUBLIC":
        return True
    # Server Only
    if post.visibility == "SERVERONLY" and post.associated_author.host == requestor.host:
        return True
    # Own
    if post.associated_author == requestor:
        return True
    # Friend, FOAF
    try:
        friend = Friend.objects.get(id=requestor.id)
        if (post.visibility == "FRIENDS" or post.visibility == "FOAF") and friend in post.associated_author.friends.all():
            return True
    except Friend.DoesNotExist as e:
        if post.visibility == "FOAF":
            for friend in post.associated_author.friends.all():
                # Verify the middle friend is a friend of requestor
                if friend in requestor.friends().all():
                    return True
    # Private
    if post.visibility == "PRIVATE" and requestor.url in post.visibleTo:
        return True

    return False


def get_readable_posts(requestor, posts):
    if requestor.user.is_superuser:
        return posts

    queryset = posts.filter(unlisted=False)
    for post in queryset:
        if not is_authenticated_to_read(requestor, post):
            queryset.remove(post)
    return queryset.order_by("-published")

    # # Public
    # public_posts = queryset.filter(visibility="PUBLIC")
    # # FOAF
    # foaf_posts = queryset.none()
    # for friend in requestor.friends.all():
    #     foaf_posts = foaf_posts | queryset.filter(associated_author__id=friend, visibility="FOAF")
    #     for foaf in friend.friends.all():
    #         foaf_posts = foaf_posts | queryset.filter(associated_author=foaf, visibility="FOAF")
    # # Friends
    # friends_posts = queryset.none()
    # for friend in requestor.friends.all():
    #     friends_posts = friends_posts | queryset.filter(associated_author=friend, visibility="FRIENDS")
    # # Private
    # private_posts = queryset.filter(visibility="PRIVATE", visibleTo__contains=requestor.url)
    # # Server Only
    # serveronly_posts = queryset.filter(visibility="SERVERONLY", associated_author__host=requestor.host)
    # # Own
    # own_posts = queryset.filter(associated_author=requestor)
    # posts_author_can_see = public_posts | foaf_posts | friends_posts | private_posts | serveronly_posts | own_posts
    #
    # return posts_author_can_see.order_by("-published")
