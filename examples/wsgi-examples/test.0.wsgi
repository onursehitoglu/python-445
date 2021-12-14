#!/usr/bin/python3
import os
os.environ.clear()
from urllib.parse import parse_qs
from html import escape
from http.cookies import SimpleCookie
from wsgiref.simple_server import make_server
	

def application(environ, start_response):
	''' Simple post and show application '''

	body = '''<html><body>
		  <h1> Hello </h1>
		  {}
		  <form action="/" method="post">
			Name <input type="text" name="name"/>
			Surname <input type="text" name="sname"/>
			<input type="submit" name="submit" value="Send"/>
		 </form>'''

	# body.format("message") will return html with message after Hello

	if environ['REQUEST_METHOD'] == 'GET':
		qstr = environ['QUERY_STRING']
	elif environ['REQUEST_METHOD'] == 'POST':
		try:
			qlen = int(environ['CONTENT_LENGTH'])
		except:
			qlen = 0
		qstr = environ['wsgi.input'].read(qlen)
	else:
		qstr = ''

	query = parse_qs(qstr)
	# query is a dictionary of form data

	try:
		response_body = body.format(query['name'][0] + ', ' + query['sname'][0])
	except:
		response_body = body.format('')

	status = '200 OK'
	response_headers = [('Content-Type','text/html')]

	start_response(status, response_headers)

	yield response_body.encode()
	for i in environ:
		 yield "<strong>{}:</strong> {}<br/>\n".format(i,environ[i]).encode()
	yield b"</body></html>"

if __name__ == '__main__':
	httpd = make_server('localhost', 9090, application)
	httpd.serve_forever()()
