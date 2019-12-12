# Package: forms.py
# Defines forms used in the application

from django import forms

# Class: MovieForm
# HTML form of user is generated and input from this
class MovieForm(forms.Form):
    '''Form used for add and update of Movies'''
    title = forms.CharField(max_length=200)
    imdb = forms.CharField(max_length=20)
    director = forms.CharField(max_length=100)
    cast = forms.CharField(max_length=100)

