#!/usr/bin/python3
import os
os.environ.clear()

from wsgiref.simple_server import make_server

from urllib.parse import parse_qs
from html import escape
from http.cookies import SimpleCookie
import datetime
	

def application(environ, start_response):
	''' State transfer through cookies '''
	body = '''<html><body>
		  <h1> Hello </h1>
		  {}
		  <form action="/" method="post">
			Name <input type="text" name="name"/>
			Surname <input type="text" name="sname"/>
			<input type="submit" name="submit" value="Send"/>
		 </form>'''

	# implement state transfer with cookies load cookie
	cookie = SimpleCookie()
	try:
		cookie.load(environ['HTTP_COOKIE'])
		counter = int(cookie['counter'].value)
		counter += 1
		cookie['counter'] = str(counter)
	except:
		# first time use, initialize to 0
		counter = 0
		cookie['counter'] = '0'


	cookie['counter']['path'] = '/'
	cookie['counter']['expires'] = (datetime.datetime.now() +  # add 15 days to now()
			datetime.timedelta(days=3)).strftime("%a, %d %b %Y %H:%M:%S")
	# expires 3 days after we set the cookie for the last time
	response_headers=[('Content-Type','text/html')]
	response_headers.append(('Set-Cookie',cookie['counter'].OutputString()))

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


	try:
		response_body = body.format(query['name'][0] + ', ' + query['sname'][0])
	except:
		response_body = body.format('')

	status = '200 OK'

	start_response(status, response_headers)

	yield response_body.encode()

	yield '<p><strong>Counter:</strong> {}</p>'.format(counter).encode()
 
	for i in environ:
		yield "<strong>{}:</strong> {}<br/>\n".format(i,environ[i]).encode()

	yield b"</body></html>"



if __name__ == '__main__':
	httpd = make_server('localhost', 9090, application)
	httpd.serve_forever()()
