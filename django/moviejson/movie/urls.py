from django.urls import include, re_path
#from django.conf.urls import include, url
#    '^$'	-	 'poll., views.home'
#    '^list$'	-	 'poll., views.list'
#    '^get/([0-9]+)$'	-	 'poll., views.mget'
#    '^votes$'	-	 'poll., views.votes'
#    '^watches$'	-	 'poll., views.watches'
#    '^notauth$'	-	 'poll., views.notauth'
#    '^addmovie$'	-	 'poll., views.addmovie'
#    '^updmovie$'	-	 'poll., views.updmovie'
#    '^watch/([0-9]+)$'	-	 'poll., views.watch'
#    '^vote/([0-9]+)/([1-5])$'	-	 'poll., views.vote'
#    '^delete/([0-9]+)$'	-	 'poll., views.delete'
#    '^logout$'	-	 'poll., views.logout_view'
#    '^logp$'	-	 'poll., views.log'
from movie import views

urlpatterns = [
    re_path(r'^$', views.home, name='Movie Party Application'),
    re_path(r'^list$', views.list, name='Movie Party Application'),
    re_path(r'^get/([0-9]+)$', views.mget, name='Add new movie'),
    re_path(r'^votes$', views.votes, name='Add new movie'),
    re_path(r'^watches$', views.watches, name='Add new movie'),
    re_path(r'^notauth$', views.notauth, name='Add new movie'),
    re_path(r'^addmovie$', views.addmovie, name='Add new movie'),
    re_path(r'^updmovie$', views.updmovie, name='Add new movie'),
    re_path(r'^watch/([0-9]+)$', views.watch, name='Add new movie'),
    re_path(r'^vote/([0-9]+)/([1-5])$', views.vote, name='Add new movie'),
    re_path(r'^delete/([0-9]+)$', views.delete, name='Add new movie'),
    re_path(r'^logout$', views.logout_view, name='Logout'),
    re_path(r'^logp$', views.log, name='Login'),
]

