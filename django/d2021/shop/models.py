from django.db import models

class Product(models.Model):
	name = models.CharField(max_length = 100)
	price = models.FloatField(null = True)
	description = models.CharField(max_length = 1024 , null = True)
	quantity = models.IntegerField(default = 0)
	def __str__(self):
		return self.name

class Basket(models.Model):
	user = models.CharField(max_length = 50)
	created = models.DateField(auto_now_add = True)
	updated = models.DateField(auto_now = True)
	def __str__(self):
		return self.user
	
class Entry(models.Model):
	product = models.ForeignKey(Product, on_delete = models.CASCADE)
	count = models.IntegerField(default = 1)
	basket = models.ForeignKey(Basket, on_delete = models.CASCADE)
	def __str__(self):
		return str(self.basket)+str(self.product)+str(self.count)



# Create your models here.
