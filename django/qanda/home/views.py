from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from home.models import Question,Reply,Tag

# Create your views here.

def home(request,tagname=None, search=None):
	if tagname == None and search == None:
		questions = Question.objects.all() 
	elif search == None: 
		try:
			t = Tag.objects.get(text = tagname)
			questions = t.question_set.all()
		except ObjectDoesNotExist:
			questions = []
	else:
			tags = Tag.objects.filter(text__icontains = search)
			print(tags, search)
			questions = Question.objects.filter(Q(qtitle__icontains = search.lower()) |
				Q(qtext__contains = search.lower()) |
				Q(tag__in = tags)).distinct()
			
	print(questions)
	return render(request, "home.html", { 'questions': questions})

def viewquestion(request,qid):
	try:
		q = Question.objects.get(id=qid)
		return render(request, "question.html",{'question':q})
	except ObjectDoesNotExist:
		return redirect("/")

def votereply(request, rid, vote):
	try:
		r = Reply.objects.get(id = rid)
		if vote == 'up' and request.user not in r.uppers.all():
			r.uppers.add(request.user)
		elif vote == 'down' and request.user in r.uppers.all():
			r.uppers.remove(request.user)
	except:
		pass
	return redirect(viewquestion,r.replyto.id)

def replyquestion(request, qid):
	try:
		q = Question.objects.get(id = qid)
		r = Reply.objects.create(rtext = request.POST['rtext'], replyto = q,
								 user = request.user)
	except:
		pass
	return redirect(viewquestion,qid)

def addquestion(request):
	q = Question.objects.create(qtitle = request.POST['title'], 
								qtext = request.POST['qtext'], user=request.user)
	for t in request.POST['tags'].split(','):
		try:
			tag = Tag.objects.get(text = t)
		except ObjectDoesNotExist:
			tag = Tag.objects.create(text = t)
		q.tag.add(tag)
	return redirect("/")

