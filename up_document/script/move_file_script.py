#!/usr/bin/python
__author__ = 'cysnake4713', 'Giulio Marcon'

import xmlrpclib

username = 'admin' #the user
pwd = 'updis_admin_2013'      #the password of the user
dbname = 'develop'    #the database
OPENERP_URL = 'localhost:8069'

# Get the uid
sock_common = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/object')


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