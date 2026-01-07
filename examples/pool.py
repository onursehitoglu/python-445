from multiprocessing import Pool, Queue, Process

class Pool:
	class Slave(Process):
		def __init__(self, qin, qout):
			self.qin = qin
			self.qout = qout
			super().__init__()
		def run(self):
			while True:
				(val, vid, func) = self.qin.get()
				res = func(val)
				self.qout.put( (res, vid) )
			
	def __init__(self, number):
		self.qout = Queue()
		self.qin = Queue()
		self.slaves = [Pool.Slave(self.qout, self.qin) for i in range(number)]
		for s in self.slaves:
			s.start()

	def map(self, func, elems):
		n = 0
		for e in elems:
			self.qout.put( (e, n, func) )
			n += 1
		results = [None] * n
		for i in range(n):
			(res, vid) = self.qin.get()
			print (i, res, vid)
			results[vid] = res
		return results

	def terminate(self):
		for p in self.slaves:
			p.terminate()


