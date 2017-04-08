from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from rest_framework import routers
from api_views import *

# Based on http://www.django-rest-framework.org/tutorial/quickstart/
router = routers.DefaultRouter()
router.register(r'author', ProfileViewSet, base_name="Profile")
router.register(r'author/(?P<author_id>[a-z0-9-]+)/friends', FriendViewSet, base_name="Friend")


urlpatterns = [
    url(r'^api/posts/$', PostListView.as_view(), name='post-list'),
    url(r'^api/posts/(?P<post_id>[a-z0-9-]+)/$', PostDetailView.as_view(), name='post-detail'),
    url(r'^api/author/posts/$', PostsAuthorCanSeeView.as_view(), name='posts-author-can-see'),
    url(r'^api/author/(?P<author_id>[a-z0-9-]+)/posts/$', AuthorPostsView.as_view(), name='author-posts'),

    url(r'^api/posts/(?P<post_id>[a-z0-9-]+)/comments/$', CommentView.as_view(), name='comments'),

    url(r'^api/friendrequest/$', FriendRequestView.as_view(), name='friend-request'),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

]
