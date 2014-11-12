# -*- encoding:utf-8 -*-
from openerp import exceptions
from openerp.osv import fields
from openerp.osv import osv
from openerp.osv.osv import except_osv, openerp
from openerp.tools.translate import _


class ProjectFiledFiling(osv.Model):
    _name = 'project.project.filed.filing'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _order = 'create_date desc'

    FILING_STATE = [('apply_filing', u'提出申请'), ('manager_approve', u'负责人审批'), ('approve_filing', u'档案室审批'),
                    ('end_filing', u'归档完成')]

    _track = {
        'state': {},
    }

    # noinspection PyUnusedLocal
    def _get_name(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, u'项目文件归档表')
        return result

    _columns = {
        'name': fields.function(_get_name, type='char', string='Name'),
        'state': fields.selection(
            selection=FILING_STATE, string='State', track_visibility='onchange'),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'project_name': fields.char('Project Name', 256),
        'project_serial_number': fields.related('project_id', 'xiangmubianhao', type='char', readonly=True, string='Project Serial Number'),
        'project_scale': fields.related('project_id', 'guimo', type='char', string='Project Scale', readonly=True),
        'project_user': fields.many2many('res.users', 'rel_pj_filing_users', 'filing_id', 'user_id', string='Project Manager'),
        'project_category_id': fields.related('project_id', 'categories_id', type='many2one', relation='project.upcategory',
                                              string='Project Category', readonly=True),
        'project_country_id': fields.related('project_id', 'country_id', type='many2one', relation='res.country', string='Project Country',
                                             readonly=True),
        'project_state_id': fields.related('project_id', 'state_id', type='many2one', relation='res.country.state', string='Project State',
                                           readonly=True),
        'project_city': fields.related('project_id', 'city', type='char', string='Project City', readonly=True),
        'project_begin_date': fields.related('project_id', 'begin_date', type='date', string='Project Begin Date', readonly=True),
        'is_project_member': fields.related('project_id', 'is_project_member', type='boolean', string='Is Member of Project', readonly=True),
        'is_user_is_project_manager': fields.related('project_id', 'is_user_is_project_manager', type='boolean', string='Is user Project Manager',
                                                     readonly=True),
        'project_second_category': fields.many2many('project.project.filed.filling.secondcategory', 'rel_filing_second_category', 'filing_id',
                                                    'second_category_id', string='Secondary Categories',
                                                    states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        'project_end_date': fields.date('Project End Date', required=True,
                                        states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        'tag_ids': fields.many2many('project.project.filed.tag', 'rel_project_filing_tag', 'filing_id', 'tag_id', string='Tags', required=True,
                                    states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        # 概况
        'description': fields.text('Description', states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}, required=True),
        # 借鉴主要案例
        'note': fields.text('Note', states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        'record_ids': fields.one2many('project.project.filed.record', 'filing_id', 'Document Records',
                                      states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        'show_images': fields.many2many('ir.attachment', 'project_filing_show_attachments', 'filing_id', 'attachment_id', string='Show Images',
                                        states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        'end_stage': fields.selection([('cehua', u'策划'), ('qurenfangan', u'确认方案'), ('pingshenqian', u'评审前方案')], 'End Stage',
                                      states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        'create_date': fields.datetime('Created Date', readonly=True),
        'create_uid': fields.many2one('res.users', 'Owner', readonly=True),
        'write_date': fields.datetime('Modification date', select=True),
        'write_uid': fields.many2one('res.users', 'Last Contributor', select=True),
        'version': fields.integer('Filing Version'),
        'attachment_ids': fields.many2many('ir.attachment', 'filing_form_ir_attach_rel', 'filing_id', 'attachment_id', 'Filing Attachments',
                                           states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),

        'elec_file_approver_id': fields.many2one('res.users', 'Elec File Approver'),
        'elec_file_approver_date': fields.datetime('Elec File Approve Datetime'),
        'manager_approver_id': fields.many2one('res.users', 'Manager Approver'),
        'manager_approver_date': fields.datetime('Manager Approve Datetime'),
        'paper_file_approver_id': fields.many2one('res.users', 'Paper File Approver'),
        'paper_file_approver_date': fields.datetime('Paper File Approve Datetime'),
        # 立卷人
        'import_paper_builder': fields.char('Import Papar Builder', size=128),
        # 图别
        'import_graph_type': fields.char('Import Graph Type', size=128),
        # 张数合计
        'import_total_paper': fields.char('Import Total Paper', size=128),
        'is_import': fields.boolean('Is Import'),
    }

    _defaults = {
        'state': 'apply_filing',
        'project_end_date': lambda *args: fields.date.today(),
        'version': 1,
        'is_import': False,
    }

    def button_apply_filing(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        content_sms = u'项目[%s]需要您处理,请及时处理项目和跟进项目进度。' % filing.project_id.name
        context['mail_create_nosubscribe'] = True
        self.message_post(cr, uid, ids, body=content_sms, subject=u'项目归档审批通知', subtype='mail.mt_comment', type='comment', context=context,
                          user_ids=[u.id for u in filing.project_user], is_send_sms=True)
        filing.project_id.write({'status_code': 30104})
        return self.write(cr, uid, ids, {'state': 'manager_approve'}, context)

    def button_manager_approve(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        content_sms = u'项目[%s]需要您处理,请及时处理项目和跟进项目进度。' % filing.project_id.name
        context['mail_create_nosubscribe'] = True
        self.message_post(cr, uid, ids, body=content_sms, subject=u'项目归档审批通知', subtype='mail.mt_comment', type='comment', context=context,
                          group_xml_ids='up_project.group_up_project_filed_elec_manager', is_send_sms=True)
        filing.project_id.write({'status_code': 30103})
        return self.write(cr, uid, ids, {'state': 'approve_filing', 'manager_approver_id': uid, 'manager_approver_date': fields.datetime.now()},
                          context)

    def button_manager_disapprove(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        filing.project_id.write({'status_code': 30101})
        content_sms = u'项目[%s]需要您处理,请及时处理项目和跟进项目进度。' % filing.project_id.name
        context['mail_create_nosubscribe'] = True
        self.message_post(cr, uid, ids, body=content_sms, subject=u'项目归档审批通知', subtype='mail.mt_comment', type='comment', context=context,
                          user_ids=[filing.create_uid.id], is_send_sms=True)
        return self.write(cr, uid, ids, {'state': 'apply_filing', 'manager_approver_id': False, 'manager_approver_date': False},
                          context)

    def button_approve_filing(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        if not filing.elec_file_approver_id:
            raise except_osv('Warnning', u'电子文件审批没有通过，请等待电子文件审批完成后再进行此操作')
        project_id = filing.project_id.id
        self.pool['project.project']._workflow_signal(cr, uid, [project_id], 's_filed_filing_finish', context=context)
        attachment_obj = self.pool['ir.attachment']
        attachment_obj.filing_project_attachments(cr, 1, [a.id for a in filing.attachment_ids], context)
        filing.project_id.write({'status_code': 30102})
        # send filing success message
        content_sms = u'项目[%s]归档审批通过。' % filing.project_id.name
        context['mail_create_nosubscribe'] = True
        self.message_post(cr, uid, ids, body=content_sms, subject=u'项目归档审批通知', subtype='mail.mt_comment', type='comment', context=context,
                          user_ids=[u.id for u in filing.project_user], is_send_sms=True)
        return self.write(cr, uid, ids, {'state': 'end_filing', 'paper_file_approver_id': uid, 'paper_file_approver_date': fields.datetime.now()},
                          context)

    def button_disapprove_filing(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        filing.project_id.write({'status_code': 30104})
        content_sms = u'项目[%s]需要您处理,请及时处理项目和跟进项目进度。' % filing.project_id.name
        context['mail_create_nosubscribe'] = True
        self.message_post(cr, uid, ids, body=content_sms, subject=u'项目归档审批通知', subtype='mail.mt_comment', type='comment', context=context,
                          user_ids=[u.id for u in filing.project_user], is_send_sms=True)
        return self.write(cr, uid, ids,
                          {'state': 'manager_approve', 'paper_file_approver_id': None, 'paper_file_approver_date': None, 'manager_approver_id': False,
                           'manager_approver_date': False}, context)

    def button_elec_approve(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'elec_file_approver_id': uid, 'elec_file_approver_date': fields.datetime.now()}, context=context)
        filing = self.browse(cr, uid, ids[0], context)
        # send filing success message
        content_sms = u'项目[%s]电子审批通过,请及时处理项目和跟进项目进度。' % filing.project_id.name
        context['mail_create_nosubscribe'] = True
        self.message_post(cr, uid, ids, body=content_sms, subject=u'项目归档审批通知', subtype='mail.mt_comment', type='comment', context=context,
                          group_xml_ids='up_project.group_up_project_filed_manager', is_send_sms=True)
        return True

    def button_show_filing_update_list(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        project_dir_id = self.pool['ir.model.data'].get_object(cr, uid, 'up_project', 'dir_up_project_going', context=context)
        temp_context = {
            'search_index_model': ('res_model', '=', 'project.project'),
            'search_index_id': ('res_id', '=', filing.project_id.id),
            'default_res_model': 'project.project',
            'default_res_id': filing.project_id.id,
            'eval_context': True
        }
        return {
            'name': u'项目待归档文件',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_type': 'tree',
            'res_model': 'document.directory',
            'target': 'current',
            'context': temp_context,
            'domain': [('id', '=', project_dir_id.id)],
        }

    def button_show_filing_attachment_analysis(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        return {
            'name': u'项目已归档电子文件记录',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'project.project.filed.filing.attachment.analysis',
            'target': 'new',
            'domain': [('project_id', '=', filing.project_id.id)],
        }

    def write(self, cr, user, ids, vals, context=None):
        if 'show_images' in vals:
            super(ProjectFiledFiling, self).write(cr, user, ids, {'show_images': [(5,)]}, context)
        return super(ProjectFiledFiling, self).write(cr, user, ids, vals, context)

    def create(self, cr, user, vals, context=None):
        if context:
            context.update({'mail_create_nolog': True})
        else:
            context = {'mail_create_n`olog': True}
        return super(ProjectFiledFiling, self).create(cr, user, vals, context)

    def _message_get_auto_subscribe_fields(self, cr, uid, updated_fields, auto_follow_fields=['user_id'], context=None):
        return []


class ProjectFiledFilingTag(osv.Model):
    _name = 'project.project.filed.tag'

    # noinspection PyUnusedLocal
    def _get_parent_id_id(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, 0)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.parent_id.id
        return result

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'parent_id': fields.many2one('project.project.filed.tag', 'Parent Tag'),
        'parent_id_id': fields.function(_get_parent_id_id, type='integer', string='Parent Id For colors'),
    }

    _sql_constraints = [
        ('project_tag_name_unq', 'unique (name)', 'The name of the tag must be unique !')
    ]

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not self.search(cr, uid, [('id', 'in', ids)]):
            ids = []
        for d in self.browse(cr, uid, ids, context=context):
            res.append((d.id, (d.parent_id.name if d.parent_id else '') + '/' + d.name))
        return res


class ProjectFiledFilingType(osv.Model):
    _name = 'project.project.filed.type'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
    }


class ProjectFiledFilingRecord(osv.Model):
    _name = 'project.project.filed.record'
    _order = 'type_id'

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'type_id': fields.many2one('project.project.filed.type', 'Type', required=True),
        # 页数
        'page_count': fields.integer('Page Count'),
        # 份数
        'copy_count': fields.integer('Copy Count / Zhehe A1'),
        'filing_id': fields.many2one('project.project.filed.filing', 'Related Filing Form', ondelete='cascade'),
        'comment': fields.char('Comment', size=256),
        'document_number': fields.char('Document Number', size=64),
        'is_template': fields.boolean('Is Template'),
    }

    _defaults = {
        'is_template': False,
    }


class ProjectProjectInherit(osv.Model):
    _inherit = 'project.project'

    # noinspection PyUnusedLocal
    def _get_filing_state(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, '')
        filing_obj = self.pool.get('project.project.filed.filing')
        filing_ids = filing_obj.search(cr, uid, [('project_id', '=', ids[0])], order='create_date desc', context=context)
        if filing_ids:
            result[ids[0]] = filing_obj.browse(cr, uid, filing_ids[0], context).state
        return result

    # noinspection PyUnusedLocal
    def _filed_field_calc(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, None)
        filing_obj = self.pool.get('project.project.filed.filing')
        for id in ids:
            result[id] = {
                'is_multi_filing_allowed': False,
                'filed_times': False,
                'filed_project_end_date': None,
                'filed_import_paper_builder': None,
                'filed_import_total_paper': None,
                'filed_import_tag_ids': None,
                'filed_description': None,
                'filed_show_images': None,
            }
            project = self.browse(cr, uid, id, context=context)
            filing_ids = filing_obj.search(cr, uid, [('project_id', '=', id), ('state', 'not in', ['end_filing'])], order='create_date desc',
                                           context=context)
            filed_records = filing_obj.search(cr, uid, [('project_id', '=', id), ('state', 'in', ['end_filing'])], order='create_date desc',
                                              context=context)
            filed_times = len(filed_records)
            # if is allow multi filing
            if project.state == 'project_finish' and not filing_ids and filing_obj.search(cr, uid, [('project_id', '=', id)], context=context):
                result[id]['is_multi_filing_allowed'] = True
            result[id]['filed_times'] = filed_times
            # if have filing record,show detail in project page
            if filed_records:
                filing_form = filing_obj.browse(cr, uid, filed_records[0], context)
                result[id]['filed_project_end_date'] = filing_form.project_end_date
                result[id]['filed_import_paper_builder'] = filing_form.import_paper_builder
                result[id]['filed_import_total_paper'] = filing_form.import_total_paper
                result[id]['filed_import_tag_ids'] = [t.id for t in filing_form.tag_ids]
                result[id]['filed_description'] = filing_form.description
                result[id]['filed_show_images'] = [a.id for a in filing_form.show_images]
        return result

    _columns = {
        'filed_filing_ids': fields.one2many('project.project.filed.filing', 'project_id', 'Related Filing Form'),
        'filed_filing_state': fields.function(_get_filing_state, type='selection', selection=ProjectFiledFiling.FILING_STATE, string='Filing State'),
        'is_multi_filing_allowed': fields.function(_filed_field_calc, type='boolean', string='Is Multi Filing Allowed', multi='filed'),
        'filed_times': fields.function(_filed_field_calc, type='integer', string='Is Multi Filing Allowed', multi='filed'),
        # 归档日期
        'filed_project_end_date': fields.function(_filed_field_calc, type='date', string='Project End Date', multi='filed', readonly=True),
        # 立卷人
        'filed_import_paper_builder': fields.function(_filed_field_calc, type='char', string='Filed Paper Builder', multi='filed', readonly=True),
        # 张数合计
        'filed_import_total_paper': fields.function(_filed_field_calc, type='char', string='Filed Total Paper', multi='filed', readonly=True),
        # 关键词
        'filed_import_tag_ids': fields.function(_filed_field_calc, type='many2many', relation='project.project.filed.tag', string='Filed Tags',
                                                multi='filed', readonly=True),
        # 概况
        'filed_description': fields.function(_filed_field_calc, type='char', string='Filed Description', multi='filed', readonly=True),
        # 推荐图纸
        'filed_show_images': fields.function(_filed_field_calc, type='many2many', relation='ir.attachment', string='File Show Images', multi='filed',
                                             readonly=True)
    }

    def button_filed_filing_form(self, cr, uid, ids, context):
        filing_obj = self.pool.get('project.project.filed.filing')
        project = self.browse(cr, uid, ids[0], context=context)
        filing_id = None
        user_ids = self.read(cr, uid, ids[0], ['user_id'], context=context)['user_id']
        filing_ids = filing_obj.search(cr, uid, [('project_id', '=', ids[0])], order='create_date desc', context=context)
        # if have filing record then show the last filing form
        if filing_ids:
            filing_id = filing_ids[0]
        else:
            # if project is in project filing state then created
            if project.state == 'project_filed':
                template_ids = self.pool['project.project.filing.record.template'].get_record_ids(cr, uid, context=context)
                new_datas = []
                for template_id in template_ids:
                    data = self.pool['project.project.filed.record'].copy_data(cr, uid, template_id, context=context)
                    data['is_template'] = False
                    new_datas += [(0, 0, data), ]
                filing_id = filing_obj.create(cr, uid, {'project_id': ids[0], 'record_ids': new_datas, 'project_name': project.name,
                                                        'project_user': [(6, 0, user_ids)]}, context=context)
                # Write Status Code
                project.write({'status_code': 30101})
            # else if project is in project filed state
            elif project.state == 'project_finish':
                raise exceptions.Warning(u'本项目没有归档表单！')
        # if user is project member
        if not self.is_project_member(cr, uid, project.id, context):
            context['editable'] = False
        if filing_id:
            return {
                'name': u'项目文件归档表',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'project.project.filed.filing',
                'target': 'current',
                'context': context,
                'res_id': filing_id,
            }
        else:
            return False

    def button_multi_filing_form(self, cr, uid, ids, context):
        filing_obj = self.pool.get('project.project.filed.filing')
        project = self.browse(cr, uid, ids[0], context=context)
        user_ids = self.read(cr, uid, ids[0], ['user_id'], context=context)['user_id']
        filing_ids = filing_obj.search(cr, uid, [('project_id', '=', ids[0]), ('state', 'not in', ['end_filing'])], order='create_date desc',
                                       context=context)
        # if is allow multi filing
        if project.state == 'project_finish' and not filing_ids and filing_obj.search(cr, uid, [('project_id', '=', ids[0])], context=context):
            old_filing_id = filing_obj.search(cr, uid, [('project_id', '=', ids[0])], order='create_date desc', context=context)[0]
            old_filing = filing_obj.browse(cr, uid, old_filing_id, context)
            new_filing_id = filing_obj.copy(cr, uid, old_filing_id, context)
            (dummy, type_id) = self.pool['ir.model.data'].get_object_reference(cr, uid, 'up_project', 'project_filed_type_0004')
            filing_obj.write(cr, uid, new_filing_id, {
                'version': old_filing.version + 1,
                'attachment_ids': [(5,)],
                'project_end_date': fields.date.today(),
                'record_ids': [(0, 0, {'name': u'____项目更改记录表', 'type_id': type_id})],
                'elec_file_approver_id': None,
                'elec_file_approver_date': None,
                'paper_file_approver_id': None,
                'paper_file_approver_date': None,
                'manager_approver_id': False,
                'manager_approver_date': False,
                'project_user': [(6, 0, user_ids)],
                'is_import': False,
                'import_paper_builder': None,
                'import_graph_type': None,
                'import_total_paper': None,
            }, context=context)
            project.write({'status_code': 30101})
            filing_obj.message_unsubscribe_users(cr, uid, [new_filing_id], [uid], context=context)
            return True

    # noinspection PyUnusedLocal
    def button_filed_filing_form_history(self, cr, uid, ids, context):
        return {
            'name': u'项目文件归档表',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.project.filed.filing',
            'target': 'current',
            'context': context,
            'domain': [('project_id', 'in', ids)],
        }


class FilingElecAttachmentsAnalysis(osv.Model):
    _name = "project.project.filed.filing.attachment.analysis"
    _description = "Project Filing Attachments Analysis"
    _rec_name = "attachment_id"
    _order = "version desc,parent_id"
    _auto = False

    _columns = {
        'attachment_id': fields.many2one('ir.attachment', 'Attachment'),
        'parent_id': fields.many2one('document.directory', 'Directory'),
        'filing_id': fields.many2one('project.project.filed.filing', 'Filing'),
        'project_id': fields.many2one('project.project', 'Project'),
        'version': fields.integer('Version'),
        'create_date': fields.datetime('Created Date', readonly=True),
        'create_uid': fields.many2one('res.users', 'Owner', readonly=True),
        'write_date': fields.datetime('Modification date', select=True),
        'write_uid': fields.many2one('res.users', 'Last Contributor', select=True),
    }

    def init(self, cr):
        openerp.tools.sql.drop_view_if_exists(cr, 'project_project_filed_filing_attachment_analysis')
        cr.execute(
            " CREATE VIEW project_project_filed_filing_attachment_analysis AS ( "
            " SELECT "
            " r.attachment_id as id,"
            " a.parent_id as parent_id,"
            " r.filing_id as filing_id,"
            " r.attachment_id as attachment_id,"
            " f.project_id as project_id,"
            " f.version as version,"
            " a.create_date as create_date,"
            " a.create_uid as create_uid,"
            " a.write_date as write_date,"
            " a.write_uid as write_uid"
            " FROM "
            " filing_form_ir_attach_rel as r LEFT JOIN project_project_filed_filing as f"
            " on r.filing_id = f.id"
            " LEFT JOIN ir_attachment as a"
            " on a.id = r.attachment_id"
            " )"
        )


class SecondaryCategory(osv.Model):
    _name = 'project.project.filed.filling.secondcategory'
    _columns = {
        'name': fields.char('Name', size=128),
        'category_id': fields.many2one('project.upcategory', 'Project Category'),
    }