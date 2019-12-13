# Title: views.py
# Django views
from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.template import RequestContext, loader
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from movie.models import Movie,Vote
from movie.forms import MovieForm

# Function: getobject(req, obj, objname, objcols)
# return renderered xml for an object
#
# Parameters:
#  req - request
#  obj - object dictionary
#  objname - name of the object in XML tags
#  objcols - coloumns to export in XML
def getobject(req,obj, objname, objcols):
	context = {'obj':   obj,
		 'objname': objname,
		 'objcols': objcols,
		 'result' : 'Success' if obj else 'Not Found'}
	return render(req, 'object.xml', context)

# Function: getlist(req, objlist, objname, objcols)
# return renderered xml for a list of objects
#
# Parameters:
#  req - request
#  objlist - list of object dictionaries
#  objname - name of the object in XML tags
#  objcols - coloumns to export in XML
def getlist(req,objlist, objname, objcols):
	context = {'objlist':   objlist,
		 'objname': objname,
		 'objcols': objcols,
		'result': 'Success' if objlist else 'Not Found'}
	return render(req, 'list.xml', context)

# Function: geterror(req, mess)
# returns an xml error representation
#
# Parameters:
#	req - request object
#	mess - message as the fail reason
def geterror(req,mess):
	#template = loader.get_template('error.xml')
	#context = RequestContext(req, 
	context =	{'result': 'Fail', 'reason': mess }
	return render(req, "error.xml",context)
	#return template.render(context)

# Function: getsuccess(req, mess)
# returns an xml success representation
#
# Parameters:
#	req - request object
#	mess - success message
def getsuccess(req,mess):
	context = {'result': 'Success', 'reason': mess}
	return render(req, "error.xml", context)
		  

# Function: home(request)
# Default home view. Renders 'home.html' template
def home(request):
	#template = loader.get_template('home.html')
	context =  {'username':request.user.username}
	#context.update(csrf(request))
	#return HttpResponse(template.render(context),'text/html')
	return render(request, "home.html",context)
	

# Function: list(request)
# View returning the list of movies in XML
@login_required(login_url='/notauth')
def list(request):
	movielist = Movie.objects.all()
	return HttpResponse(getlist(request, movielist, 'movie',
			['title','imdb','director','cast','watches','votes']),
		'text/xml')

# Function: mget(request, movieid)
# View returning a single movie for given <movieid>
#
# Parameters:
#	movieid - id of the movie
@login_required(login_url='/notauth')
def mget(request, movieid):
	try:
		movie = Movie.objects.get(id=movieid)
	except:
		movie = None

	return HttpResponse(getobject(request, movie, 'movie',
			['title','imdb','director','cast','watches','votes']),
		'text/xml')

# Function: votes(request)
# View returning votes of the current user, list of movieid,vote pairs in XML
@login_required(login_url='/notauth')
def votes(request):
	votes = [{'id':v.id, 'movieid':v.movie.id, 'vote':v.vote}
		 for v in Vote.objects.filter(user = request.user)]
	return HttpResponse(getlist(request, votes, 'vote',
			['movieid','vote']),
		'text/xml')

# Function: watches(request)
# View returning list of watched movies for current user, list of movieids in XML
@login_required(login_url='/notauth')
def watches(request):
	# watched__in = [user] queries many to many objects
 	# if user in watched list for movie, returns true
	watches = [{'id':m.id}
		 for m in Movie.objects.filter(watched__in=[request.user])]
	return HttpResponse(getlist(request, watches, 'watch',
			[]),
		'text/xml')

# Function: noauth(request)
# View returning authentication error, other views redirected to this in case of 
# user not authenticated
def notauth(request):
		return HttpResponse(geterror(request,'Authentication'),
			'text/xml')

# Function: log(request)
# View for authentication of the user. login form posted to this view
# returns the result of authentication as an XML value.
def log(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			return HttpResponse(getsuccess(request,
				"Login successfull"), 'text/xml');
		else:
			return HttpResponse(geterror(request,
				'User is disabled'), 'text/xml')
	else:
		# Return an 'invalid login' error message.
		return HttpResponse(geterror(request,
			'Invalid username or password'), 'text/xml')

# Function: addmovie(request)
# View for adding a movie. Add movie form is posted on this view
# result is returned as an XML. On success movieid is included in the result
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
		return HttpResponse(getobject(request,
			{'id': m.id, 'message':'Movie added'},
			'success',['id','message']),
				'text/xml')
	except:
		return HttpResponse(geterror(request,'Invalid form data'),
				'text/xml')

# Function: updmovie(request)
# View for updating a movie. Update movie form is posted on this view
# result is returned as an XML. 
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
		return HttpResponse(getobject(request,
			{'message':'Movie updated'},'success',['message']),
				'text/xml')
	except:
		return HttpResponse(geterror(request,'Invalid form data'),
				'text/xml')
	
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
		return HttpResponse(getobject(request,
			{'message':'Watch switched'},'success',['message']),
				'text/xml')
	except:
		return HttpResponse(geterror(request,'Invalid operation',
				'text/xml'))

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

		return HttpResponse(getsuccess(request,
				'Voted successfully'), 'text/xml')
	except:
		return HttpResponse(geterror(request,'Cannot vote',
				'text/xml'))

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
		return HttpResponse(getobject(request,
			{'message':'Deleted'},'success',['message']),
				'text/xml')
	except:
		return HttpResponse(geterror(request,'Cannot delete',
				'text/xml'))


# Function: logout_view(request):
# ending current session
def logout_view(request):
	logout(request)
	return redirect("/")
	
