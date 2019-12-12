# Package: views.py
# View functions

from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.template import RequestContext, loader
#from django.core.context_processors import csrf
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

from movie.models import Movie,Vote
from movie.forms import MovieForm

# Function: home
# Home page of the application, renders all movies on
# an HTML table
def home(request):
	'''Home page of application, renders all movies on
	an HTML table.'''
	# this is longer version for authentication control
        # @login_required decorator does the same job

	if  not request.user.is_authenticated():
		return redirect("/login")

	# all movies as a list
	movielist = Movie.objects.all()

	# get all votes for current user
	votes = dict([(v.movie,v.vote) for v in 
				Vote.objects.filter(user=request.user)])

	# get all movies user has watched.
	# watched is a ManytoMany relation to User in Movie. In User
	# reverse relation is 'movie_set'.
	watchlist = request.user.movie_set.all()

	context = {'movielist':   movielist,
		 'votes': votes,
		 'username': request.user.username,
		 'watchlist': watchlist,
		 'choices':[1,2,3,4,5]}
	try:
		# if there is a message, it is added
		context['message'] = request.GET['msg']
	except:
		pass
	return render(request, "home.html", context)


# Function: add
# Display add movie page
@login_required(login_url='/login')
def add(request):
	'''Display add movie page'''

	# form data loaded form forms.py classMovieForm
	c = { 'form' : MovieForm() , 'action' : 'addmovie', 'button' : 'Add'}
	return render(request, "add.html", c)

# Function: addmovie
# Add movie action handler, adds the movie
@login_required(login_url='/login')
def addmovie(request):
	'''Add movie action handler, adds the movie'''
	p = request.POST

	try:
		# p is a dictionary of form data
		m = Movie.objects.create(title=p['title'], 
			director = p['director'],
			cast = p['cast'],
			imdb = p['imdb'])
		m.save()
	except:
		redirect('/?msg="Insertion failed"')
	# reload the home page after insertion
	return redirect('/?msg="Insertion successfull"')

# Function: update
# Display update movie page
@login_required(login_url='/login')
def update(request, updid):
	'''Display update movie page'''

	# form data loaded form forms.py classMovieForm
	# but initialized
	try:
		m = Movie.objects.get(id=int(updid))
	
		# form with prefill data in a dictionary
		mf = MovieForm({'title':m.title, 'imdb':m.imdb, 
				'director':m.director, 'cast':m.cast})

		# send form to template, this time prefilled
		c = { 'form' : mf , 'id': m.id, 'action' : 'updatemovie', 
			'button' : 'Update'}
	except:
		return redirect('/?msg=Movie does not exist')
	return render(request, "add.html", c)

# Function: updatemovie
# update movie action handler, updates the movie
@login_required(login_url='/login')
def updatemovie(request):
	'''Add movie action handler, adds the movie'''
	p = request.POST

	# p is a dictionary of form data
	try:
		m = Movie.objects.get(id=p['id'])
		m.title=p['title'] 
		m.director = p['director']
		m.cast = p['cast']
		m.imdb = p['imdb']
		m.save()
	except:
		return redirect('/?msg=Invalid movie or update failed')
	return redirect('/?msg=Update successfull')
	
# Function: watch
# Parameters: 
#    watchid -  movie id to toggle watch
# toggle watch status of a movie for user
@login_required(login_url='/login')
def watch(request,watchid):
	'''toggle watch status of movie'''
	u = request.user
	m = Movie.objects.get(id=int(watchid))
	# if user in current set of users watched movie
	if u in m.watched.all():
		# this is how to delete items on ManytoMany Fields
		m.watched.remove(u)
	else:
		# this is how to add items on ManytoMany Fields
		m.watched.add(u)
	return redirect('/')

# Function: vote
# Parameters:
#   voteid -  movie id to vote
#   voterate - rating for the movie
# Vote for given movie with voterate
def vote(request,voteid,voterate):
	'''Vote for given movie with voterate'''
	u = request.user
	# get Movie model
	m = Movie.objects.get(id=int(voteid))
	try:
		# get current vote of user
		v = Vote.objects.get(user=u, movie=m)
		# update vote
		v.vote = voterate
		v.save()
	except:	# not voted yet (get above failed)
		Vote.objects.create(user=u, movie=m, vote=voterate)

	return redirect('/')

# Function: delete
#  Delete the given movie
@login_required(login_url='/login')
def delete(request,likeid):
	'''Delete given movie'''
	m = Movie.objects.get(id=int(likeid))
	m.delete()
	return redirect('/')

# Function: login_view
#  Show login form
def login_view(request):
	'''Show login form'''
	context =  {'message':''}
	return render(request, 'login.html', context)

# Function: login_post
#  Login to system
def login_post(request):
	'''Login to system'''
	username = request.POST['username']
	password = request.POST['password']
	# check for authentication
	user = authenticate(username=username, password=password)
	if user is not None:
		# test if user is not disabled by admin
		if user.is_active:
			# create login session 
			login(request, user)
			return redirect("/")
		else:
			return render(request, 'login.html', {'message',
						'Account is disabled'})
	else:
		# Return an 'invalid login' error message.
		return render(request, 'login.html', {'message': 'Invalid username or password'})

# Function: logout_view
# logout from movie
def logout_view(request):
	'''Simply logout'''
	logout(request)
	return redirect("/")
	
