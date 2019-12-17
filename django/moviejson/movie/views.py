# Title: views.py
# Django views (json)
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from movie.models import Movie,Vote
from movie.forms import MovieForm

import json


# Function: home(request)
# Default home view. Renders 'home.html' template
def home(request):
	return render(request, 'home.html',{'username':request.user.username})
	
# Function: getmovie(movie)
# Return a dictionary representing the movie object
#
# Returns:
#	Dictionary of all fields of a movie
def getmovie(movie):
	r = {}
	for i in ['id','title','imdb','director','cast']:
		r[i] = getattr(movie,i)
	r['votes'] = movie.votes()
	r['watches'] = movie.watches()
	return r

# Function: success(obj,name)
# Return a successfull result in JSON httpresponse
def success(obj, name):
	return HttpResponse(json.dumps({'result':'Success',name : obj}),
				'text/json')

# Function: error(reason)
# Return a successfull result in JSON
def error(reason):
	return HttpResponse(json.dumps({'result':'Fail','reason' : reason}),
				'text/json')

# Function: list(request)
# View returning the list of movies as a json list
@login_required(login_url='/notauth')
def list(request):
	movielist = [getmovie(m) for m in Movie.objects.all()]
	return success(movielist,'movielist')

# Function: mget(request, movieid)
# View returning a single movie for given <movieid>
#
# Parameters:
#	movieid - id of the movie
@login_required(login_url='/notauth')
def mget(request, movieid):
	try:
		movie = Movie.objects.get(id=movieid)
		return success(getmovie(movie),'movie')
	except:
		return error('Movie not found')


# Function: votes(request)
# View returning votes of the current user, list of movieid,vote pairs in JSON
@login_required(login_url='/notauth')
def votes(request):
	votes = [{'movieid':v.movie.id, 'vote':v.vote}
		 for v in Vote.objects.filter(user = request.user)]
	return success(votes,'votes')

# Function: watches(request)
# View returning list of watched movies for current user, list of movieids in JSON
@login_required(login_url='/notauth')
def watches(request):
	# watched__in = [user] queries many to many objects
 	# if user in watched list for movie, returns true
	watches = [{'id':m.id}
		 for m in Movie.objects.filter(watched__in=[request.user])]
	return success(watches, 'watches')

# Function: noauth(request)
# View returning authentication error, other views redirected to this in case of 
# user not authenticated
def notauth(request):
		return error('Authentication')

# Function: log(request)
# View for authentication of the user. login form posted to this view
# returns the result of authentication as an JSON value.
def log(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			return success('Login successfull','message')
		else:
			return error('User is disabled')
	else:
		# Return an 'invalid login' error message.
		return error('Authentication')

# Function: addmovie(request)
# View for adding a movie. Add movie form is posted on this view
# result is returned as a JSON value. On success movieid is included in the result
@login_required(login_url='/notauth')
def addmovie(request):
	try:
		f = MovieForm(request.POST)
		if not f.is_valid():
			raise Exception
		m = Movie.objects.create(title=f['title'].value(), 
			director = f['director'].value(),
			cast = f['cast'].value(),
			imdb = f['imdb'].value())
		m.save()
		return success({'id': m.id, 'message':'Movie added'},
			'success')
	except:
		return error('Invalid form data')

# Function: updmovie(request)
# View for updating a movie. Update movie form is posted on this view
# result is returned as JSON. 
@login_required(login_url='/notauth')
def updmovie(request):
	try:
		f = MovieForm(request.POST)
		if not f.is_valid():
			raise Exception
		m = Movie.objects.get(id=request.POST['id'])
		m.title = f['title'].value()
		m.director = f['director'].value()
		m.cast = f['cast'].value()
		m.imdb = f['imdb'].value()
		m.save()
		return success('Movie updated','message')
	except:
		return error('Invalid form data')
	
# Function: watch(request,watchid)
# View for marking as a movie watched or not watched. Flips the current state
# for current user.
#
# Parameters:
#	watchid - id of the movie to change state
@login_required(login_url='/notauth')
def watch(request,watchid):
	try:
		u = request.user
		m = Movie.objects.get(id=int(watchid))
		if u in m.watched.all():
			m.watched.remove(u)
		else:
			m.watched.add(u)
		return success('Watch switched','message')
	except:
		return error('Invalid operation')

# Function: vote(request,voteid, voterate)
# View for voting a movie. Creates a vote record for current user.
#
# Parameters:
#	voteid - id of the movie to vote
#	voterate - rating given by the user
@login_required(login_url='/notauth')
def vote(request,voteid,voterate):
	try:
		u = request.user
		m = Movie.objects.get(id=int(voteid))
		try:
			v = Vote.objects.get(user=u, movie=m)
		except:	# not voted yet
			v = Vote.objects.create(user=u, movie=m, vote=voterate)

		v.vote = voterate
		v.save()

		return success('Voted successfully','message')
	except:
		return error('Cannot vote')

# Function: delete(request,delid)
# View for deleting a movie. 
#
# Parameters:
#	delid - id of the movie to delete
@login_required(login_url='/notauth')
def delete(request,delid):
	try:
		m = Movie.objects.get(id=int(delid))
		m.delete()
		return success('Deleted','message')
	except:
		return error('Cannot delete')


# Function: logout_view(request):
# ending current session
def logout_view(request):
	logout(request)
	return redirect("/")
	
