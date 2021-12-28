from django import forms

class Product(forms.Form):
	name = forms.CharField(label='Product Name', max_length=100, required = True)
	price = forms.DecimalField(label = "Product Price", min_value = 0, decimal_places = 2, required = True)
	description = forms.CharField(label = "Description", max_length = 1024 , widget = forms.Textarea, required = False)
	image = forms.ImageField(label = "Product image", required = False)
	quantity = forms.IntegerField(label = "Stock quantity",min_value = 0)

