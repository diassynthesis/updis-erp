# -*- encoding:utf-8 -*-
from openerp import exceptions
from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _

FILING_STATE = [('apply_filing', 'Apply Filing'), ('manager_approve', 'Manager Approving'), ('approve_filing', 'Approve Filing'),
                ('end_filing', 'Filing Complete')]


class ProjectFiledFiling(osv.Model):
    _name = 'project.project.filed.filing'

    _order = 'create_date desc'

    # noinspection PyUnusedLocal
    def _get_name(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, u'项目文件归档表')
        return result

    _columns = {
        'name': fields.function(_get_name, type='char', string='Name'),
        'state': fields.selection(
            selection=FILING_STATE, string='State'),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'project_serial_number': fields.related('project_id', 'xiangmubianhao', type='char', readonly=True, string='Project Serial Number'),
        'project_scale': fields.related('project_id', 'guimo', type='char', string='Project Scale', readonly=True),
        'project_user': fields.related('project_id', 'user_id', type="many2many", relation='res.users', string='Project Manager', readonly=True),
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
        'description': fields.text('Description', states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
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
        # 'attachment_ids': fields.many2many('ir.attachment', 'filing_form_ir_attach_rel', 'filing_id', 'attachment_id', 'Filing Attachments',
        # states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),

        # 'elec_file_approver_id': fields.many2one('res.users', 'Elec File Approver'),
        # 'elec_file_approver_date': fields.datetime('Elec File Approve Datetime'),
        'manager_approver_id': fields.many2one('res.users', 'Manager Approver'),
        'manager_approver_date': fields.datetime('Manager Approve Datetime'),
        'paper_file_approver_id': fields.many2one('res.users', 'Paper File Approver'),
        'paper_file_approver_date': fields.datetime('Paper File Approve Datetime'),

    }

    _defaults = {
        'state': 'apply_filing',
        'project_end_date': lambda *args: fields.date.today(),
        'version': 1,
    }

    def button_apply_filing(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        sms_obj = self.pool['sms.sms']
        http_address = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.static.url', default='', context=context)
        http_address += "/#id=%s&amp;view_type=form&amp;model=project.project" % filing.project_id.id
        content_sms = u'项目[%s]需要您处理【项目归档-负责人审批】请求,请及时处理项目和跟进项目进度。' % filing.project_id.name
        content_ant = u"""项目 <![CDATA[<a target='_blank' href='%s'> [%s] </a> ]]> 需要您处理【项目归档-负责人审批】请求,请及时处理项目和跟进项目进度 """ % (
            http_address, filing.project_id.name)
        sms_obj.send_sms_to_users(cr, uid, users=filing.project_user, from_rec=filing.name, content=content_sms, model=self._name, res_id=filing.id,
                                  context=context)
        sms_obj.send_big_ant_to_users(cr, uid, users=filing.project_user, from_rec=filing.name, subject=u'项目归档申请等待处理', content=content_ant,
                                      model=self._name, res_id=filing.id, context=context)
        filing.project_id.write({'status_code': 30104})
        return self.write(cr, uid, ids, {'state': 'manager_approve'}, context)

    def button_manager_approve(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        sms_obj = self.pool['sms.sms']
        http_address = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.static.url', default='', context=context)
        http_address += "/#id=%s&amp;view_type=form&amp;model=project.project" % filing.project_id.id
        content_sms = u'项目[%s]需要您处理【项目归档-图档室审批】请求,请及时处理项目和跟进项目进度。' % filing.project_id.name
        content_ant = u"""项目 <![CDATA[<a target='_blank' href='%s'> [%s] </a> ]]> 需要您处理【项目归档-图档室审批】请求,请及时处理项目和跟进项目进度 """ % (
            http_address, filing.project_id.name)
        sms_obj.send_sms_to_group(cr, uid, from_rec=filing.name, content=content_sms, model=self._name, res_id=filing.id,
                                  group_xml_id='up_project.group_up_project_filed_manager', context=context)
        sms_obj.send_big_ant_to_group(cr, uid, from_rec=filing.name, subject=u'项目归档申请等待处理', content=content_ant, model=self._name, res_id=filing.id,
                                      group_xml_id='up_project.group_up_project_filed_manager', context=context)
        filing.project_id.write({'status_code': 30103})
        return self.write(cr, uid, ids, {'state': 'approve_filing', 'manager_approver_id': uid, 'manager_approver_date': fields.datetime.now()},
                          context)

    def button_manager_disapprove(self, cr, uid, ids, context):
        self.browse(cr, uid, ids[0], context).project_id.write({'status_code': 30101})
        return self.write(cr, uid, ids, {'state': 'apply_filing', 'manager_approver_id': False, 'manager_approver_date': False},
                          context)

    def button_approve_filing(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        # if not filing.elec_file_approver_id:
        # raise except_osv('Warnning', u'电子文件审批没有通过，请等待电子文件审批完成后再进行此操作')
        project_id = filing.project_id.id
        self.pool['project.project']._workflow_signal(cr, uid, [project_id], 's_filed_filing_finish', context=context)
        # attachment_obj = self.pool['ir.attachment']
        # attachment_obj.filing_project_attachments(cr, 1, [a.id for a in filing.attachment_ids], context)
        filing.project_id.write({'status_code': 30102})
        return self.write(cr, uid, ids, {'state': 'end_filing', 'paper_file_approver_id': uid, 'paper_file_approver_date': fields.datetime.now()},
                          context)

    def button_disapprove_filing(self, cr, uid, ids, context):
        self.browse(cr, uid, ids[0], context).project_id.write({'status_code': 30104})
        return self.write(cr, uid, ids,
                          {'state': 'manager_approve', 'paper_file_approver_id': None, 'paper_file_approver_date': None, 'manager_approver_id': False,
                           'manager_approver_date': False}, context)

    # def button_elec_approve(self, cr, uid, ids, context):
    # self.write(cr, uid, ids, {'elec_file_approver_id': uid, 'elec_file_approver_date': fields.datetime.now()}, context=context)
    # return True

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

        # def button_show_filing_attachment_analysis(self, cr, uid, ids, context):
        # filing = self.browse(cr, uid, ids[0], context)
        # return {
        # 'name': u'项目已归档电子文件记录',
        # 'type': 'ir.actions.act_window',
        # 'view_mode': 'tree',
        # 'res_model': 'project.project.filed.filing.attachment.analysis',
        # 'target': 'new',
        # 'domain': [('project_id', '=', filing.project_id.id)],
        # }


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
        result = dict.fromkeys(ids, {'is_multi_filing_allowed': False, 'filed_times': False})
        filing_obj = self.pool.get('project.project.filed.filing')
        for id in ids:
            project = self.browse(cr, uid, id, context=context)
            filing_ids = filing_obj.search(cr, uid, [('project_id', '=', id), ('state', 'not in', ['end_filing'])], order='create_date desc',
                                           context=context)
            filed_times = len(filing_obj.search(cr, uid, [('project_id', '=', id), ('state', 'in', ['end_filing'])], order='create_date desc',
                                                context=context))
            # if is allow multi filing
            if project.state == 'project_finish' and not filing_ids and filing_obj.search(cr, uid, [('project_id', '=', id)], context=context):
                result[id]['is_multi_filing_allowed'] = True
            result[id]['filed_times'] = filed_times
        return result

    _columns = {
        'filed_filing_ids': fields.one2many('project.project.filed.filing', 'project_id', 'Related Filing Form'),
        'filed_filing_state': fields.function(_get_filing_state, type='selection', selection=FILING_STATE, string='Filing State'),
        'is_multi_filing_allowed': fields.function(_filed_field_calc, type='boolean', string='Is Multi Filing Allowed', multi='filed'),
        'filed_times': fields.function(_filed_field_calc, type='integer', string='Is Multi Filing Allowed', multi='filed'),
    }

    def button_filed_filing_form(self, cr, uid, ids, context):
        filing_obj = self.pool.get('project.project.filed.filing')
        project = self.browse(cr, uid, ids[0], context=context)
        filing_id = None
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
                    new_datas += [(0, 0, data), ]
                filing_id = filing_obj.create(cr, uid, {'project_id': ids[0], 'record_ids': new_datas, }, context=context)
                # Write Status Code
                project.write({'status_code': 30101})
            # else if project is in project filed state
            elif project.state == 'project_finish':
                raise exceptions.Warning(
                    _("This project is import from old system, don't have filing record!"))
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
                # 'attachment_ids': [(5,)],
                'project_end_date': fields.date.today(),
                'record_ids': [(0, 0, {'name': u'____项目更改记录表', 'type_id': type_id})],
                # 'elec_file_approver_id': None,
                # 'elec_file_approver_date': None,
                'paper_file_approver_id': None,
                'paper_file_approver_date': None,
                'manager_approver_id': False,
                'manager_approver_date': False,
            }, context=context)
            project.write({'status_code': 30101})
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


# class FilingElecAttachmentsAnalysis(osv.Model):
# _name = "project.project.filed.filing.attachment.analysis"
# _description = "Project Filing Attachments Analysis"
# _rec_name = "attachment_id"
# _order = "version desc,parent_id"
# _auto = False
#
# _columns = {
# 'attachment_id': fields.many2one('ir.attachment', 'Attachment'),
# 'parent_id': fields.many2one('document.directory', 'Directory'),
# 'filing_id': fields.many2one('project.project.filed.filing', 'Filing'),
# 'project_id': fields.many2one('project.project', 'Project'),
# 'version': fields.integer('Version'),
# 'create_date': fields.datetime('Created Date', readonly=True),
# 'create_uid': fields.many2one('res.users', 'Owner', readonly=True),
# 'write_date': fields.datetime('Modification date', select=True),
# 'write_uid': fields.many2one('res.users', 'Last Contributor', select=True),
#     }
#
#     def init(self, cr):
#         openerp.tools.sql.drop_view_if_exists(cr, 'project_project_filed_filing_attachment_analysis')
#         cr.execute(
#             " CREATE VIEW project_project_filed_filing_attachment_analysis AS ( "
#             " SELECT "
#             " r.attachment_id as id,"
#             " a.parent_id as parent_id,"
#             " r.filing_id as filing_id,"
#             " r.attachment_id as attachment_id,"
#             " f.project_id as project_id,"
#             " f.version as version,"
#             " a.create_date as create_date,"
#             " a.create_uid as create_uid,"
#             " a.write_date as write_date,"
#             " a.write_uid as write_uid"
#             " FROM "
#             " filing_form_ir_attach_rel as r LEFT JOIN project_project_filed_filing as f"
#             " on r.filing_id = f.id"
#             " LEFT JOIN ir_attachment as a"
#             " on a.id = r.attachment_id"
#             " )"
#         )


class SecondaryCategory(osv.Model):
    _name = 'project.project.filed.filling.secondcategory'
    _columns = {
        'name': fields.char('Name', size=128),
    }