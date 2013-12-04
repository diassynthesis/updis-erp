__author__ = 'cysnake4713'
# -*- coding: utf-8 -*-
import collections
import gzip
import urllib
import urllib2

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


_HTTP_GET = 0
_HTTP_POST = 1
_METHOD_MAP = {'GET': _HTTP_GET, 'POST': _HTTP_POST}
_BIG_ANT_DOMAIN = "10.100.100.200"
_BIG_ANT_PORT = 6664


class APIError(StandardError):
    '''
    raise APIError if receiving json message indicating failure.
    '''

    def __init__(self, error_code, error, request):
        self.error_code = error_code
        self.error = error
        self.request = request
        StandardError.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s, request: %s' % (self.error_code, self.error, self.request)


def _read_body(obj):
    using_gzip = obj.headers.get('Content-Encoding', '') == 'gzip'
    body = obj.read()
    if using_gzip:
        gzipper = gzip.GzipFile(fileobj=StringIO(body))
        fcontent = gzipper.read()
        gzipper.close()
        return fcontent
    return body


def _encode_params(**kw):
    '''
    do url-encode parameters

    >>> _encode_params(a=1, b='R&D')
    'a=1&b=R%26D'
    >>> _encode_params(a=u'\u4e2d\u6587', b=['A', 'B', 123])
    'a=%E4%B8%AD%E6%96%87&b=A&b=B&b=123'
    '''
    args = []
    for k, v in kw.iteritems():
        if isinstance(v, basestring):
            qv = v.encode('utf-8') if isinstance(v, unicode) else v
            args.append('%s=%s' % (k, urllib.quote(qv)))
        elif isinstance(v, collections.Iterable):
            for i in v:
                qv = i.encode('utf-8') if isinstance(i, unicode) else str(i)
                args.append('%s=%s' % (k, urllib.quote(qv)))
        else:
            qv = str(v)
            args.append('%s=%s' % (k, urllib.quote(qv)))
    return '&'.join(args)


def _http_call(the_url, method, authorization, **kw):
    '''
    send an http request and return a xml object if no error occurred.
    '''
    params = None
    boundary = None
    params = _encode_params(**kw)
    http_url = '%s?%s' % (the_url, params) if method == _HTTP_GET else the_url
    http_body = None if method == _HTTP_GET else params
    req = urllib2.Request(http_url, data=http_body)
    req.add_header('Accept-Encoding', 'gzip')
    try:
        resp = urllib2.urlopen(req, timeout=5)
        body = _read_body(resp)
        r = et.fromstring(body)
        return r
    except urllib2.HTTPError, e:
        try:
            r = _read_body(e)
        except:
            r = None
        if hasattr(r, 'error_code'):
            raise APIError(r.error_code, r.get('error', ''), r.get('request', ''))
        raise e


class HttpObject(object):
    def __init__(self, client, method):
        self.client = client
        self.method = method

    def __getattr__(self, attr):
        def wrap(**kw):
            return _http_call('%s%s' % (self.client.api_url, attr.replace('__', '/')), self.method, **kw)

        return wrap


class BigAntClient(object):
    def __init__(self, domain=_BIG_ANT_DOMAIN, port=_BIG_ANT_PORT):
        self.api_url = 'http://%s:%d/' % (domain, port)
        self.get = HttpObject(self, _HTTP_GET)
        self.post = HttpObject(self, _HTTP_POST)

    def __getattr__(self, attr):
        if '__' in attr and '___' not in attr:
            return getattr(self.get, attr)
        return _Callable(self, attr)


class _Executable(object):
    def __init__(self, client, method, path):
        self._client = client
        self._method = method
        self._path = path

    def __call__(self, **kw):
        method = _METHOD_MAP[self._method]
        return _http_call('%s%s' % (self._client.api_url, self._path), method, self._client.access_token, **kw)

    def __str__(self):
        return '_Executable (%s %s)' % (self._method, self._path)

    __repr__ = __str__


class _Callable(object):
    def __init__(self, client, name):
        self._client = client
        self._name = name.replace('___', '.')

    def __getattr__(self, attr):
        if attr == 'get':
            return _Executable(self._client, 'GET', self._name)
        if attr == 'post':
            return _Executable(self._client, 'POST', self._name)
        name = '%s/%s' % (self._name, attr)
        return _Callable(self._client, name)

    def __str__(self):
        return '_Callable (%s)' % self._name

    __repr__ = __str__


if __name__ == "__main__":
    client = BigAntClient()
    result = client.Employee___asmx.SendMessenge.post(bigantServer="10.100.100.200", port=6660, sendLoginName="xinxi",
                                                      passwordType=0,
                                                      sendPassword="xinxi", contentType='Text/Html', sendUserName="",
                                                      msgId="",
                                                      recvLoginNames="caiyang", subject=u"测试",
                                                      content=u"<a href='#'>asdfasdf</a>")
    print (result)