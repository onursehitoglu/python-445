#!/usr/bin/python

from threading import *
from time import *
from random import *
STARTED = 0
THINKING = 1
HUNGRY = 2
EATING = 3
EXITTED = 4

stmess = "0?-*X"


class Philosopher(Thread):
	def __init__(self,id,forks,states):
		Thread.__init__(self)
		self.id = id
		self.left = forks[0]
		self.right = forks[1]
		self.states = states
		self.states[id] = STARTED
		self.term = False
	def terminate(self):
		self.term = True
	def run(self):
		for i in range(10):
			if self.term:
				break
			self.states[self.id] = THINKING
			sleep(random()*1)
			self.states[self.id] = HUNGRY
			if self.id % 2 == 0:
				self.left.acquire()
				self.right.acquire()
			else:
				self.right.acquire()
				self.left.acquire()
			self.states[self.id] = EATING
			sleep(random()*4)
			self.left.release()
			self.right.release()
		self.states[self.id] = EXITTED

print("Enter number of philosopher: ",end='')
n = int(input())

forks = [Lock() for i in range(n)]

phils = []

states = n * [0]

for i in range(n):
	phils.append( Philosopher(i,(forks[i],forks[(i+1)%n]),states) )


for phil in phils:
	phil.start() 

while True:
	eflag = True
	for i in range(n):
		if states[i] != EXITTED:
			eflag = False
		print(stmess[states[i]], end='')
	print()
	if eflag:
		break
	try:
		sleep(1)
	except KeyboardInterrupt:
		for phil in phils:
			phil.terminate()

for phil in phils:
	phil.join() 






