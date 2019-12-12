from django import forms
import re

# Class: NamesField
# class for validation of CharFields containing only names
class NamesField(forms.CharField):
	def __init__(self,*k,**kw):
		forms.CharField.__init__(self,*k,**kw)
	# Function: clean(self,value)
	# test if name contains only alphanumeric chars , ',' and '.'
	def clean(self,value):
		if re.match("^[ \w,'.]+$", value):
			return value
		else:
			raise forms.ValidationError(_('Invalid char in name'), code='invalid')
	
# Class: MovieForm
# A form class for movie forms
class MovieForm(forms.Form):
	# Variable: title
	title = forms.CharField(max_length=200)
	# Variable: imdb
	imdb = forms.CharField(max_length=20)
	# Variable: director
	# <NamesField> 
	director = NamesField(max_length=100)
	# Variable: cast
	# <NamesField>
	cast = NamesField(max_length=100)

