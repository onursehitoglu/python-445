#!/usr/bin/python

from threading import Thread,Lock,Condition
import socket
import sys

class Chat:
	def __init__(self):
		self.buf = []
		self.lock = Lock()
		self.newmess = Condition(self.lock)
	def newmessage(self,mess):
		self.lock.acquire()
		self.buf.append(mess)
		self.newmess.notifyAll()
		self.lock.release()
	def getmessages(self,after=0):
		self.lock.acquire()
		if len(self.buf) < after:
			a = []
		else:
			a = self.buf[after:]
		self.lock.release()
		return a
		
		
	

class RDAgent(Thread):
	def __init__(self, conn, addr, chat):
		self.conn = conn
		self.claddr = addr
		self.chat = chat
		Thread.__init__(self)
	def run(self):
		inp = self.conn.recv(1024)
		while inp:
			self.chat.newmessage(inp)
			print('waiting next',self.claddr)
			inp = self.conn.recv(1024)
		print('client is terminating')
		conn.close()

class WRAgent(Thread):
	def __init__(self, conn, addr, chat):
		self.conn = conn
		self.claddr = addr
		self.chat = chat
		self.current = 0
		Thread.__init__(self)
	def run(self):
		oldmess = self.chat.getmessages()
		self.current += len(oldmess)
		self.conn.send('\n'.join([i.decode() for i in oldmess]).encode())
		notexit = True
		while notexit:
			self.chat.lock.acquire()
			self.chat.newmess.wait()
			self.chat.lock.release()
			oldmess = self.chat.getmessages(self.current)
			self.current += len(oldmess)
			try:
			  self.conn.send('\n'.join([i.decode() for i in oldmess]).encode())
			except:
			  notexit = False
			

if len(sys.argv) != 2:
	print('usage: ',sys.argv[0],'port')
	sys.exit(-1)


HOST = ''         
PORT = int(sys.argv[1] )
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

chatroom = Chat()


while True:
	conn, addr = s.accept()

	print('Connected by', addr)
	a = RDAgent(conn,addr,chatroom)
	b = WRAgent(conn,addr,chatroom)
	a.start()
	b.start()


