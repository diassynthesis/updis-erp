from openerp.report.report_sxw import rml_parse

__author__ = 'cysnake4713'


def monkey_set_html_image(self, id, model=None, field=None, context=None):
    if not id:
        return ''
    if not model:
        model = 'ir.attachment'
    try:
        ids = [int(id)]
        res = self.pool[model].read(self.cr, self.uid, ids)[0]
        if field:
            return res[field]
        elif model == 'ir.attachment':
            return res['datas']
        else:
            return ''
    except Exception:
        return ''


rml_parse.set_html_image = monkey_set_html_image