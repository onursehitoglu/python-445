#!/usr/bin/python3

import sys
import os
from socket import *
import asyncio
import websockets
import logging
import json
import http.cookies
from threading import Thread


## Uncomment following to use session_keys from django.
## This way request authentication will be
## achieved. similarly CSRF token can be used for
## authentication as well.

#import django
#from django.contrib.session.models import Session
#
#def setupDjango(projectpath, projectname):
#	'''call this once to setup django environment'''
#	sys.path.append(projectpath)
#	os.environ.setdefault('DJANGO_SETTINGS_MODULE',projectname + '.settings')
#	django.setup()
#
#def checksession(sessionkey):
#	'''check UDP/WS supplied id againts django session keys
#	   for browser, 'sessionid' cookie will save this id
#	   for django view request.session.session_key gives this id.
#		simply view sends udp notifications with request.session.session_key and
#		browser sends sessionid cookie. Note that they don't need to match.
#		User A can send notification to user B. But both have session ids.
#	'''
#	try:
#		Session.objects.get(session_key=sessionkey)
#		return True
#	except:	
#		return False
def singleton(cls):
        '''generic python decorator to make any class
        singleton.'''
        _instances = {}   # keep classname vs. instance
        def getinstance():
                '''if cls is not in _instances create it
                and store. return the stored instance'''
                if cls not in _instances:
                        _instances[cls] = cls()
                return _instances[cls]
        return getinstance



@singleton
class Notifications:
	'''An observer class, saving notifications and notifiying
		registered coroutines'''
	def __init__(self):
		self.observers = {}
		self.broadcast = set()
		self.messages = {}

	def register(self, ws, cid):
		'''register a Lock and an id string'''
		if cid in self.observers:
			self.observers[cid].add(ws)
		else:
			self.observers[cid] = set([ws])
		self.broadcast.add(ws)
		print(self.observers)

	def unregister(self, ws, cid):
		'''remove registration'''
		if cid not in self.observers:
			return
		self.observers[cid].discard(ws)
		self.broadcast.discard(ws)
		if self.observers[cid] == set():
			del self.observers[cid]
		print(self.observers)

	async def addNotification(self, oid, message):
		'''add a notification for websocket conns with id == oid
			the '*' oid is broadcast. Message is the dictionary
			to be sent to connected websockets.
		'''
		if oid == '*':     # broadcast message
			for c in self.broadcast:
				await c.send(json.dumps(message))
		elif oid in self.observers:
			for c in self.observers[oid]:
				await c.send(json.dumps(message))


class GetNotifications:
	''' Class for getting notifications as udp packets'''
	def connection_made(self, transport):
		self.transport = transport
		print("Starting UDP server")

	async def datagram_received(self, data, addr):
		try:
			mess = json.loads(data.decode())
		except:
			print('Cannot parse {}\n'.format(data.decode()))
			self.transport.sendto(b'cannot parse', addr)
			return
		await Notfications().addNotification(mess['id'], mess)
		print('Received %r from %s' % (mess, addr))

		
async def websockethandler(websocket, path):
	
	# websocket.request_headers is a dictionary like object
	print (websocket.request_headers.items())
	# following parses the cookie object
	if 'Cookie' in websocket.request_headers:
		print(http.cookies.SimpleCookie(websocket.request_headers['Cookie']))

	# get the list of ids to follow from browser
	reqlist = await websocket.recv()
	idlist = json.loads(reqlist)
	
	print('connected', idlist)

	if type(idlist) != list:
		idlist = [idlist]
	for myid in idlist:
		Notifications().register(websocket, myid)

	print(Notifications().observers)

	try:
		while True:
			data = await websocket.recv()
			try:
				message = json.loads(data)
				await Notifications().addNotification(message['id'], message) 
			except Exception as e:
				print("invalid message. {} : exception: {}".format(data, str(e)))
	except Exception as e:
		print(e)
	finally:
		print('closing', idlist)
		for myid in idlist:
			Notifications().unregister(websocket, myid)
		websocket.close()


#enable logging
logging.basicConfig(level=logging.DEBUG)

try:
	ws_addr = sys.argv[1].split(':',1)
	if ws_addr[0] == '' : ws_addr[0] = '0'
	ws_addr = getaddrinfo(ws_addr[0], ws_addr[1], AF_INET, SOCK_STREAM)
	ws_addr = ws_addr[0][4]
except Exception as e:
	sys.stderr.write("{}\nusage: {} wsip:port\n".format(e, sys.argv[0]))
	sys.exit()



## Following creates a UDP handler
#udplistener = loop.create_datagram_endpoint(
#    	GetNotifications, local_addr=udp_addr )
# following creates a websocket handler
loop = asyncio.get_event_loop()
loop.set_debug(True)
ws_server = websockets.serve(websockethandler, ws_addr[0], ws_addr[1], loop = loop)

#loop.run_until_complete(ws_server)
# start both in an infinite service loop
#asyncio.async(ws_server)
#asyncio.ensure_future(ws_server)
loop.run_until_complete(ws_server)
loop.run_forever()
