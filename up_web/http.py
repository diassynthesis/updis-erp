__author__ = 'cysnake4713'

# -*- coding: utf-8 -*-
#----------------------------------------------------------
# OpenERP Web HTTP layer
#----------------------------------------------------------

from openerp.addons.web.http import *


def monkey_dispatch(self, environ, start_response):
    """
    Performs the actual WSGI dispatching for the application, may be
    wrapped during the initialization of the object.

    Call the object directly.
    """
    request = werkzeug.wrappers.Request(environ)
    request.parameter_storage_class = werkzeug.datastructures.ImmutableDict
    request.app = self

    handler = self.find_handler(*(request.path.split('/')[1:]))

    if not handler:
        response = werkzeug.exceptions.NotFound()
    else:
        sid = request.cookies.get('sid')
        if not sid:
            sid = request.args.get('sid')

        session_gc(self.session_store)

        with session_context(request, self.session_store, self.session_lock, sid) as session:
            result = handler(request)

            if isinstance(result, basestring):
                headers = [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', len(result))]
                response = werkzeug.wrappers.Response(result, headers=headers)
            else:
                response = result

            if hasattr(response, 'set_cookie'):
                from tools import config

                response.set_cookie('sid', session.sid, domain=config.get('domain', None))

    return response(environ, start_response)


Root.dispatch = monkey_dispatch

