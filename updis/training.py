#encoding:UTF-8
__author__ = 'cysnake4713'
from osv import fields, osv


class updis_hr_training(osv.osv):
    _description = "Employee Training"
    _name = "updis.hr.training"

    _columns = {
        'name': fields.char(size=100, string='Training Name', required=True),
        'time': fields.date(string='Training Time'),
        'organizers': fields.char(size=100, string='Training Organizers'),
        'record_ids': fields.one2many('updis.hr.training.record', 'training_id', 'Training Related employees'),

    }


class updis_hr_training_record(osv.osv):
    _description = "Employee Training Record"
    _name = "updis.hr.training.record"
    _columns = {
        'training_id': fields.many2one('updis.hr.training', 'Training Name', required=True),
        'employee': fields.many2one('hr.employee', 'Employee', required=True),

        'score': fields.selection([(u'pass', u'通过'), (u'fail', u'未通过')], 'Score'),
        'training_certificate': fields.char(string='Certificate Number', size=100),
        'training_time': fields.related('training_id', 'time', type="date",
                                        string="Training Time", readonly=True),
        'training_organizers': fields.related('training_id', 'organizers', type="char",
                                              string="Training Organizers", readonly=True),
    }

    _defaults = {
        'score': u'pass',
    }

