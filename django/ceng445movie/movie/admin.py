'''Create default forms for Movie and Vote in /admin/ site'''
from django.contrib import admin

from movie.models import Movie,Vote

admin.site.register(Movie)
admin.site.register(Vote)
