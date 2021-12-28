from django.shortcuts import render,redirect
from django.http import HttpResponse
from shop.models import *
from shop.forms import Product as ProductForm
from django.contrib.auth.decorators import login_required

@login_required
def prodpost(request):
	p = request.POST
	if 'insert' in request.POST:
		product = Product.objects.create(name = p['name'],
			description = p['description'],
			price = p['price'],
			quantity = p['quantity'])
		return redirect("/")
	elif 'update' in request.POST:
		product = Product.objects.filter(id = p['pid']).update(name = p['name'],
			description = p['description'],
			price = p['price'],
			quantity = p['quantity'])
		return redirect("/")
	elif 'delete' in request.POST:
		product = Product.objects.filter(id = p['pid']).delete()
		return redirect("/")
	else:
		return redirect("/", message = "Product not found")

@login_required
def add(request, pid):
	try:
		basket = Basket.objects.get(user = request.user)
	except:
		basket = Basket.objects.create(user = request.user)

	try:
		product = Product(id = pid)
	except:
		return redirect("/",message = "Product not found")

	try:
		entry = basket.entry_set.get(product = product)
		entry.count += 1
		entry.save()
	except:
		try:
			entry = Entry(product = product, count = 1, basket = basket)
			entry.save()
			basket.entry_set.add(entry)
		except:
			return redirect('/', message = 'No such product')

	return redirect('/basket')
	

def product(request, pid = None):
	if request.user and request.user.is_staff:
		# show an update screen if product is given, otherwise insert
		try:
			product = Product.objects.get(id = pid)
			prform = ProductForm({'name': product.name,
				'price': product.price,
				'description' : product.description,
				'quantity' : product.quantity})
			operation = 'update'
		except:
			#insert case
			prform = ProductForm()
			operation = 'insert'
		return render(request, 'productupd.html', {'pid': pid, 'form': prform, 'operation': operation})
	else:
		try:
			product = Product.objects.get(id = pid)
			return render(request, 'productview.html', {'product': product})
		except:
			return render(request, 'productview.html', {'product': None})


@login_required
def basket(request):
    try:
        basket = Basket.objects.get(user = request.user)
    except:
        basket = Basket(user = request.user)
        basket.save()

    entries = list( basket.entry_set.values())
    sum = 0.0
    for e in entries:
        e['name'] = Product.objects.get(id = e['product_id']).name
        e['price'] = Product.objects.get(id = e['product_id']).price
        e['amount'] = e['price'] * e['count']
        sum += e['amount']

    return render(request, 'basket.html', {'basket': entries, 'total': sum, 'user': basket.user})

def index(request, message = ''):
	products = Product.objects.all()
	#return HttpResponse("Hello, this is a shop")
	return render(request, 'products.html', {'message': message, 'products': products})

# Create your views here.
