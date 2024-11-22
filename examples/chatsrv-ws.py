#!/usr/bin/python
from websockets.sync import server
from websockets.exceptions	import ConnectionClosedError,ConnectionClosedOK

from threading import Thread,RLock,Condition
import socket
import json
import sys

class Monitor:
	'''A generic monitor class, derive from this class and
	   call super().__init__()
	   then decorate sync methods with Monitor.sync '''
	def __init__(self):
		self.mlock = RLock()
	@classmethod
	def sync(self, method):
		def w(self, *p, **kw):
			with self.mlock:
				return method(self,*p, **kw)
		return w

	def CV(self):
		'''Create condition variables with this method to get
		   them share the monitor lock'''
		return Condition(self.mlock)

class Chat(Monitor):
	def __init__(self):
		super().__init__()
		self.buf = []
		self.newmess = self.CV()

	@Monitor.sync
	def newmessage(self,mess):
		self.buf.append(mess)
		self.newmess.notify_all()

	@Monitor.sync
	def getmessages(self,after=0):
		if len(self.buf) < after:
			a = []
		else:
			a = self.buf[after:]
		return a

	@Monitor.sync
	def wait(self):
		self.newmess.wait()

class NotifierAgent(Thread):
	def __init__(self, sock,chat):
		self.sock = sock
		self.peer = self.sock.remote_address
		self.chat = chat
		self.current = 0
		self.notexit = True
		Thread.__init__(self)
	def run(self):
		oldmess = self.chat.getmessages()
		self.current += len(oldmess)
		self.sock.send(json.dumps(oldmess))
		while self.notexit:
			self.chat.wait()
			oldmess = self.chat.getmessages(self.current)
			if len(oldmess) == 0:
				continue
			self.current += len(oldmess)
			try:
			  self.sock.send(json.dumps(oldmess))
			except:
			  self.notexit = False
	def terminate(self):
		self.notexit = False
		with self.chat.newmess:
			self.chat.newmess.notify_all()
			

if len(sys.argv) != 2:
	print('usage: ',sys.argv[0],'port')
	sys.exit(-1)


HOST = ''		 
PORT = int(sys.argv[1] )
chatroom = Chat()

def Agent(sock):
	global chatroom

	peer = sock.remote_address
	rdr = NotifierAgent(sock, chatroom)
	rdr.start() 
	
	try:
		while True:
			inp = sock.recv()
			print(inp)
			mess = json.loads(inp)
			print(mess)
			if 'message' in mess: 
				chatroom.newmessage( {'sender':peer,
						              'message': mess['message']})
	except ConnectionClosedOK:
		print('client is terminating')
	except ConnectionClosedOK:
		print('client generated error')

	sock.close()
	rdr.terminate()


srv =  server.serve(Agent, host=HOST, port=PORT) 
#print(dir(srv))
srv.serve_forever()

