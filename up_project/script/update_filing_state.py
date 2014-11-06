# coding=utf-8
__author__ = 'cysnake4713', 'Giulio Marcon'

import httplib
import xmlrpclib

username = 'admin'  # the user
pwd = 'updis_admin_2013'  # the password of the user
dbname = 'develop'  # the database
OPENERP_URL = 'localhost:8069'


class TimeoutHTTPConnection(httplib.HTTPConnection):
    def __init__(self, host, timeout=10):
        httplib.HTTPConnection.__init__(self, host, timeout=timeout)
        # self.set_debuglevel(99)
        # self.sock.settimeout(timeout)


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


def get_project_id(p_extend_id):
    extend_id = p_extend_id.replace('\n', '').split('.')
    if len(extend_id) == 1:
        extend_id = [''] + extend_id
    return sock.execute(dbname, uid, pwd, 'ir.model.data', 'get_object_reference', extend_id[0], extend_id[1])[1]


def set_project_filed(p_id):
    sock.execute(dbname, uid, pwd, 'project.project', 'force_project_filed', [p_id])


if __name__ == "__main__":

    in_file = file(u'/home/cysnake4713/KuaiPan/Projects/updis/数据/csv/filing/filing_project.csv')
    for project_extend_id in in_file.readlines():
        project_id = get_project_id(project_extend_id)
        project_pre_state = sock.execute(dbname, uid, pwd, 'project.project', 'read', project_id, ['state'])['state']
        set_project_filed(project_id)
        project_cur_state = sock.execute(dbname, uid, pwd, 'project.project', 'read', project_id, ['state'])['state']
        print 'project_id=%s, pre_status=%s, current_status=%s' % (project_id, project_pre_state, project_cur_state)

    print "done ..."


