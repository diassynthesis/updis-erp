from report import report_sxw


class ProjectFiledFilingPDF(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ProjectFiledFilingPDF, self).__init__(cr, 1, name, context)
        filing = self.pool.get(context['active_model']).browse(cr, uid, context['active_id'])
        tags = {}
        for tag in filing.tag_ids:
            if tag.parent_id and tag.parent_id.name not in tags:
                tags[tag.parent_id.name] = [tag.name]
            elif tag.parent_id and tag.parent_id.name in tags:
                tags[tag.parent_id.name].append(tag.name)
        self.localcontext.update({
            'cr': cr,
            'object': filing,
            'tags': tags,
        })

report_sxw.report_sxw('report.project.filed.filing.report.pdf', 'project.project.filed.filing',
                      'up_project/report/active/project_project_filed_filing_report_pdf.mako', parser=ProjectFiledFilingPDF)