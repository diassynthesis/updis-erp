from openerp.report.report_sxw import rml_parse

__author__ = 'cysnake4713'


def monkey_set_html_image(self, id, model=None, field=None, context=None):
    if not id:
        return ''
    if not model:
        model = 'ir.attachment'
    try:
        id = int(id)
        res = self.pool.get(model).read(self.cr, self.uid, id)
        if field:
            return res[field]
        elif model == 'ir.attachment':
            return res[0]['datas']
        else:
            return ''
    except Exception:
        return ''


rml_parse.set_html_image = monkey_set_html_image