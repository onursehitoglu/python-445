from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^detail/(?P<stid>[0-9]{5,})?$', views.detail, name='detail'),
    url('^update/(?P<stid>[0-9]{5,})$', views.update, name='update'),
    url('^add$', views.add, name='add'),
    url('^register/(?P<stid>[0-9]{5,})?$', views.register, name='register'),
]
