from django.shortcuts import render
from django.http import HttpResponse
from shop.models import *
from django.contrib.auth.decorators import login_required

@login_required
def basket(request):
    try:
        basket = Basket.objects.get(user = request.user)
    except:
        basket = Basket(user = request.user)

    entries = list( basket.entry_set.values())
    sum = 0.0
    for e in entries:
        e['name'] = Product.objects.get(id = e['product_id']).name
        e['price'] = Product.objects.get(id = e['product_id']).price
        e['amount'] = e['price'] * e['count']
        sum += e['amount']

    return render(request, 'basket.html', {'basket': entries, 'total': sum, 'user': basket.user})

def index(request):
	products = Product.objects.all()
	#return HttpResponse("Hello, this is a shop")
	return render(request, 'products.html', {'products': products})

# Create your views here.
