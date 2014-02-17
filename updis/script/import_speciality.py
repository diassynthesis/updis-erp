#!/usr/bin/python
__author__ = 'cysnake4713', 'Giulio Marcon'

import xmlrpclib

username = 'admin'  #the user
pwd = 'updis_admin_2013'  #the password of the user
dbname = 'develop'  #the database
OPENERP_URL = 'localhost:8069'

# Get the uid
sock_common = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/object')

if __name__ == "__main__":
    # SELECT attachments:
    employee_ids = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', [])
    employee_datas = sock.execute(dbname, uid, pwd, 'hr.employee', 'read', employee_ids, ['strong_point'])

    for employee_data in employee_datas:
        if employee_data['strong_point']:
            print('process employee ... %s' % employee_data['id'])
            strong_points = employee_data['strong_point'].split(',')
            for strong_point in strong_points:
                try:
                    speciality_id = sock.execute(dbname, uid, pwd, 'ir.model.data', 'get_object_reference', '', strong_point)
                    sock.execute(dbname, uid, pwd, 'hr.employee', 'write', employee_data['id'], {'speciality_id': [(4, speciality_id[1])]})
                    print('           ... %s' % speciality_id[1])
                except Exception as e:
                    print("didn't find %s" % strong_point)
    print "done ..."