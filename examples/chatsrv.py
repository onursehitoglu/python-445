#!/usr/bin/python
from websockets.sync import server
from websockets.exceptions	import ConnectionClosedError,ConnectionClosedOK

from threading import Thread,Lock,Condition
import socket
import json
import sys

class Chat:
	def __init__(self):
		self.buf = []
		self.lock = Lock()
		self.newmess = Condition(self.lock)
	def newmessage(self,mess):
		self.lock.acquire()
		self.buf.append(mess)
		self.newmess.notify_all()
		self.lock.release()
	def getmessages(self,after=0):
		self.lock.acquire()
		if len(self.buf) < after:
			a = []
		else:
			a = self.buf[after:]
		self.lock.release()
		return a
		
class NotifierAgent(Thread):
	def __init__(self, sock, chat):
		self.sock = sock
		self.chat = chat
		self.current = 0
		self.notexit = True
		Thread.__init__(self)
	def run(self):
		oldmess = self.chat.getmessages()
		self.current += len(oldmess)
		self.sock.send(json.dumps(oldmess))
		while self.notexit:
			self.chat.lock.acquire()
			self.chat.newmess.wait()
			self.chat.lock.release()
			oldmess = self.chat.getmessages(self.current)
			if len(oldmess) == 0:
				continue
			self.current += len(oldmess)
			try:
			  self.sock.send(json.dumps(oldmess))
			except:
			  self.notexit = False
	def terminate():
		self.notexit = False
		self.chat.lock.acquire()
		self.newmess.notify_all()
		self.chat.lock.release()
			

if len(sys.argv) != 2:
	print('usage: ',sys.argv[0],'port')
	sys.exit(-1)


HOST = ''         
PORT = int(sys.argv[1] )
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((HOST, PORT))
#s.listen(1)

chatroom = Chat()

def Agent(sock):
	global chatroom

	rdr = NotifierAgent(sock,chatroom)
	rdr.start() 
	
	try:
		while True:
			inp = sock.recv()
			mess = json.loads(inp)
			print(mess)
			if 'message' in mess: chatroom.newmessage(mess['message'])
	except ConnectionClosedOK:
		print('client is terminating')
	except ConnectionClosedOK:
		print('client generated error')

	sock.close()
	rdr.terminate()


srv =  server.serve(Agent, host=HOST, port=PORT) 
print(dir(srv))
srv.serve_forever()
#while True:
#	conn, addr = s.accept()
#
#	print('Connected by', addr)
#	a = RDAgent(conn,addr,chatroom)
#	b = WRAgent(conn,addr,chatroom)
#	a.start()
#	b.start()


