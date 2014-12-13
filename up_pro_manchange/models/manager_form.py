# coding=utf-8
__author__ = 'cysnake4713'

from openerp.osv import osv, fields


class ManagerForm(osv.Model):
    _name = 'project.project.manager.change'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'name': fields.char('Project Manager & Chief Change', size=64),
        'origin_manager': fields.many2many('res.users', 'origin_manager_change_res_user_rel', 'file_id', 'user_id', 'Origin Manager'),
        'origin_chief': fields.many2many('res.users', 'origin_chief_change_res_user_rel', 'file_id', 'user_id', 'Origin Chief'),

        'target_manager': fields.many2many('res.users', 'target_manager_change_res_user_rel', 'file_id', 'user_id', 'Target Manager'),
        'target_chief': fields.many2many('res.users', 'target_chief_change_res_user_rel', 'file_id', 'user_id', 'Target Chief'),

        'attachment_ids': fields.many2many('ir.attachment', 'manager_change_attachment_rel', 'change_id', 'attachment_id', 'Documents'),

        'state': fields.selection(
            [('draft', u'申请'), ('director', u'所长审批'), ('chief', u'主管总师审批'), ('yuanzhang', u'院长审批'), ('complete', u'完成'), ('cancel', u'取消')],
            'State', track_visibility='onchange'),

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
        'name': u'项目负责人和主管总师变更',
    }

    def _is_same_department(self, cr, uid, ids, context):
        # Is project director?
        application = self.browse(cr, uid, ids[0], context)
        hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
        apply_hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', application.apply_id.id)], context=context)
        if hr_id and apply_hr_id and self.user_has_groups(cr, uid, "up_project.group_up_project_suozhang",
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
        subject = u'项目负责人和主管总师变更申请'
        context['mail_create_nosubscribe'] = True
        if vals['target'] == 'suozhang':
            suzhang_ids = self.pool['res.users'].get_department_suzhang_ids(cr, uid, [uid], context=context)
            # zhurengong_ids = self.pool['res.users'].get_department_zhurengong_ids(cr, uid, [uid], context=context)
            self.message_post(cr, uid, ids, body=sms_msg, subject=subject, subtype='mail.mt_comment', type='comment', context=context,
                              user_ids=suzhang_ids, is_send_sms=True)
        if vals['target'] == 'group':
            group_id = vals['group_ids']
            self.message_post(cr, uid, ids, body=sms_msg, subject=subject, subtype='mail.mt_comment', type='comment', context=context,
                              group_xml_ids=group_id, is_send_sms=True)
        if vals['target'] == 'user':
            user_ids = vals['user_ids']
            self.message_post(cr, uid, ids, body=sms_msg, subject=subject, subtype='mail.mt_comment', type='comment', context=context,
                              user_ids=user_ids, is_send_sms=True)
        return True

    def _apply_state(self, cr, uid, ids, vals, context):
        return self._update_state(cr, uid, ids, vals, True, context)

    def _reject_state(self, cr, uid, ids, vals, context):
        return self._update_state(cr, uid, ids, vals, False, context)

    def apply(self, cr, uid, ids, context):
        change_file = self.browse(cr, uid, ids[0], context)
        if set([om.id for om in change_file.origin_manager]) == set([tm.id for tm in change_file.target_manager]) and \
                        set([oc.id for oc in change_file.origin_chief]) == set([tc.id for tc in change_file.target_chief]):
            raise osv.except_osv(u'没有修改', u'您还未填写人员调整表单，请返回点击左上角“编辑”按钮编辑表单后再提交申请！')
        values = {
            'user_field': 'apply_id',
            'date_field': 'apply_date',
            'state': 'director',
            'sms': u"项目:%s -> 负责人变更申请,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'suozhang',
        }
        return self._apply_state(cr, uid, ids, values, context)

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
        return self._apply_state(cr, uid, ids, values, context)

    def director_reject(self, cr, uid, ids, context):
        if not self._is_same_department(cr, uid, ids, context):
            raise osv.except_osv(u'没有权限', u'必须是申请人所在部门所长才能审批')
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'apply_id',
            'date_field': 'apply_date',
            'state': 'draft',
            'sms': u"项目:%s -> 负责人变更申请被打回,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'user',
            'user_ids': [change_file.apply_id.id],
        }
        return self._reject_state(cr, uid, ids, values, context)

    def chief_apply(self, cr, uid, ids, context):
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'chief_id',
            'date_field': 'chief_date',
            'state': 'yuanzhang',
            'sms': u"项目:%s -> 负责人变更申请,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'group',
            'group_ids': 'up_pro_manchange.manager_change_yuanzhang',
        }
        return self._apply_state(cr, uid, ids, values, context)

    def chief_reject(self, cr, uid, ids, context):
        change_file = self.browse(cr, uid, ids[0], context)
        values = {
            'user_field': 'director_id',
            'date_field': 'director_date',
            'state': 'director',
            'sms': u"项目:%s -> 负责人变更申请被打回,请登陆系统处理" % change_file.project_id.name,
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': 'suozhang',
        }
        return self._reject_state(cr, uid, ids, values, context)

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
            'user_ids': list(set(notify_user_ids)),
        }
        result = self._apply_state(cr, uid, ids, values, context)
        change_file = self.browse(cr, uid, ids[0], context)
        log_info = u"""项目负责人变更：
主管总师： %s -> %s,
项目负责人： %s -> %s,
发起人:(%s)  所长审批:(%s)  总师审批:(%s)  院长审批:(%s)""" % (
            ','.join([u.name for u in change_file.origin_chief]),
            ','.join([u.name for u in change_file.target_chief]),
            ','.join([u.name for u in change_file.origin_manager]),
            ','.join([u.name for u in change_file.target_manager]),
            change_file.apply_id.name,
            change_file.director_id.name,
            change_file.chief_id.name,
            change_file.yuanzhang_id.name,
        )
        change_file.project_id.add_log(log_info=log_info, context=context)
        change_file.project_id.message_post(subject=u'项目负责人和主管总师变更', body=log_info, type='notification', context=context)
        change_file.project_id.write({'user_id': [(6, 0, [u.id for u in change_file.target_manager])],
                                      'zhuguanzongshi_id': [(6, 0, [u.id for u in change_file.target_chief])]}, context=context)
        return result

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
        return self._reject_state(cr, uid, ids, values, context)

    def cancel(self, cr, uid, ids, context):
        values = {
            'state': 'cancel',
            'model': 'project.project.manager.change',
            'id': ids[0],
            'target': '',
        }
        return self._apply_state(cr, uid, ids, values, context)

    def create(self, cr, user, vals, context=None):
        if context:
            context.update({'mail_create_nolog': True})
        else:
            context = {'mail_create_nolog': True}
        return super(ManagerForm, self).create(cr, user, vals, context)


class ProjectInherit(osv.Model):
    _inherit = 'project.project'
    _columns = {
    }

    _defaults = {
    }

    def button_change_project_manager(self, cr, uid, ids, context=None):
        project = self.browse(cr, uid, ids[0], context)
        change_ids = self.pool['project.project.manager.change'].search(cr, uid,
                                                                        [('project_id', '=', ids[0]), ('state', 'not in', ['complete', 'cancel'])],
                                                                        limit=1,
                                                                        context=context)
        if change_ids:
            res_id = change_ids[0]
        else:
            user_ids = self.read(cr, uid, ids[0], ['user_id'], context=context)['user_id']
            res_id = self.pool['project.project.manager.change'].create(cr, uid, {
                'origin_manager': [(6, 0, user_ids)],
                'origin_chief': [(6, 0, [u.id for u in project.zhuguanzongshi_id])],
                'target_manager': [(6, 0, user_ids)],
                'target_chief': [(6, 0, [u.id for u in project.zhuguanzongshi_id])],
                'project_id': project.id,
            }, context=context)
        # update chief list
        record = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'project.active.tasking.config'),
                                                               ('name', '=', 'project_active_tasking_config_record')], context=context)
        record_id = self.pool.get('ir.model.data').read(cr, 1, record[0], ['res_id'], context=context)
        target = self.pool.get('project.active.tasking.config').browse(cr, 1, record_id['res_id'], context)
        context['chief_engineer_domain'] = [z.id for z in target.chief_engineer_config]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project.manager.change',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': res_id,
            'views': [(False, 'form')],
            'target': 'current',
            'context': context,
        }
