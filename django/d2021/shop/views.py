from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	return HttpResponse("Hello, this is a shop")

# Create your views here.
