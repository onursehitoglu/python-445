from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from student.models import Department,Student,Course
# Create your views here.

@login_required
def register(request, stid = None):
	'''Show and process registration page
       stid is required for admin users to register a specific student
	'''
	try:
		if request.user.has_perms('student.add_student'): # admin user
			student = Student.objects.get(sid=stid)
		else:
			student = User.objects.get(username = request.user).student
	except:
		return render(request,'error.html', {'message': 'no student with id {} found'.format(stid)})

	try:
		if request.POST['submit'] == 'Add':	# form submitted, process it
			student.add(request.POST['course'])
			return redirect(register,stid=student.sid) # redirect to home page
		elif request.POST['submit'] == 'Drop':
			for v in request.POST.getlist('drop'):
				student.drop(v)
			return redirect(register,stid=student.sid)
		else:
			return render(request,'error.html',{'message':'Invalid request'})
	except KeyError:	# form not submitted yet, show it
		return render(request,'register.html', {'student':student, 'courselist': student.coursestoregister() })

@login_required
def update(request, stid):
	'''Show and process update form. 
	   Only admin can update student information. Other users should not see or post this'''

	if not request.user.has_perms('student.change_student'):
		return render(request, "error.html", {'message': 'You are not authorized to update students'})

	try:
		student = Student.objects.get(sid=stid)
	except:
		return render(request,'error.html',
			{'message': 'no student with id {} found'.format(stid)})

	# create a list of unassigned users + user of current student
	userlist = list(User.objects.filter(student=None)) + list(User.objects.filter(student=student))

	try:
		if request.POST['submit'] == 'Update':	# form submitted, process it
			student.name = request.POST['name']
			student.surname = request.POST['surname']
			if request.POST['user'] == 'NONE':
				student.user = None
			else:
				student.user = User.objects.get(username=request.POST['user'])
			student.save()
			return redirect(index) # redirect to home page
		elif request.POST['submit'] == 'Cancel':
			return redirect(index) # redirect to home page
		else:
			return render(request,'error.html',{'message':'Invalid request'})
	except KeyError:	# form not submitted yet, show it
		return render(request,'addupdatestudent.html', {'student':student, 'opname' : 'Update', 
				'userlist':userlist, 'formaction':'/student/update/{}'.format(stid)})

@login_required
def add(request):
	'''Show and process add student form. 
	   Only admin can add students. Other users should not see or post this'''

	try:
		if not request.user.has_perms('student.add_student'):
			return render(request, "error.html", {'message': 'You are not authorized to add students'})
		# create a list of unassigned users
		userlist = list(User.objects.filter(student=None))

		if request.POST['submit'] == 'Add':	# form submitted, process it
			if request.POST['user'] == 'NONE':
				user = None
			else:
				user = User.objects.get(username=request.POST['user'])

			student = Student.objects.create(sid=request.POST['sid'], name=request.POST['name'], 
				surname = request.POST['surname'], user = user)
			return redirect(index) # redirect to home page
		elif request.POST['submit'] == 'Cancel':
			return redirect(index) # redirect to home page
		else:
			return render(request,'error.html',{'message':'Invalid request'})
	except KeyError:	# form not submitted yet, show it
		return render(request, 'addupdatestudent.html', { 'opname':'Add', 'userlist' :userlist,
				'formaction':'/student/add'})
		


@login_required
def detail(request, stid = None):
	'''Show student details.
       admin can see all, student can only see their records'''
	try:
		if request.user.has_perms('student.add_student'): # admin user
			student = Student.objects.get(sid=stid)
		else:
			student = User.objects.get(username = request.user).student
	except:
		return render(request,'error.html',
			{'message': 'no student with id {} found'.format(stid)})
	
	return render(request,'details.html',{'student':student})

@login_required
def index(request):
	'''home page view
	   depending on if user is an administrator shows a list
       of student or simply directs to detail page for students
	'''

	students = []
	stmodel = Student.objects.all()

	if not request.user.has_perms('student.add_student'):
		try:
			student = User.objects.get(username = request.user).student
			return redirect(detail)
		except:
			return render(request, "error.html", {'message': 'No student associated with account'})

	for st in stmodel:
		students.append(st)
	return render(request,'student.html',{'st':students})

