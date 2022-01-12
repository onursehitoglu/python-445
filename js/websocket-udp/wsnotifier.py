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

class Notifications:
	'''An observer class, saving notifications and notifiying
		registered coroutines'''
	def __init__(self):
		self.observers = {}
		self.broadcast = set()
		self.messages = {}

	def connect(self,cond):
		self.broadcast.add(cond)

	def disconnect(self,cond):
		self.broadcast.discard(cond)

	def register(self, cond, cid):
		'''register a Lock and an id string'''
		if cid in self.observers:
			self.observers[cid].add(cond)
		else:
			self.observers[cid] = set([cond])
		print(self.observers)

	def unregister(self, cond, cid):
		'''remove registration'''
		if cid not in self.observers:
			return
		self.observers[cid].discard(cond)
		self.broadcast.discard(cond)
		if self.observers[cid] == set():
			del self.observers[cid]
		print(self.observers)

	def addNotification(self, oid, message):
		'''add a notification for websocket conns with id == oid
			the '*' oid is broadcast. Message is the dictionary
			to be sent to connected websockets.
		'''
		if oid == '*':     # broadcast message
			distribution = self.broadcast
		elif oid in self.observers:
			distribution = self.observers[oid]
		else:
			print("no observers")
			return

		mt = [len(distribution), message]
		if oid in self.messages:
			self.messages[oid].append(mt)
		else:
			self.messages[oid] = [mt]

		print('addnotification',self.messages)
		# tell observers that there is a new message
		for c in distribution:
			try:
				c.release()
			except:
				pass


	def newmessages(self, oidlist):
		'''returns a list of messages for the connection with id==oid'''
		ret = []
		for oid in oidlist + ['*']:
			if oid not in self.messages:
				continue
			for mt in self.messages[oid]:
				ret.append(mt[1])
				mt[0] -= 1
				if mt[0] == 0:
					self.messages[oid].remove(mt)
					if self.messages[oid] == []:
						del self.messages[oid]
	
		print("tosend:", ret, self.messages)
		return json.dumps(ret)
	
# initialize a global notifications object
notifications = Notifications()

class GetNotifications:
	''' Class for getting notifications as udp packets'''
	def connection_made(self, transport):
		self.transport = transport
		print("Starting UDP server")

	def datagram_received(self, data, addr):
		try:
			mess = json.loads(data.decode())
		except:
			print('Cannot parse {}\n'.format(data.decode()))
			self.transport.sendto(b'cannot parse', addr)
			return
		notifications.addNotification(mess['id'], mess)
		print('Received %r from %s' % (mess, addr))

		
async def websockethandler(websocket, path):
	''' function sending notifications to browsers
        it expects browser to send an identification string
		later all notifications for this id will be sent to
		the browser'''
	
	# websocket.request_headers is a dictionary like object
	print (websocket.request_headers.items())
	# following parses the cookie object
	if 'Cookie' in websocket.request_headers:
		print(http.cookies.SimpleCookie(websocket.request_headers['Cookie']))

	# get the list of ids to follow from browser
	reqlist = await websocket.recv()
	idlist = json.loads(reqlist)
	
	print('connected', idlist)

	# create my lock to be notified
	mycond = asyncio.Lock()
	if type(idlist) != list:
		idlist = [idlist]
	for myid in idlist:
		notifications.register(mycond, myid)
	notifications.connect(mycond)

	print(notifications.observers)

	try:
		while True:
			# wait on lock. UDP notifier will release me to enter
			await mycond.acquire()
			await websocket.send(notifications.newmessages(idlist))

	except Exception as e:
		print(e)
	finally:
		print('closing', idlist,notifications.newmessages(idlist))
		for myid in idlist:
			notifications.unregister(mycond, myid)
		notifications.disconnect(mycond)
		await websocket.close()


#enable logging
logging.basicConfig(level=logging.DEBUG)

try:
	# normalize user supplied addresses and validate
	udp_addr = sys.argv[1].split(':',1)
	if udp_addr[0] == '' : udp_addr[0] = '0'
	udp_addr = getaddrinfo(udp_addr[0], udp_addr[1], AF_INET, SOCK_DGRAM)
	udp_addr = udp_addr[0][4]

	ws_addr = sys.argv[2].split(':',1)
	if ws_addr[0] == '' : ws_addr[0] = '0'
	ws_addr = getaddrinfo(ws_addr[0], ws_addr[1], AF_INET, SOCK_STREAM)
	ws_addr = ws_addr[0][4]
except Exception as e:
	sys.stderr.write("{}\nusage: {} udpip:port wsip:port\n".format(e, sys.argv[0]))
	sys.exit()



## Following creates a UDP handler
loop = asyncio.get_event_loop()
loop.set_debug(True)
udplistener = loop.create_datagram_endpoint(
    	GetNotifications, local_addr=udp_addr )
# following creates a websocket handler
ws_server = websockets.serve(websockethandler, ws_addr[0], ws_addr[1], loop = loop)

#loop.run_until_complete(ws_server)
# start both in an infinite service loop
asyncio.ensure_future(ws_server)
loop.run_until_complete(udplistener)
loop.run_forever()

