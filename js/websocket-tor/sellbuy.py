#!/usr/bin/env python3
#
"""Derived from tornado websocket chat demo
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options

define("port", default=8800, help="run on the given port", type=int)


class Application(tornado.web.Application):
	def __init__(self):
		# set handlers based on the URI path
		handlers = [(r"/", MainHandler), (r"/chatsocket", ChatSocketHandler)]
		settings = dict(
			cookie_secret="db0b04103c079c743f2d6562bb5315c",
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			xsrf_cookies=True,
		)
		super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
	'''handler for regular http requests (for getting index.html)'''
	def get(self):
		# no authentication in system. Just assign a random username per browser connection
		user = str(uuid.uuid4())[:8]
		ChatSocketHandler.users[user] = { 'balance' : 100}
		self.render("index.html", username = user, entries=ChatSocketHandler.entries)


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
	'''handler for websocket events'''
	waiters = set()
	entries = {}
	users = {}



	def get_compression_options(self):
		# Non-None enables compression with default options.
		return {}

	def open(self):
		ChatSocketHandler.waiters.add(self)

	def on_close(self):
		ChatSocketHandler.waiters.remove(self)

	def check_origin(self, orig):
		return True

	@classmethod
	def handle_message(cls, operation, mop):
		'''handle operation message coming from websocket.
           fills in mop for the model changes that is necessary'''
		try:
			eid = operation['id'] if 'id' in operation else None
			op = operation['op']
			ouser = operation['user']
			euser = cls.entries[eid]['user'] if eid in cls.entries else None
			# DELETE item
			if op == 'delete' and ouser == euser:
				mop['message'] = "entry {} is removed by the owner".format(cls.entries[eid]['name'])
				mop['change'] = {'op':'del', 'id': eid}
				del cls.entries[eid]
			# INCREMENT item (a new bidder)
			elif op == 'increment':
				cls.entries[eid]['price'] = int(cls.entries[eid]['price'])+1
				cls.entries[eid]['bidder'] = operation['user']
				mop['message'] = "entry {} price is changed".format(cls.entries[eid]['name'])
				mop['change'] = {'op':'upd', 'entry': cls.entries[eid]}
			# NEW item to sale
			elif op == 'new':
				eid = 'E' + str(uuid.uuid4())
				entry = {'id': eid}
				for k in ('name','price', 'user'):
					entry[k] = operation[k]
				entry['price'] = str(int(entry['price']))  # check if it is a number
				cls.entries[eid] = entry
				mop['message'] = "a new item {} is on sale".format(cls.entries[eid]['name'])
				mop['change'] = {'op':'add', 'entry': entry}
			# owner SELLs item to last bidder
			elif op == 'sell':
				if ouser == euser and 'bidder' in cls.entries[eid]:
					buyer = cls.entries[eid]['bidder']
					cls.users[ouser]['balance'] -= cls.entries[eid]['price']
					cls.users[ouser]['balance'] += cls.entries[eid]['price']
					mop['message'] = "entry {} is sold to {}".format(cls.entries[eid]['name'], buyer)
					mop['change'] = {'op':'del', 'id': eid}
					del cls.entries[eid]
				else:
					mop['message'] = "invalid sell request for entry {} taken from {}!".format(cls.entries[eid], ouser)
		except Exception as e:
			if type(e) == ValueError:
				mess = 'invalid price in request {}'
			elif type(e) == KeyError:
				mess = 'invalid or incomplete request {}'
			else:
				mess = 'invalid operation or unknown error {}'

			mop['message'] = mess.format(op)
			logging.error("invalid request object: {} ".format(operation), exc_info=True)

	@classmethod
	def send_updates(cls, modelop):
		'''send model update information to all connections'''
		logging.info("sending message to %d waiters", len(cls.waiters))
		for waiter in cls.waiters: # for all websocket connections
			try:
				waiter.write_message(modelop)
			except:
				logging.error("Error sending message", exc_info=True)

	def on_message(self, message):
		'''when a new message (operation) is received from browser'''
		logging.info("got message %r", message)
		operation = tornado.escape.json_decode(message)
		modelop = {message: ""}
		ChatSocketHandler.handle_message(operation, modelop)
		if 'change' in modelop:
			ChatSocketHandler.send_updates(modelop)
		elif 'message' in modelop:
			self.write_message({'error':modelop['message']})


def main():
	tornado.options.parse_command_line()
	app = Application()
	app.listen(options.port)
	tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
	main()
