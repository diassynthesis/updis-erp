# -*- encoding:utf-8 -*-
import datetime
from openerp.osv import fields
from openerp.osv import osv


class ProjectFiledFiling(osv.Model):
    _name = 'project.project.filed.filing'

    _columns = {
        'state': fields.selection(selection=[('apply_filing', 'Apply Filing'), ('end_filing', 'End Filing')], string='State'),
        'project_id': fields.many2one('project.project', 'Project'),
        'project_scale': fields.related('project_id', 'guimo', type='char', string='Project Scale', readonly=True),
        'project_category_id': fields.related('project_id', 'categories_id', type='many2one', relation='project.upcategory',
                                              string='Project Category', readonly=True),
        'project_country_id': fields.related('project_id', 'country_id', type='many2one', relation='res.country', string='Project Country',
                                             readonly=True),
        'project_state_id': fields.related('project_id', 'state_id', type='many2one', relation='res.country.state', string='Project State',
                                           readonly=True),
        'project_city': fields.related('project_id', 'city', type='char', string='Project City', readonly=True),
        'project_begin_date': fields.related('project_id', 'begin_date', type='date', string='Project Begin Date', readonly=True),
        'tag_ids': fields.many2many('project.project.filed.tag', 'rel_project_filing_tag', 'filing_id', 'tag_id', string='Tags'),
        'description': fields.text('Description'),
        'note': fields.text('Note'),


    }


class ProjectFiledFilingTag(osv.Model):
    _name = 'project.project.filed.tag'

    _columns = {
        'name': fields.char('Name', size=64),
    }


class ProjectProjectInherit(osv.Model):
    _inherit = 'project.project'

    def button_filed_filing_form(self, cr, uid, ids, context):
        #TODO: the relationship between project and filing need discuss
        filing_obj = self.pool.get('project.project.filed.filing')
        filing_ids = filing_obj.search(cr, uid, [('project_id', '=', ids[0])], context=context)
        if filing_ids:
            filing_id = filing_ids[0]
        else:
            filing_id = filing_obj.create(cr, uid, {'project_id': ids[0], }, context=context)
        return {
            'name': u'所有项目',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.project.filed.filing',
            'target': 'current',
            'context': context,
            'res_id': filing_id,
        }