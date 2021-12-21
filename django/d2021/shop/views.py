from django.shortcuts import render
from django.http import HttpResponse
from shop.models import *

def index(request):
	products = Product.objects.all()
	#return HttpResponse("Hello, this is a shop")
	return render(request, 'products.html', {'products': products})

# Create your views here.
