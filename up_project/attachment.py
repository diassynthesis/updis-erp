# coding=utf-8
from openerp import tools
from openerp.osv import osv
from openerp.tools.translate import _

__author__ = 'cysnake4713'

FILING_DIR_MAP = {
    'dir_up_project_going': 'dir_up_project_filed',
    'dir_up_project_going_processing': 'dir_up_project_filed_processing',
    'dir_up_project_going_processing_dwg': 'dir_up_project_filed_processing_dwg',
    'dir_up_project_going_processing_psd': 'dir_up_project_filed_processing_psd',
    'dir_up_project_going_processing_report': 'dir_up_project_filed_processing_report',
    'dir_up_project_going_iso': 'dir_up_project_filed_iso',
    'dir_up_project_going_iso_workflow': 'dir_up_project_filed_iso_workflow',
    'dir_up_project_activing': 'dir_up_project_active',
    'dir_up_project_going_iso_contract': 'dir_up_project_filed_iso_contract',
    'dir_up_project_going_iso_memo': 'dir_up_project_filed_iso_memo',
    'dir_up_project_going_result': 'dir_up_project_filed_result',
    'dir_up_project_going_result_media': 'dir_up_project_filed_result_media',
    'dir_up_project_going_result_guide': 'dir_up_project_filed_result_guide',
    'dir_up_project_going_result_picture': 'dir_up_project_filed_result_picture',
    'dir_up_project_going_result_doc': 'dir_up_project_filed_result_doc',
    'dir_up_project_going_result_else': 'dir_up_project_filed_result_else',
    'dir_up_project_going_brief': 'dir_up_project_filed_brief',
    'dir_up_project_going_brief_display': 'dir_up_project_filed_brief_display',
    'dir_up_project_going_brief_brief': 'dir_up_project_filed_brief_brief',
    'dir_up_project_going_brief_picture': 'dir_up_project_filed_brief_picture',
    'dir_up_project_going_data': 'dir_up_project_filed_data',
    'dir_up_project_going_data_cadastral': 'dir_up_project_filed_data_cadastral',
    'dir_up_project_going_data_terrain': 'dir_up_project_filed_data_terrain',
    'dir_up_project_going_data_tellite': 'dir_up_project_filed_data_tellite',
    'dir_up_project_going_data_outsource': 'dir_up_project_filed_data_outsource',
}


class IrAttachmentInherit(osv.Model):
    _inherit = 'ir.attachment'

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context)
        for record in records:
            if record.res_model == 'project.project':
                trash = self.pool['ir.model.data'].get_object(cr, uid, 'up_project', 'dir_up_project_trash', context=context)
                self.write(cr, uid, ids, {'parent_id': trash.id}, context=context)
            return super(IrAttachmentInherit, self).unlink(cr, uid, ids, context)


    def filing_project_attachments(self, cr, uid, ids, context):
        for attachment in self.browse(cr, uid, ids, context):
            dir_map = self.get_filing_id_dir_map(cr, uid, ids, context)
            src_dir = attachment.parent_id.id
            target_dir = dir_map[src_dir]
            if target_dir:
                conflict_attachment_id = self.search(cr, uid, [('name', '=', attachment.name),
                                                               ('res_model', '=', attachment.res_model), ('res_id', '=', attachment.res_id),
                                                               ('parent_id', '=', target_dir)], context=context)
                if conflict_attachment_id:
                    conflict_attachment = self.browse(cr, uid, conflict_attachment_id[0], context=context)
                    conflict_attachment.write({'name': u'历史版本' + conflict_attachment.create_date + '_' + conflict_attachment.name}, context=context)
                attachment.write({'parent_id': target_dir}, context=context)


    # noinspection PyUnusedLocal
    @tools.ormcache()
    def get_filing_id_dir_map(self, cr, uid, id, context=None):
        data_obj = self.pool['ir.model.data']
        result = {}
        for (key, value) in FILING_DIR_MAP.items():
            new_key = data_obj.get_object_reference(cr, uid, 'up_project', key)
            new_value = data_obj.get_object_reference(cr, uid, 'up_project', value)
            result.update({new_key[1]: new_value[1]})
        return result