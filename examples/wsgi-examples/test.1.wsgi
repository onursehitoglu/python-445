#!/usr/bin/python3
import os
os.environ.clear()

from urllib.parse import parse_qs
from html import escape
from http.cookies import SimpleCookie
from wsgiref.simple_server import make_server

	

def application(environ, start_response):
	''' State transfer with form element. counter value is
	    incremented and posted at each step'''
	body = '''<html><body>
		  <h1> Hello </h1>
		  {}
		  <form action="/" method="post">
			Name <input type="text" name="name"/>
			Surname <input type="text" name="sname"/>
			<!-- hidden variable here -->
			<input type="hidden" name="counter" value="{}"/>

			<input type="submit" name="submit" value="Send"/>
		 </form>'''


	if environ['REQUEST_METHOD'] == 'GET':
		qstr = environ['QUERY_STRING']
	elif environ['REQUEST_METHOD'] == 'POST':
		try:
			qlen = int(environ['CONTENT_LENGTH'])
		except:
			qlen = 0
		qstr = environ['wsgi.input'].read(qlen).decode()
	else:
		qstr = ''

	query = parse_qs(qstr)

	# implement state transfer with form. assume state is a counter
	try:
		counter = int(query['counter'][0])
	except:
		counter = 0

	counter += 1

	try:
		response_body = body.format(escape(query['name'][0] + ', ' + query['sname'][0]), counter)
	except:
		response_body = body.format('',counter)


	status = '200 OK'
	response_headers = [('Content-Type','text/html')]
	start_response(status, response_headers)
	yield response_body.encode()
	
	yield '<p><strong>Counter:</strong> {}</p>'.format(counter).encode()

	for i in environ:
		yield "<strong>{}:</strong> {}<br/>\n".format(i,environ[i]).encode()
	yield b"</body></html>"


if __name__ == '__main__':
	httpd = make_server('localhost', 9090, application)
	httpd.serve_forever()()
