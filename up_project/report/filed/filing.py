# coding=utf-8
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

        keys = ['1', '2', '3', '4', '5', '6']
        records = {key: list([]) for key in keys}
        for record_id in filing.record_ids:
            if record_id.type_id.name == u'文本类成果':
                records['1'].append(record_id)
            if record_id.type_id.name == u'图件成果':
                records['2'].append(record_id)
            if record_id.type_id.name == u'计算书':
                records['3'].append(record_id)
            if record_id.type_id.name == u'项目过程质量记录单':
                records['4'].append(record_id)
            if record_id.type_id.name == u'重要依据性文件':
                records['5'].append(record_id)
            if record_id.type_id.name == u'项目依据性资料':
                records['6'].append(record_id)

        self.localcontext.update({
            'cr': cr,
            'object': filing,
            'tags': tags,
            'file_records': records,
        })


report_sxw.report_sxw('report.project.filed.filing.report.pdf.info', 'project.project.filed.filing',
                      'up_project/report/active/project_project_filed_filing_report_pdf_info.mako', parser=ProjectFiledFilingPDF)

report_sxw.report_sxw('report.project.filed.filing.report.pdf.paper', 'project.project.filed.filing',
                      'up_project/report/active/project_project_filed_filing_report_pdf_paper.mako', parser=ProjectFiledFilingPDF)