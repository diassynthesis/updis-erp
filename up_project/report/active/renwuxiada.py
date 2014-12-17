import os
import time
import datetime
from openerp.report import report_sxw


class renwuxiada(report_sxw.rml_parse):
    """docstring for renwuxiada"""

    def __init__(self, cr, uid, name, context):
        super(renwuxiada, self).__init__(cr, 1, name, context)
        self.localcontext.update({
            'time': time,
            'date_format': self.date_format,
            'manager_names': self._get_manager_names(context['active_id'], context=context),
            'zongshi_names': self._get_zhuguanzongshi_names(context['active_id'], context=context),
            'bottom_image': self._get_bottom_image(),
            # 'project_active_tasking': self._get_project_active_tasking_form,
        })

    def date_format(self, current_date):
        if current_date.split('.')[0] != 'False':
            create_date_display = datetime.datetime.strptime(current_date.split('.')[0],
                                                             '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
            return create_date_display.strftime('%Y/%m/%d')
        else:
            return ""

    def _get_manager_names(self, pid, context):
        # import pdb;pdb.set_trace()
        project = self.pool.get('project.project.active.tasking')
        user_ids = project.read(self.cr, self.uid, pid, ['user_id'], context=context)
        if user_ids['user_id']:
            return " ".join(
                [u.name for u in self.pool.get('res.users').browse(self.cr, 1, user_ids['user_id'], context=context)])
        else:
            return " "

    def _get_bottom_image(self):
        # import pdb;pdb.set_trace()
        head_img_obj = self.pool.get("ir.header_img")
        img_ids = head_img_obj.search(self.cr, 1, [('name', '=', 'updis_logo')])
        if img_ids:
            head_img = head_img_obj.browse(self.cr, 1, img_ids[0])
            return head_img.img
        else:
            return None

    def _get_zhuguanzongshi_names(self, pid, context):
        # import pdb;pdb.set_trace()
        project = self.pool.get('project.project.active.tasking')
        tasking = project.browse(self.cr, self.uid, pid, context=context)
        return " ".join([z.name for z in tasking.zhuguanzongshi_id])

    def _get_project_active_tasking_form(self, pid):
        form = self.pool.get('project.project.active.tasking')
        form_ids = form.search(self.cr, self.uid, [('project_id', '=', pid)])
        if form_ids:
            return form.browse(self.cr, self.uid, form_ids[0])


report_sxw.report_sxw('report.project.active.tasking.report.pdf', 'project.project.active.tasking',
                      'up_project/report/active/project_project_active_tasking_report_pdf.rml', parser=renwuxiada,
                      header=True)