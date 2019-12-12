'''For extending template language with a filter
   templates use {% load poll_extra %} to load this'''

from django import template
register = template.Library()

@register.filter
def lookup(value,arg):
	''' lookup a variable dictionary key from template
	    workarround for: 
		{% for k in dict %}
                     {{dict.k}}
	        ... will lookup for dict['k']
			 instead of the content of 'k'
	    Usage example:
		{% for k in dict %}
	    	   {{ dict|lookup:k }}
		...
	'''
	try:
		return value[arg]
	except:
		return ""
