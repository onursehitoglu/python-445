from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.core.exceptions import ObjectDoesNotExist
from home.models import Question,Reply,Tag

# Create your views here.

def home(request):
	return render(request, "home.html", { 'questions': Question.objects.all() })

def viewquestion(request,qid):
	try:
		q = Question.objects.get(id=qid)
		return render(request, "question.html",{'question':q})
	except ObjectDoesNotExist:
		return redirect("/")

def addquestion(request):
	q = Question.objects.create(qtitle = request.POST['title'], qtext = request.POST['qtext'])
	for t in request.POST['tags'].split(','):
		try:
			tag = Tag.objects.get(text = t)
		except ObjectDoesNotExist:
			tag = Tag.objects.create(text = t)
		q.tag.add(tag)
	return redirect("/")

