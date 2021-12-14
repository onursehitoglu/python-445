from http.cookies import SimpleCookie
import sqlite3
import time
import uuid
import pickle

	
# session timeout
timeout = 30*60


class Session:
	'''Simple session manager'''
	def __init__(self, name, env, head, storepath= '/tmp'):
		'''name is the name for application, env is environment, head is the
		   response headers. session store is storepath/session_name.db'''
		name = ''.join(chr for chr in name if chr.isalpha())  # don't trust user, get alphanum chars
		self.name = name
		self.c = SimpleCookie()
		try:
			self.c.load(env['HTTP_COOKIE'])
		except:
			pass
		self.head = head
		self.dbpath = storepath + '/sessions_' + name + '.sqlite3'
		try:
			db = sqlite3.connect(self.dbpath)
			db.execute('select 1 from session')
		except sqlite3.OperationalError: # table does not exists
			# create table for the next time
			print('no session table. creating')
			db.execute('''create table session (
					id varchar(64), user varchar(64), timestamp int,
					vars varchar(4096))''')
			db.commit()
		r = None
		try:
			sname =  self.c['SESSID_' + self.name].value
			suser =  self.c['SESSUSER_' + self.name].value
			t = int(time.time())
			c = db.cursor()
			c.execute('select * from session where id = ? and  user = ? and timestamp > ?',
				(sname, suser, t - timeout))
			r = c.fetchone()
		except Exception as s:
			self.vars = None
		if r:
			db.close()
			db = sqlite3.connect(self.dbpath)
			db.execute('update session set timestamp = ? where id = ? and user = ?',
				( t, sname, suser))
			db.commit()
			self.vars = pickle.loads(r[3])
		else:
			self.vars = None

	def is_valid(self):
		try:
			sid = self['id']
			return True
		except:
			return False

	def create(self,user):
		sname = str(uuid.uuid1())
		self.c['SESSID_' + self.name] = sname
		self.c['SESSUSER_' + self.name] = user
		self.c['SESSID_' + self.name]['path'] = "/"
		self.c['SESSUSER_' + self.name]['path'] = "/"
		t = int(time.time())
		try:
			db = sqlite3.connect(self.dbpath)
			# timeout the old sessions
			db.execute('delete from session where timestamp < ?',
				(t - timeout,))
			# create the new session
			self.vars = {'user':user, 'id': sname, 'ts':t}
			db.execute('insert into session values (?,?,?,?)',
					( sname, user,t, pickle.dumps(self.vars)))
		except sqlite3.OperationalError: # table does not exists
			self.vars = None
		db.commit()
		# set session headers so that session cookies are set
		for k in self.c:
			self.head.append( ('Set-Cookie',self.c[k].OutputString()))

	def destroy(self):
		db = sqlite3.connect(self.dbpath)
		# timeout the old sessions
		try:
			print('delete from session where user = %s' % self['user'])
			db.execute('delete from session where user = ? or id = ?', ( self['user'],self['id']))
			db.commit()
		except:
			pass

	def __getitem__(self, i):
		return self.vars[i]

	def __setitem__(self, i,v):
		self.vars[i] = v
		t = int(time.time())
		db = sqlite3.connect(self.dbpath)
		# timeout the old sessions
		db.execute('delete from session where timestamp < ?',
				( t - timeout,))
		db.execute('update session set vars=?, timestamp=? where id = ? and user = ?',
			(pickle.dumps(self.vars), t, self.vars['id'], self.vars['user']))
		db.commit()
