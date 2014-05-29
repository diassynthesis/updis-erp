# -*- encoding:utf-8 -*-
from openerp import exceptions
import openerp
from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _

FILING_STATE = [('apply_filing', 'Apply Filing'), ('approve_filing', 'Approve Filing'), ('end_filing', 'Filing Complete')]


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
        'project_second_category': fields.char('Project Second Category', size=128,
                                               states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        'project_end_date': fields.date('Project End Date', required=True,
                                        states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        'tag_ids': fields.many2many('project.project.filed.tag', 'rel_project_filing_tag', 'filing_id', 'tag_id', string='Tags', required=True,
                                    states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}),
        # 概况
        'description': fields.text('Description', states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}, required=True),
        # 借鉴主要案例
        'note': fields.text('Note', states={'end_filing': [('readonly', True)], 'approve_filing': [('readonly', True)]}, required=True),
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
    }

    _defaults = {
        'note': u'(自填案例名称，借鉴的主要内容)',
        'state': 'apply_filing',
        'project_end_date': lambda *args: fields.date.today(),
        'version': 1,
    }

    def button_apply_filing(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state': 'approve_filing'}, context)

    def button_approve_filing(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        attachment_obj = self.pool['ir.attachment']
        project_id = filing.project_id.id
        self.pool['project.project']._workflow_signal(cr, uid, [project_id], 's_filed_filing_finish', context=context)
        attachment_obj.filing_project_attachments(cr, 1, [a.id for a in filing.attachment_ids], context)
        return self.write(cr, uid, ids, {'state': 'end_filing'}, context)

    def button_disapprove_filing(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state': 'apply_filing'}, context)

    def button_show_filing_update_list(self, cr, uid, ids, context):
        filing = self.browse(cr, uid, ids[0], context)
        project_dir_id = self.pool['ir.model.data'].get_object(cr, uid, 'up_project', 'dir_up_project', context=context)
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
            'res_model': 'document.directory',
            'target': 'current',
            'context': temp_context,
            'domain': [('parent_id', '=', False), ('id', 'child_of', project_dir_id.id)],
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


class ProjectFiledFilingTag(osv.Model):
    _name = 'project.project.filed.tag'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'parent_id': fields.many2one('project.project.filed.tag', 'Parent Tag'),
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

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'type_id': fields.many2one('project.project.filed.type', 'Type', required=True),
        # 页数
        'page_count': fields.integer('Page Count'),
        # 份数
        'copy_count': fields.integer('Copy Count / A1'),
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
    def _is_multi_filing_allowed(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        filing_obj = self.pool.get('project.project.filed.filing')
        for id in ids:
            project = self.browse(cr, uid, id, context=context)
            filing_ids = filing_obj.search(cr, uid, [('project_id', '=', id), ('state', 'not in', ['end_filing'])], order='create_date desc',
                                           context=context)
            # if is allow multi filing
            if project.state == 'project_finish' and not filing_ids and filing_obj.search(cr, uid, [('project_id', '=', id)], context=context):
                result[id] = True
        return result

    _columns = {
        'filed_filing_ids': fields.one2many('project.project.filed.filing', 'project_id', 'Related Filing Form'),
        'filed_filing_state': fields.function(_get_filing_state, type='selection', selection=FILING_STATE, string='Filing State'),
        'is_multi_filing_allowed': fields.function(_is_multi_filing_allowed, type='boolean', string='Is Multi Filing Allowed'),
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

                filing_id = filing_obj.create(cr, uid, {
                    'project_id': ids[0],
                    'record_ids': new_datas,
                }, context=context)
            # else if project is in project filed state
            elif project.state == 'project_finish':
                raise exceptions.Warning(
                    _("This project is import from old system, don't have filing record!"))
        if filing_id:
            return {
                'name': u'所有项目',
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
            filing_obj.write(cr, uid, new_filing_id, {
                'version': old_filing.version + 1,
                'attachment_ids': [(5,)],
            }, context=context)
            return True

    # noinspection PyUnusedLocal
    def button_filed_filing_form_history(self, cr, uid, ids, context):
        return {
            'name': u'所有项目',
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
    _order = "id desc"
    _auto = False

    _columns = {
        'attachment_id': fields.many2one('ir.attachment', 'Attachment'),
        'parent_id': fields.many2one('document.directory', 'Directory'),
        'filing_id': fields.many2one('project.project.filed.filing', 'Filing'),
        'project_id': fields.many2one('project.project', 'Project'),
        'version': fields.related('filing_id', 'version', type='integer', string='Version'),
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