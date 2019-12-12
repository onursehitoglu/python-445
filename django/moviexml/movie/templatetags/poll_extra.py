from django import template
register = template.Library()

@register.filter
def lookup(value,arg):
	try:
		return value[arg]
	except:
		try:
			t = getattr(value,arg)
			if hasattr(t,'__call__'):
				return t.__call__()
			else:
				return t
		except:
			return ""
