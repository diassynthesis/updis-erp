from HTMLParser import HTMLParser
import getpass
import contextlib
import os
import re
import tempfile
import threading
from dateutil.parser import parse
from flask import Flask, Blueprint, request_started, Request, request
from werkzeug.contrib.sessions import FilesystemSessionStore
from openerp.service.messages.messages import blueprint_messages

__author__ = 'Zhou Guangwen'


def session_path():
    try:
        username = getpass.getuser()
    except Exception:
        username = "unknown"
    path = os.path.join(tempfile.gettempdir(), "oe-sessions-" + username)
    if not os.path.exists(path):
        os.mkdir(path, 0700)
    return path


app = Flask(__name__)
app.register_blueprint(blueprint_messages, url_prefix="/internal")
session_store = FilesystemSessionStore(session_path())


@app.template_filter()
def format_date(s, format):
    return parse(s).strftime(format)


@contextlib.contextmanager
def erpsession_context(environ, session_store, session_lock, sid):
    with session_lock:
        if sid:
            environ['erpsession'] = session_store.get(sid)
        else:
            environ['erpsession'] = session_store.new()
    try:
        yield environ['erpsession']
    finally:
        # removed_sessions = set()
        # for k,v in environ['erpsession'].items():
        #     if not isinstance(v,session.OpenERPSession):
        #         continue
        #     if getattr(v,'_suicide',False) or (not v._uid and not v.jsonp_requests and v._creation_time + (60*5)<time.time()):
        #         removed_sessions.add(k)
        #         del environ['erpsession'][k]
        with session_lock:
            # if sid:
            #     in_store = environ['erpsession'].get(sid)
            #     for k,v in environ['erpsession'].iteritems():
            #         stored = in_store.get(k)
            #         if stored and isinstance(v,session.OpenERPSession):
            #             if hasattr(v,'contexts_store'):
            #                 del v.contexts_store
            #             if hasattr(v,'domains_store'):
            #                 del v.domains_store
            #             if not hasattr(v,'jsonp_requests'):
            #                 v.jsonp_requests = {}
            #             v.jsonp_requests.update(getattr(stored,'jsonp_requests',{}))
            #     for k,v in in_store.iteritems():
            #         if k not in environ['erpsession'] and k not in removed_sessions:
            #             environ['erpsession'][k] = v
            session_store.save(environ['erpsession'])


def require_erpsession(wrapped_app):
    session_lock = threading.Lock()

    def middleware(environ, start_response):
        req = Request(environ)
        sid = req.cookies.get('sid')
        if not sid:
            sid = req.args.get('sid')
        with erpsession_context(environ, session_store, session_lock, sid) as erpsession:
            environ['erp'] = environ['erpsession'].get(req.cookies.get('instance0|session_id').replace('%22', ''))
            results = wrapped_app(environ, start_response)
        return results

    return middleware


app.wsgi_app = require_erpsession(app.wsgi_app)


def setup_erp_session(sender, **kwargs):
    request.erpsession = None
    request.erpsession = request.environ['erp']


request_started.connect(setup_erp_session, app)

whitespace = re.compile('(\w+)')


class HTMLAbbrev(HTMLParser):
    def __init__(self, maxlength, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.stack = []
        self.maxlength = maxlength
        self.length = 0
        self.done = False
        self.out = []

    def emit(self, thing, count=False):
        if count:
            self.length += len(thing)
        if self.length < self.maxlength:
            self.out.append(thing)
        elif not self.done:
            # trim trailing whitespace
            self.out[-1] = self.out[-1].rstrip()

            # close out tags on the stack
            for tag in reversed(self.stack):
                self.out.append('</%s>' % tag)
            self.done = True

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        attrs = ' '.join('%s="%s"' % (k, v) for k, v in attrs)
        self.emit('<%s%s>' % (tag, (' ' + attrs).rstrip()))

    def handle_endtag(self, tag):
        if tag == self.stack[-1]:
            self.emit('</%s>' % tag)
            del self.stack[-1]
        else:
            pass
            # raise Exception(
            #     'end tag %r does not match stack: %r' % (tag, self.stack))

    def handle_startendtag(self, tag, attrs):
        self.stack.append(tag)
        attrs = ' '.join('%s="%s"' % (k, v) for k, v in attrs)
        self.emit('<%s%s/>' % (tag, (' ' + attrs).rstrip()))

    def handle_data(self, data):
        for word in whitespace.split(data):
            self.emit(word, count=True)

    def handle_entityref(self, name):
        self.emit('&amp;%s;' % name)

    def handle_charref(self, name):
        return self.handle_entityref('#%s' % name)

    def close(self):
        return ''.join(self.out)


@app.template_filter()
def html_truncate(value, maxlen=150):
    parser = HTMLAbbrev(maxlen)
    parser.feed(value)
    return parser.close()