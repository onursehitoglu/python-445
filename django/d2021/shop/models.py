from django.db import models

class Product(models.Model):
	name = models.CharField(max_length = 100)
	price = models.FloatField(null = True)
	description = models.CharField(max_length = 1024 , null = True)
	quantity = models.IntegerField(default = 0)

class Basket(models.Model):
	user = models.CharField(max_length = 50)
	created = models.DateField(auto_now_add = True)
	updated = models.DateField(auto_now = True)
	
class Entry(models.Model):
	product = models.ForeignKey(Product, on_delete = models.CASCADE)
	count = models.IntegerField(default = 1)
	basket = models.ForeignKey(Basket, on_delete = models.CASCADE)



# Create your models here.
