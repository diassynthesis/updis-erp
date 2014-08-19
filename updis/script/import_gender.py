#!/usr/bin/python
__author__ = 'cysnake4713', 'Giulio Marcon'

import xmlrpclib

username = 'admin'  #the user
pwd = 'updis_admin_2013'  #the password of the user
dbname = 'develop'  #the database
# OPENERP_URL = '10.100.100.171:8069'
OPENERP_URL = 'localhost:8069'

# Get the uid
sock_common = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/object')

if __name__ == "__main__":
    # SELECT attachments:
    employee_ids = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', [])
    employee_datas = sock.execute(dbname, uid, pwd, 'hr.employee', 'read', employee_ids, ['gender'])

    for employee_data in employee_datas:
        if employee_data['gender']:
            print('process employee ... %s' % employee_data['id'])
            sock.execute(dbname, uid, pwd, 'hr.employee', 'write', employee_data['id'], {'gender_rel': employee_data['gender']})
    print "done ..."