# Package: urls.py
# Project URL routing configuration
"""ceng445 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import  path, include
from django.contrib import admin

import movie.views

# Variable: urlpatterns
# used to map patterns
urlpatterns = [
#       HOME page
    path('', movie.views.home, name='Movie Party Application'),
#       ADD movie page
    path('add', movie.views.add, name='Add new movie'),
#       ADD movie action
    path('addmovie', movie.views.addmovie, name='Add new movie'),
#       UPDATE movie page
    path('update/<int:updid>', movie.views.update, name='Update movie'),
#       UPDATE movie action
    path('updatemovie', movie.views.updatemovie, name='Update movie'),
#       CHANGE watch status of movie
    path('watch/<int:watchid>', movie.views.watch, name='Change watch'),
#       VOTE/movieid/1-5
    path('vote/<int:voteid>/<int:voterate>', movie.views.vote, name='Vote movie'),
#       DELETE movie
    path('delete/<int:delid>', movie.views.delete, name='Add new movie'),
#       LOGOUT
    path('logout', movie.views.logout_view, name='Logout'),
#       LOGIN post
    path('loginp', movie.views.login_post, name='Login'),
#       LOGIN page
    path('login', movie.views.login_view, name='Login'),
#       uncomment if python-django-registration is installed
#    path(r'^accounts/', include('registration.backends.default.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
#    path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    path('admin/', admin.site.urls),
]
