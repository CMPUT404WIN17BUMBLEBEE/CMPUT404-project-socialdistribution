from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'socialdistribution.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^posts/', include('posts.urls', namespace='posts')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^authors/register/$', 'authors.views.register', name='register'),
    url(r'^authors/register/complete/$', 'authors.views.registration_complete',
 name='registration_complete'),
]
