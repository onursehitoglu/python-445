# Title: models.py
# django models
from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

# Function: validate_vote
# Check if given vote is in range [1,5]
# used by <Vote> model class
def validate_vote(val):
	if val < 1 or val > 5:
		raise ValidationError('Invalid vote [1..5]')

# Create your models here.

# Class: Movie
# Movie class
class Movie(models.Model):
	class Meta:
		ordering = ['title']
	# Variable: title
	title = models.CharField(max_length=200)
	# Variable: imdb
	imdb = models.CharField(max_length=20)
	# Variable: director
	director = models.CharField(max_length=100)
	# Variable: cast
	cast = models.CharField(max_length=100)

	# Variable: watched
	# many to many relation with user. gives a set of users
	watched = models.ManyToManyField(User)

	def __unicode__(self):
		return self.title

	# Function: votes
	# returns the average votes given to the movie
	# iterates over <Vote> objects for the movie.
	def votes(self):
		'''return number of people voted for this movie'''
		l = [v.vote for v in Vote.objects.filter(movie=self)]
		if len(l) > 0:
			return "%.1f" % (sum(l)*1.0/len(l))
		else:
			return "???"

	# Function: watches
	# returns the total number of user watched the movie
	# number of elements in <watched> set.
	def watches(self):
		'''return number of people watched this movie'''
		return len(self.watched.all())


# Class: Vote
# Model class for movie votes. It keeps movieid,user,vote relation per movie,user pair.
class Vote(models.Model):
	class Meta:
		unique_together = (('user','movie'),)
	# Variable: user
	# A foreign key to User class in django.contrib.auth
	user = models.ForeignKey(User, models.CASCADE)
	# Variable: movie
	# A foreign key to <Movie> model class
	movie = models.ForeignKey(Movie, models.CASCADE)
	# Variable: vote
	# vote of the user on the movie, an integer in [1,5]
	vote = models.IntegerField(validators=[validate_vote])

	def __unicode__(self):
		return self.user.username + ":" + self.movie.title
