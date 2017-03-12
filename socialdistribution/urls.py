from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from router import router

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

    url(r'^profile/$', 'thebuzz.views.profile', name='profile'),
    url(r'^profile/edit_profile$', 'thebuzz.views.edit_profile', name='edit_profile'),

    #Change 'thebuzz.view.[] so that it calls the appropriate method in views to get or add
    url(r'^friends/$', 'thebuzz.views.homePage', name='friends'),
    url(r'^friends/add_friends$', 'thebuzz.views.add_friends', name='add_friend'),
    url(r'^friends/(?P<profile_id>[0-91-f-]+)/delete_friend$', 'thebuzz.views.delete_friend', name='delete_friend'),

    url(r'^api/', include(router.urls))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

#url(r'^posts/post_form_upload.html$', 'thebuzz.views.post_form_upload', name='post_form_upload'),
#url(r'^ajax/uploadText/', 'thebuzz.views.uploadText'),
#url(r'^ajax/uploadImage/', 'thebuzz.views.image_form_upload'),
