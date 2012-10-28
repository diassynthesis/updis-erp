
import logging

import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi

import openerp

_logger = logging.getLogger(__name__)
class Root(object):
	"""Root app for UPDIS Internal Web Client"""
	def __call__(self, environ, start_response):
		""" Handle a WSGI request"""
		return self.dispatch(environ, start_response)
	def dispatch(self, environ, start_response):
		"""
		Performs the actual WSGI dispatching for the application, may be
		wrapped during the initialization of the object.

		Call the object directly.
		"""
		request = werkzeug.wrappers.Request(environ)
		request.parameter_storage_class = werkzeug.datastructures.ImmutableDict
		request.app = self
		headers=[('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', len(result))]
		response = werkzeug.wrappers.Response("result!", headers=headers)
		return response
def wsgi_postload():
	_logger.info("Loaded my WSGI APP!")
	openerp.wsgi.register_wsgi_handler(Root())