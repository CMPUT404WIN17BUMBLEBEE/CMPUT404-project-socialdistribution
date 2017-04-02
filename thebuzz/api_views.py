
from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import ListCreateAPIView, GenericAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK


from serializers import *
from pagination import *

from .models import *
from authorization import is_authorized_to_read_local_post, get_readable_local_posts, is_authorized_to_comment


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
        if is_authorized_to_read_local_post(request.user.profile, post):
            serializer = self.serializer_class(post)
            return Response(serializer.data)


    def post(self, request, *args, **kwargs):
        serializer = GetPostSerializer(data=request.data)
        if serializer.get_read(data=request.data):
            post = get_object_or_404(self.queryset, id=kwargs['post_id'])
            serializer = self.serializer_class(post)
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class PostsAuthorCanSeeView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostsPagination
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return get_readable_local_posts(self.request.user.profile, self.queryset)


class AuthorPostsView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostsPagination
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        authorposts = self.queryset.filter(associated_author__id=self.kwargs['author_id'])
        return get_readable_local_posts(self.request.user.profile, authorposts)


class CommentView(ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentsPagination
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        author = get_object_or_404(Profile, id=self.request.user.profile.id)
        if is_authorized_to_read_local_post(author, post):
            return self.queryset.filter(associated_post__id=self.kwargs['post_id']).order_by("-date_created")
        return self.queryset.none()

    def post(self, request, *args, **kwargs):

        split = request.data.get('comment').get('author').get('id').split("/")
        split = [x for x in split if x]
        actual_id = split[-1]
        d = (request.data)
        d['comment']['author']['id'] = actual_id

        post = get_object_or_404(Post, id=kwargs['post_id'])
        if is_authorized_to_comment(actual_id, post, request.data['comment']['author']['host']):
            serializer = AddCommentSerializer(data=request.data, context={'post_id': kwargs['post_id']})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = OrderedDict([
                ("query", "addComment"),
                ("success", True),
                ("message", "Comment Added"),
            ])
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = OrderedDict([
                ("query", "addComment"),
                ("success", False),
                ("message", "Comment not allowed"),
            ])
            return Response(response, status=status.HTTP_403_FORBIDDEN)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.filter(user__is_staff=False)
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
        serializer = self.serializer_class(author.following, many=True)
        friendlist = []
        for ele in serializer.data:
            friendlist.append(ele.get('url'))
        response = OrderedDict([
            ("query", "friends"),
            ("authors", friendlist),
        ])
        return Response(response, status=status.HTTP_200_OK)

    # GET http://service/author/<authorid>/friends/<authorid2>
    # Check if two users are friends
    def retrieve(self, request, *args, **kwargs):
        author = get_object_or_404(Profile, id=kwargs['author_id'])

        is_friend = False
        for friend in author.following.all():
            if str(friend.id) == kwargs['pk']:
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
        friends = author.following.all()
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

class RemoteFriendView(GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = FriendURLSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    # GET http://service/author/<author_id>/friends/service2/author/<friend_id>/
    # Check if two users are friends
    def get(self, request, *args, **kwargs):
        author = get_object_or_404(Profile, id=kwargs['author_id'])

        is_friend = False
        for friend in author.following.all():
            if kwargs['friend_id'] in str(friend.url):
                is_friend = True
                break

        try:
            friend = Friend.objects.get(url__contains=kwargs['friend_id'])
        except:
            friendlist = list()
            friendlist.append(author.url)
            friendlist.append('http://'+kwargs['friend_id'])
            response = OrderedDict([
                ("query", "friends"),
                ("authors", friendlist),
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

class FriendRequestView(GenericAPIView):
    serializer_class = FriendRequestSerializer
    def post(self, request, *args, **kwargs):
        print(str(request.data))
        # firend id handling
        id = str(request.data.get('author').get('id')).split('author/')[-1]
        id = id.replace('/', '')
        request.data['author']['id'] = id

        id = str(request.data.get('friend').get('id')).split('author/')[-1]
        id = id.replace('/', '')
        request.data['friend']['id'] = id
        print(str(request.data))
        serializer = FriendRequestSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.handle()
        return Response(serializer.data)

