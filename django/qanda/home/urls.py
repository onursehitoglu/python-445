"""qanda home URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
"""
from django.conf.urls import url, include
from django.contrib import admin
from home import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^asknew', views.addquestion),
    url(r'^view/(?P<qid>[0-9]+)', views.viewquestion),
    url(r'^reply/(?P<qid>[0-9]+)', views.replyquestion),
    url(r'^setvote/(?P<rid>[0-9]+)/(?P<vote>up|down)', views.votereply),
    url(r'^tag/(?P<tagname>.+)', views.home),
    url(r'^search/(?P<search>.+)', views.home),
]
