# coding=utf-8
__author__ = 'cysnake4713'


from openerp.osv import osv, fields


class HrMember(osv.Model):
    _name = 'hr.member'
    _columns = {
        'name': fields.char('Name', 64,required=True),
        'type': fields.selection([('intern', 'Intern'), ('recuit', 'Recuit')], 'Member Type'),
        'gender': fields.selection([(u'男', u'男'), (u'女', u'女')], 'Gender'),
        'birthday': fields.date('Birthday'),
        'native_place': fields.char('Native Place', 32),
        'folk': fields.char('Folk', 32),
        'academy': fields.char("Academy", 128),
        'major': fields.char("Major", 128),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'moblie': fields.char('Moblie', 24),
        'qq': fields.char('QQ or Weichat', size=32),
        'image': fields.binary('Image'),
        'resume': fields.binary('Resume'),
        'works': fields.binary('Works'),
    }
