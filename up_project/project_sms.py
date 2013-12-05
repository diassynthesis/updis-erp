from openerp.osv import fields

__author__ = 'cysnake4713'
from osv import osv


class project_sms(osv.osv):
    _name = "project.config.sms"
    _columns = {
        'name': fields.char(size=128, string='Name'),
        'users': fields.many2many('res.users', 'project_sms_users', 'project_config_sms_id', 'user_id',
                                  string='Sms Send To Users'),
    }

