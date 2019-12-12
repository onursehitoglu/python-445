from django.conf.urls import include, url
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
]

