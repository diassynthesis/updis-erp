import time
from report import report_sxw


class renwuxiada(report_sxw.rml_parse):
    """docstring for renwuxiada"""

    def __init__(self, cr, uid, name, context):
        super(renwuxiada, self).__init__(cr, 1, name, context)
        self.localcontext.update({
            'time': time,
            # 'project_active_tasking': self._get_project_active_tasking_form,
        })

    def _get_category_names(self, pid):
        # import pdb;pdb.set_trace()
        project = self.pool.get('project.project')
        return [cat.name for cat in project.browse(self.cr, self.uid, pid).categories_id]

    def _get_project_active_tasking_form(self, pid):
        form = self.pool.get('project.project.active.tasking')
        form_ids = form.search(self.cr, self.uid, [('project_id', '=', pid)])
        if form_ids:
            return form.browse(self.cr, self.uid, form_ids[0])


report_sxw.report_sxw('report.project.active.tasking.report.pdf', 'project.project.active.tasking',
                      'up_project/report/active/project_project_active_tasking_report_pdf.rml', parser=renwuxiada,
                      header=True)