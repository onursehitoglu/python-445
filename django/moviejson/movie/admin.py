from django.contrib import admin

# Register your models here.
from movie.models import Movie,Vote

admin.site.register(Movie)
admin.site.register(Vote)

