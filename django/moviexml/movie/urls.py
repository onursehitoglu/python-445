# Title: urls.py
# Url mappings to views
from django.conf.urls import include, url

# Variable: urlpatterns
# url mappings for views
#
#    '^$'   -    'views.home'
#    '^list$'   -    'views.list'
#    '^get/([0-9]+)$'   -    'views.mget'
#    '^votes$'  -    'views.votes'
#    '^watches$'    -    'views.watches'
#    '^notauth$'    -    'views.notauth'
#    '^addmovie$'   -    'views.addmovie'
#    '^updmovie$'   -    'views.updmovie'
#    '^watch/([0-9]+)$' -    'views.watch'
#    '^vote/([0-9]+)/([1-5])$'  -    'views.vote'
#    '^delete/([0-9]+)$'    -    'views.delete'
#    '^logout$' -    'views.logout_view'
#    '^logp$'   -    'views.log'

from movie import views

urlpatterns = [
   url(r'^$', views.home, name='Movie Party Application'),
    url(r'^list$', views.list, name='Movie Party Application'),
    url(r'^get/([0-9]+)$', views.mget, name='Add new movie'),
    url(r'^votes$', views.votes, name='Add new movie'),
    url(r'^watches$', views.watches, name='Add new movie'),
    url(r'^notauth$', views.notauth, name='Add new movie'),
    url(r'^addmovie$', views.addmovie, name='Add new movie'),
    url(r'^updmovie$', views.updmovie, name='Add new movie'),
    url(r'^watch/([0-9]+)$', views.watch, name='Add new movie'),
    url(r'^vote/([0-9]+)/([1-5])$', views.vote, name='Add new movie'),
    url(r'^delete/([0-9]+)$', views.delete, name='Add new movie'),
    url(r'^logout$', views.logout_view, name='Logout'),
    url(r'^logp$', views.log, name='Login'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
]

