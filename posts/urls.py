from django.conf.urls import url
from . import views
urlpatterns = [
	url(r'^$', views.index, name='index'),
]

#posts/ should be in front of the three later ones, but for some reason it does not work when they are
