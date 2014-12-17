__author__ = 'cysnake4713'
from openerp.osv import osv, fields


class project_engineer_room_config_wizard(osv.osv_memory):
    _name = "project.engineer.room.config.wizard"
    _description = "project Engineer Room Config"
    _columns = {
        'users': fields.many2many("res.users", "project_engineer_room_res_users", "project_id",
                                  "res_user_id",
                                  "Users"),
    }

    def default_get(self, cr, uid, fields_v, context=None):
        res = super(project_engineer_room_config_wizard, self).default_get(cr, uid, fields_v, context=context)
        group_data_id = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'res.groups'),
                                                                      ('name', '=',
                                                                       'group_up_project_zongshishi')],
                                                              context=context)
        group_id = self.pool.get('ir.model.data').read(cr, 1, group_data_id[0], ['res_id'])

        groups_obj = self.pool.get('res.groups')
        group_id = groups_obj.search(cr, 1, [('id', '=', group_id['res_id'])], context=context)
        groups = groups_obj.browse(cr, 1, group_id, context=context)[0]

        if 'users' in fields_v:
            res['users'] = [u.id for u in groups.users]

        return res

    def config_accept(self, cr, uid, ids, context=None):
        group_data_id = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'res.groups'),
                                                                      ('name', '=',
                                                                       'group_up_project_zongshishi')],
                                                              context=context)
        group_id = self.pool.get('ir.model.data').read(cr, 1, group_data_id[0], ['res_id'])

        groups_obj = self.pool.get('res.groups')
        self_record = self.browse(cr, uid, ids[0], context)

        groups_obj.write(cr, 1, [group_id['res_id']], {
            'users': [(6, 0, [z.id for z in self_record.users])],

        })
        return True


class FilingRecordTemplate(osv.Model):
    _name = 'project.project.filing.record.template'
    _columns = {
        'filing_record_id': fields.integer('Record Id'),
    }

    def get_record_ids(self, cr, uid, context):
        ids = self.search(cr, uid, [], context=context)
        return [t.filing_record_id for t in self.browse(cr, uid, ids, context)]


class ProjectFiledSettings(osv.TransientModel):
    _name = 'project.project.config.filed.settings'
    _inherit = 'res.config.settings'
    _columns = {
        'filing_record_template': fields.many2many('project.project.filed.record', 'rel_project_filed_setting_filing_record_wizard', 'company_id',
                                                   'record_id', domain=[('is_template', '=', True)], string='Filing Record Template'),
    }

    def get_default_filing_record_template(self, cr, uid, fields, context=None):
        template_obj = self.pool['project.project.filing.record.template']
        return {'filing_record_template': template_obj.get_record_ids(cr, uid, context=context)}

    def set_filing_record_template(self, cr, uid, ids, context):
        ids = self.browse(cr, uid, ids[0], context).filing_record_template
        template_obj = self.pool['project.project.filing.record.template']
        cr.execute('delete from project_project_filing_record_template')
        for rid in ids:
            template_obj.create(cr, uid, {'filing_record_id': rid.id}, context=context)


class ProjectProjectConfig(osv.osv_memory):
    _name = "project.project.config.wizard"
    _inherit = 'res.config.settings'

    _columns = {

    }