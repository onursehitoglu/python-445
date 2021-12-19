#!/usr/bin/python

from multiprocessing import Process,Array,Lock
import socket
import sys
import time

class Agent(Process):
	def __init__(self, i, sock, alock,state):
		self.ind = i
		self.sock = sock
		self.lock = alock
		self.state = state
		Process.__init__(self)
	def run(self):
		while True:
			self.state[self.ind] = b'.'
			self.lock.acquire()
			self.state[self.ind] = b'W'
			(ns,addr) = self.sock.accept()
			self.lock.release()
			print('accepted connection from',addr)
			self.state[self.ind] = b'A'
			self.connection(ns)

	def connection(self,conn):
		inp = conn.recv(1024)
		while inp:
			out = inp.upper()
			conn.send(out)
			inp = conn.recv(1024)
		print('client is terminating')

if len(sys.argv) != 3:
	print('usage: ',sys.argv[0],'port','poolsize')
	sys.exit(-1)


HOST = ''         
PORT = int(sys.argv[1] )
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

n = int(sys.argv[2])
states = Array('c',n)
acclock = Lock()

pool = [ Agent(i, s, acclock,states) for i in range(n) ] 

for p in pool:
	p.start()

try:
	while True:
		print("process states:",end='')
		for i in states:
			print(i.decode(),end='')
		print()
		time.sleep(1)
except KeyboardInterrupt:
	for p in pool:
		p.terminate()



