from django.urls import re_path

from . import views

urlpatterns = [
    re_path('^$', views.index, name='index'),
    re_path('^detail/(?P<stid>[0-9]{5,})?$', views.detail, name='detail'),
    re_path('^update/(?P<stid>[0-9]{5,})$', views.update, name='update'),
    re_path('^add$', views.add, name='add'),
    re_path('^register/(?P<stid>[0-9]{5,})?$', views.register, name='register'),
]
