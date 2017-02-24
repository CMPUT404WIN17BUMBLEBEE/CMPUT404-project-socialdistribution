from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Examples:
    #url(r'^$', 'socialdistribution.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^posts/', include('posts.urls', namespace='posts')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^register/$', 'authors.views.register', name='register'),
    url(r'^register/complete/$', 'authors.views.registration_complete',
 name='registration_complete'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]
