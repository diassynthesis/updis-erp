__author__ = 'cysnake4713'
from osv import osv, fields

class project_engineer_room_config_wizard(osv.osv_memory):
    _name = "project.engineer.room.config.wizard"
    _description = "project Engineer Room Config"
    _columns = {
        'users': fields.many2many("res.users", "project_engineer_room_res_users", "project_id",
                                  "res_user_id",
                                  "Users"),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(project_engineer_room_config_wizard, self).default_get(cr, uid, fields, context=context)
        group_data_id = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'res.groups'),
                                                                      ('name', '=',
                                                                       'group_up_project_zongshishi')],
                                                              context=context)
        group_id = self.pool.get('ir.model.data').read(cr, 1, group_data_id[0], ['res_id'])

        groups_obj = self.pool.get('res.groups')
        group_id = groups_obj.search(cr, 1, [('id', '=', group_id['res_id'])], context=context)
        groups = groups_obj.browse(cr, 1, group_id, context=context)[0]

        if 'users' in fields:
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


class project_project_config(osv.osv_memory):
    _name = "project.project.config.wizard"
    _columns = {

    }