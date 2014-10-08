# coding=utf-8
__author__ = 'cysnake4713'

from openerp.osv import osv, fields


class ManagerForm(osv.Model):
    _name = 'project.project.manager.change'
    _columns = {
        'origin_manager': fields.many2many('res.users', 'origin_manager_change_res_user_rel', 'file_id', 'user_id', 'Origin Manager'),
        'origin_chief': fields.many2many('res.users', 'origin_chief_change_res_user_rel', 'file_id', 'user_id', 'Origin Chief'),

        'target_manager': fields.many2many('res.users', 'target_manager_change_res_user_rel', 'file_id', 'user_id', 'Target Manager'),
        'target_chief': fields.many2many('res.users', 'target_chief_change_res_user_rel', 'file_id', 'user_id', 'Target Chief'),

        'state': fields.selection(
            [('draft', u'申请'), ('director', u'所长审批'), ('chief', u'主管总师审批'), ('yuanzhang', u'院长审批'), ('complete', u'完成'), ('cancel', u'取消')],
            'State'),

        'project_id': fields.many2one('project.project', 'Project', ondelete='cascade'),

        'apply_id': fields.many2one('res.users', 'Apply User'),
        'apply_date': fields.datetime('Apply Date'),

        'director_id': fields.many2one('res.users', 'Director Approver'),
        'director_date': fields.datetime('Director Date'),

        'chief_id': fields.many2one('res.users', 'Chief Approver'),
        'chief_date': fields.datetime('Chief Date'),

        'yuanzhang_id': fields.many2one('res.users', 'Yuanzhang Approver'),
        'yuanzhang_date': fields.datetime('Yuanzhang Date'),

    }

    _defaults = {
        'state': 'draft',
    }

    def _is_same_department(self, cr, uid, ids, context):
        # Is project director?
        application = self.browse(cr, uid, ids[0], context)
        hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
        apply_hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', application.apply_user_id.id)], context=context)
        if hr_id and apply_hr_id and self.user_has_groups(cr, uid, "up_project.group_up_project_suozhang,up_project.group_up_project_zhurengong",
                                                          context=context):
            hr_record = self.pool.get('hr.employee').browse(cr, 1, hr_id[0], context=context)
            apply_record = self.pool.get('hr.employee').browse(cr, 1, apply_hr_id[0], context=context)
            user_department_id = hr_record.department_id.id if hr_record.department_id else "-1"
            apply_department_id = apply_record.department_id.id if hr_record.department_id else "-2"
            if user_department_id == apply_department_id:
                return True
        return False

    def _update_state(self, cr, uid, ids, vals, is_apply=False, context=None):
        write_values = {}
        if is_apply:
            if 'user_field' in vals:
                write_values.update({vals['user_field']: uid})
            if 'date_field' in vals:
                write_values.update({vals['date_field']: fields.datetime.now()})
        else:
            if 'user_field' in vals:
                write_values.update({vals['user_field']: None})
            if 'date_field' in vals:
                write_values.update({vals['date_field']: None})
        if 'state' in vals:
            write_values.update({'state': vals['state']})
        self.write(cr, uid, ids, write_values, context=context)
        sms_msg = vals.get('sms', '')
        http_address = self.pool['ir.config_parameter'].get_param(cr, 1, 'web.base.static.url', context=context)
        big_ant_msg = (
            sms_msg,
            u"请点击这里处理:<a target='_blank' href='%s/#id=%s&model=%s&view_type=form'>审批请求</a>。" % (http_address, vals['id'], vals['model'])
        )
        if vals['target'] == 'suzhang':
            suzhang_ids = self.pool['res.users'].get_department_suzhang_ids(cr, uid, [uid], context=context)
            # zhurengong_ids = self.pool['res.users'].get_department_zhurengong_ids(cr, uid, [uid], context=context)
            self.pool['sms.sms'].send_sms_to_users(cr, uid, vals['model'], sms_msg, vals['model'], vals['id'], suzhang_ids, context)
            self.pool.get('sms.sms').send_big_ant_to_users(cr, uid, vals['model'], big_ant_msg[0], big_ant_msg[1], vals['model'], vals['id'],
                                                           suzhang_ids, context)
        if vals['target'] == 'group':
            group_id = vals['group_ids']
            self.pool['sms.sms'].send_sms_to_group(cr, uid, vals['model'], sms_msg, vals['model'], vals['id'], group_id, context)
            self.pool.get('sms.sms').send_big_ant_to_group(cr, 1, vals['model'], big_ant_msg[0], big_ant_msg[1], vals['model'], vals['id'], group_id,
                                                           context)
        if vals['target'] == 'user':
            user_ids = vals['user_ids']
            self.pool['sms.sms'].send_sms_to_users(cr, uid, vals['model'], sms_msg, vals['model'], vals['id'], user_ids, context)
            self.pool.get('sms.sms').send_big_ant_to_users(cr, uid, vals['model'], big_ant_msg[0], big_ant_msg[1], vals['model'], vals['id'],
                                                           user_ids, context)
        return True

    def _apply_state(self, cr, uid, ids, vals, context):
        self._update_state(cr, uid, ids, vals, True, context)

    def _reject_state(self, cr, uid, ids, vals, context):
        self._update_state(cr, uid, ids, vals, False, context)

    def apply(self, cr, uid, ids, context):
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'apply_id',
            'date_field': 'apply_date',
            'state': 'director',
            'sms': u"项目:%s -> 负责人变更申请,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'suzhang',
        }
        self._apply_state(cr, uid, ids, values, context)

    def director_apply(self, cr, uid, ids, context):
        if not self._is_same_department(cr, uid, ids, context):
            raise osv.except_osv(u'没有权限', u'必须是申请人所在部门所长才能审批')
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'director_id',
            'date_field': 'director_date',
            'state': 'chief',
            'sms': u"项目:%s -> 负责人变更申请,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'group',
            'group_ids': 'up_pro_manchange.manager_change_chief',
        }
        self._apply_state(cr, uid, ids, values, context)

    def director_reject(self, cr, uid, ids, context):
        if not self._is_same_department(cr, uid, ids, context):
            raise osv.except_osv(u'没有权限', u'必须是申请人所在部门所长才能审批')
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'apply_id',
            'date_field': 'apply_date',
            'state': 'apply',
            'sms': u"项目:%s -> 负责人变更申请被打回,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'user',
            'user_ids': [change_file.apply_id.id],
        }
        self._reject_state(cr, uid, ids, values, context)

    def chief_apply(self, cr, uid, ids, context):
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'chief_id',
            'date_field': 'chief_date',
            'state': 'chief',
            'sms': u"项目:%s -> 负责人变更申请,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'group',
            'group_ids': 'up_pro_manchange.manager_change_yuanzhang',
        }
        self._apply_state(cr, uid, ids, values, context)

    def chief_reject(self, cr, uid, ids, context):
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'director_id',
            'date_field': 'director_date',
            'state': 'suzhang',
            'sms': u"项目:%s -> 负责人变更申请被打回,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'suozhang',
        }
        self._reject_state(cr, uid, ids, values, context)

    def yuanzhang_apply(self, cr, uid, ids, context):
        change_file = self.browse(cr, uid, ids[0], context)
        notify_user_ids = [
            change_file.apply_id.id,
            change_file.director_id.id,
            change_file.chief_id.id,
        ]
        values = {
            'user_field': 'yuanzhang_id',
            'date_field': 'yuanzhang_date',
            'state': 'complete',
            'sms': u"项目:%s -> 负责人变更申请通过" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'user',
            'user_ids': notify_user_ids,
        }
        self._apply_state(cr, uid, ids, values, context)
        change_file = self.browse(cr, uid, ids[0], context)
        log_info = u"""项目负责人变更：
主管总师： %s -> %s,
项目负责人： %s -> %s,
发起人：%s 所长审批：%s, 总师审批:%s, 院长审批:%s,""" % (
            change_file.origin_chief.name,
            change_file.target_chief.name,
            change_file.origin_manager.name,
            change_file.target_manager.name,
            change_file.apply_id.name,
            change_file.director_id.name,
            change_file.chief_id.name,
            change_file.yuanzhang_id.name,
        )
        change_file.project_id.add_log(log_info=log_info, context=context)
        change_file.project_id.write({'user_id': [(6, 0, [u.id for u in change_file.target_manager])],
                                      'zhuguanzongshi_id': [(6, 0, [u.id for u in change_file.target_chief])]}, context=context)

    def yuanzhang_reject(self, cr, uid, ids, context):
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'chief_id',
            'date_field': 'chief_date',
            'state': 'chief',
            'sms': u"项目:%s -> 负责人变更申请被打回,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'group',
            'group_ids': 'up_pro_manchange.manager_change_chief',
        }
        self._reject_state(cr, uid, ids, values, context)

    def cancel(self, cr, uid, ids, context):
        values = {
            'state': 'cancel',
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': '',
        }
        self._apply_state(cr, uid, ids, values, context)
