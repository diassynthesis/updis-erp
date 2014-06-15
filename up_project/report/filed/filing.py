# coding=utf-8
from collections import OrderedDict
from report import report_sxw


class ProjectFiledFilingPDF(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        def merge_list(result, value):
            if value[0] in result:
                result[value[0]] += [value[1]]
            else:
                result[value[0]] = [value[1]]
            return result

        super(ProjectFiledFilingPDF, self).__init__(cr, 1, name, context)
        filing = self.pool.get(context['active_model']).browse(cr, uid, context['active_id'])
        tags = {}
        for tag in filing.tag_ids:
            if tag.parent_id and tag.parent_id.name not in tags:
                tags[tag.parent_id.name] = [tag.name]
            elif tag.parent_id and tag.parent_id.name in tags:
                tags[tag.parent_id.name].append(tag.name)

        paper_attachemnts = [(r.type_id.name, r) for r in filing.record_ids]
        paper_attachemnts = reduce(merge_list, paper_attachemnts, OrderedDict({}))

        attach_analysis_obj = self.pool['project.project.filed.filing.attachment.analysis']
        elec_attachments_ids = attach_analysis_obj.search(cr, uid, [('project_id', '=', filing.project_id.id)], order='version desc, project_id',
                                                          context=context)
        elec_attachments = [(a.parent_id.name_get()[0][1], a) for a in attach_analysis_obj.browse(cr, uid, elec_attachments_ids, context)]
        elec_attachments = reduce(merge_list, elec_attachments, OrderedDict({}))
        elec_attachments.items()
        self.localcontext.update({
            'cr': cr,
            'object': filing,
            'tags': tags,
            'paper_attachemnts': paper_attachemnts,
            'elec_attachments': elec_attachments,
        })


report_sxw.report_sxw('report.project.filed.filing.report.pdf.info', 'project.project.filed.filing',
                      'up_project/report/active/project_project_filed_filing_report_pdf_info.mako', parser=ProjectFiledFilingPDF)

report_sxw.report_sxw('report.project.filed.filing.report.pdf.paper', 'project.project.filed.filing',
                      'up_project/report/active/project_project_filed_filing_report_pdf_paper.mako', parser=ProjectFiledFilingPDF)

report_sxw.report_sxw('report.project.filed.filing.report.pdf.elec', 'project.project.filed.filing',
                      'up_project/report/active/project_project_filed_filing_report_pdf_elec.mako', parser=ProjectFiledFilingPDF)