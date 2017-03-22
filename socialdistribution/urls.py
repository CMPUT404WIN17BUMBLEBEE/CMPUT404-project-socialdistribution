from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers
#from thebuzz import api_views, views

from thebuzz.api_views import *
import thebuzz.views


# Based on http://www.django-rest-framework.org/tutorial/quickstart/
router = routers.DefaultRouter()
#router.register(r'posts', PublicPostsViewSet, base_name="Posts")
#router.register(r'author/posts', PostsAuthorCanSeeViewSet, base_name="PostsAuthorCanSee")
#router.register(r'author/(?P<author_id>[a-z0-9-]+)/posts', AuthorPostsViewSet, base_name="AuthorPosts")
router.register(r'author', ProfileViewSet, base_name="Profile")
router.register(r'author/(?P<author_id>[a-z0-9-]+)/friends', FriendViewSet, base_name="Friend")

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', auth_views.login, name='login'),

    url(r'^posts/$', 'thebuzz.views.posts', name='posts'),
    url(r'^posts/(?P<post_id>[0-9a-f-]+)/detail.html$', 'thebuzz.views.post_detail', name='post_detail'),
    url(r'^posts/post_form_upload.html$', 'thebuzz.views.post_form_upload', name='post_form_upload'),


    url(r'^posts/(?P<post_id>[0-9a-f-]+)/add_comment.html$', 'thebuzz.views.add_comment', name='add_comment'),
    url(r'^posts/(?P<post_id>[0-9A-Fa-f-]+)/delete/$', 'thebuzz.views.DeletePost', name="delete_comment"),

    url(r'^register/$', 'thebuzz.views.register', name='register'),
    url(r'^register/complete/$', 'thebuzz.views.registration_complete', name='registration_complete'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login/'}, name='logout'),

    url(r'^author/(?P<profile_id>[0-9a-f-]+)/profile$', 'thebuzz.views.profile', name='profile'),
    url(r'^author/(?P<profile_id>[0-9a-f-]+)/edit_profile$', 'thebuzz.views.edit_profile', name='edit_profile'),

    #Change 'thebuzz.view.[] so that it calls the appropriate method in views to get or add
    url(r'^friends/$', 'thebuzz.views.friends', name='friends'),
    url(r'^friends/(?P<profile_id>[0-91-f-]+)/delete_friend$', 'thebuzz.views.delete_friend', name='delete_friend'),

    # API urls
    #url(r'^', include('api_urls')),
    url(r'^api/posts/$', PostListView.as_view(), name='post-list'),
    url(r'^api/posts/(?P<post_id>[a-z0-9-]+)/$', PostDetailView.as_view(), name='post-detail'),
    url(r'^api/author/posts/$', PostsAuthorCanSeeView.as_view(), name='posts-author-can-see'),
    url(r'^api/author/(?P<author_id>[a-z0-9-]+)/posts/$', AuthorPostsView.as_view(), name='author-posts'),

    url(r'^api/posts/(?P<post_id>[a-z0-9-]+)/comments/$', CommentView.as_view(), name='comments'),

    url(r'^api/friendrequest/$', FriendRequestView.as_view(), name='friend-request'),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

#url(r'^posts/post_form_upload.html$', 'thebuzz.views.post_form_upload', name='post_form_upload'),
#url(r'^ajax/uploadText/', 'thebuzz.views.uploadText'),
#url(r'^ajax/uploadImage/', 'thebuzz.views.image_form_upload'),
