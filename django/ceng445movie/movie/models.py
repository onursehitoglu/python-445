# Package: models.py
# Models for movie application

from __future__ import unicode_literals

from django.db import models

# Create your models here.

# for loading user model from django user app.
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError


# Create your models here.

# Class: Movie
#	Movie model class
#	watched is ManyToManyField relation
#	keeping which user watched this movie
class Movie(models.Model):
	class Meta:		
	# set default ordering field  for movies
		ordering = ['title']
	title = models.CharField(max_length=200)
	imdb = models.CharField(max_length=20)
	director = models.CharField(max_length=100)
	cast = models.CharField(max_length=100)
# illustrates many to many relation
	watched = models.ManyToManyField(User)

	def __str__(self):
		return self.title

	# Function: votes(self)
	#   return string representation of average votes given
	#   for this movie
	def votes(self):
		'''return number of people voted for this movie'''
		l = [v.vote for v in Vote.objects.filter(movie=self)]
		if len(l) > 0:
			return "%.1f" % (sum(l)*1.0/len(l))
		else:
			return "???"

	# Function: watches(self)
	#   return number of people watched this movie
	def watches(self):
		'''return number of people watched this movie'''
		return len(self.watched.all())

# Function: validate_vote(val)
#	Check if a vote value is valid, in [1-5]
def validate_vote(val):
	if val < 1 or val > 5:
		raise ValidationError('Invalid vote [1..5]')

# Class: Vote
#   model class for keeping votes of a movie
#   it is a many to many relation however also
#   keeps a vote value
class Vote(models.Model):
	class Meta:
		unique_together = (('user','movie'),)
	user = models.ForeignKey(User)
	movie = models.ForeignKey(Movie)
	vote = models.IntegerField(validators=[validate_vote])

	def __str__(self):
		return self.user.username + ":" + self.movie.title
