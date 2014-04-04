#!/usr/bin/python

__author__ = 'cysnake4713', 'Giulio Marcon'

import httplib
import xmlrpclib

username = 'admin'  #the user
pwd = 'updis_admin_2013'  #the password of the user
dbname = 'develop'  #the database
OPENERP_URL = '10.100.100.14:8069'


class TimeoutHTTPConnection(httplib.HTTPConnection):
    def __init__(self, host, timeout=10):
        httplib.HTTPConnection.__init__(self, host, timeout=timeout)
        # self.set_debuglevel(99)
        #self.sock.settimeout(timeout)


"""
class TimeoutHTTP(httplib.HTTP):
    _connection_class = TimeoutHTTPConnection
    def set_timeout(self, timeout):
        self._conn.timeout = timeout
"""


class TimeoutTransport(xmlrpclib.Transport):
    def __init__(self, timeout=10, *l, **kw):
        xmlrpclib.Transport.__init__(self, *l, **kw)
        self.timeout = timeout

    def make_connection(self, host):
        conn = TimeoutHTTPConnection(host, self.timeout)
        return conn


class TimeoutServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, uri, timeout=10, *l, **kw):
        kw['transport'] = TimeoutTransport(timeout=timeout, use_datetime=kw.get('use_datetime', 0))
        xmlrpclib.ServerProxy.__init__(self, uri, *l, **kw)


# Get the uid
sock_common = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
sock = TimeoutServerProxy('http://' + OPENERP_URL + '/xmlrpc/object', timeout=1000)


def migrate_attachment(att_id):
    # 1. get data
    attr = sock.execute(dbname, uid, pwd, 'ir.attachment', 'read', att_id, ['datas'])

    data = attr[0]['datas']

    # Re-Write attachment
    a = sock.execute(dbname, uid, pwd, 'ir.attachment', 'write', [att_id], {'datas': data})


if __name__ == "__main__":
    # SELECT attachments:
    att_ids = sock.execute(dbname, uid, pwd, 'ir.attachment', 'search', [('store_fname', '=', False)])

    cnt = len(att_ids)
    i = 0
    for att_id in att_ids:
        att = sock.execute(dbname, uid, pwd, 'ir.attachment', 'read', att_id, ['datas', 'parent_id'])

        migrate_attachment(att_id)
        print 'Migrated ID %d (attachment %d of %d)' % (att_id + 1, i, cnt)
        i += 1

    print "done ..."