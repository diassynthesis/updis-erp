import datetime
from openerp.osv import fields
from openerp.osv import osv

__author__ = 'cysnake4713'


class updis_contract_invoice(osv.osv):
    _name = 'project.contract.invoice'
    _description = 'Project Contract Invoice'
    _rec_name = 'number'
    _columns = {
        'number': fields.char('Invoice No.', size=64, required=True),
        'obtain_date': fields.date('Invoice Create Date', required=True),
        'price': fields.float(string='Price', digits=(16, 4)),
        'comment': fields.text(string="Comment"),
        'handler': fields.many2one('hr.employee', string='Handler'),
        'contract_id': fields.many2one('project.contract.contract', string="Contract"),
        'income_ids': fields.many2many('project.contract.income', 'contract_invoice_income_rels', 'invoice_id',
                                       'income_id', string='Incomes'),
    }

    _defaults = {
        'obtain_date': lambda *a: str(datetime.date.today()),
    }


class updis_contract_income(osv.osv):
    _name = 'project.contract.income'
    _rec_name = 'price'
    _columns = {
        'obtain_date': fields.date('Obtain Date', required=True),
        'price': fields.float(string='Obtain Price', digits=(16, 4)),
        'comment': fields.text(string="Comment"),
        'handler': fields.many2one('hr.employee', string='Handler'),
        'contract_id': fields.many2one('project.contract.contract', string="Contract"),
        'invoice_ids': fields.many2many('project.contract.invoice', 'contract_invoice_income_rels', 'income_id',
                                        'invoice_id', string='Invoices'),
    }

    _defaults = {
        'obtain_date': lambda *a: str(datetime.date.today()),
    }


class updis_contract_contract(osv.osv):
    _name = 'project.contract.contract'

    def _get_project_category(self, cr, uid, ids, field_name=None, args=None, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.project_id:
                if obj.project_id.shifoutoubiao:
                    result[obj.id] = obj.project_id.toubiaoleibie
                else:
                    result[obj.id] = obj.project_id.categories_id.name
        return result

    _columns = {
        'name': fields.char(size=128, string="Contract Name", required=True),
        'customer': fields.many2many('res.partner', 'contract_partner_rel', 'contract_id', 'partner_id',
                                     string='Customers'),
        'customer_contact': fields.many2many('res.partner', 'contract_contact_partner_rel', 'contract_contact_id',
                                             'partner_id', string="Customer Contacts"),
        'price': fields.float(string='Contract Price', digits=(16, 4)),
        'number': fields.char(string='Contract No.', size=128),
        'city_level_number': fields.char(string='City Contract No.', size=128),
        'filed_date': fields.date(string='Contract Filed Date'),
        'project_start_date': fields.date(string="Project Start Date"),
        'comment': fields.text(string="Comment"),


        'project_id': fields.many2one('project.project', string="Project"),
        'project_category': fields.function(_get_project_category, type="char",
                                            string="Project Category"),
        'design_department': fields.related('project_id', 'chenjiebumen_id', type="many2one",
                                            relation="hr.department", string='Design Department'),
        'project_scale': fields.related('project_id', 'guimo', type='char', string="Project Scale"),
        'project_level': fields.related('project_id', 'guanlijibie', type='char', string='Project Level'),

        'income_ids': fields.one2many('project.contract.income', 'contract_id', string='Incomes', ondelete="cascade"),
        'invoice_ids': fields.one2many('project.contract.invoice', 'contract_id', string='Invoices',
                                       ondelete="cascade"),


    }

    def _get_project_category_on_change(self, cr, uid, ids, project_id, context=None):
        project = self.pool.get('project.project').browse(cr, uid, project_id, context)
        if project:
            if project.shifoutoubiao:
                return project.toubiaoleibie
            else:
                return project.categories_id.name
        else:
            return ""

    def on_change_project(self, cr, uid, ids, project_id, context=None):
        ret = {'value': {}}
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id, context)
            values = {
                'number': project.xiangmubianhao,
                'design_department': project.chenjiebumen_id.id,
                'project_scale': project.guimo,
                'project_level': project.guanlijibie,
                'customer': project.partner_id and [project.partner_id.id] or [],
                'customer_contact': project.customer_contact and [project.customer_contact.id] or [],
                'project_category': self._get_project_category_on_change(cr, uid, ids, project_id, context)
            }
            ret['value'].update(values)
        else:
            values = {
                'number': None,
                'design_department': None,
                'project_scale': "",
                'project_level': "",
                'customer': [],
                'customer_contact': [],
                'project_category': "",
            }
            ret['value'].update(values)
        return ret

    def _update_related_contract_id(self, cr, uid, vals, first, second, second_obj, contract_id, context):
        if first in vals.keys():
            for i in vals[first]:
                if len(i) == 3:
                    second_dict = i[2]
                    if second_dict and second in second_dict.keys():
                        for j in second_dict[second]:
                            if len(j) == 3:
                                ids = j[2]
                                self.pool.get(second_obj).write(cr, uid, ids, {'contract_id': contract_id}, context)

    def _update_contract_id(self, cr, uid, vals, contract_id, context):
        self._update_related_contract_id(cr, uid, vals, 'income_ids', 'invoice_ids', 'project.contract.invoice',
                                         contract_id, context)
        self._update_related_contract_id(cr, uid, vals, 'invoice_ids', 'income_ids', 'project.contract.income',
                                         contract_id, context)

    def create(self, cr, uid, vals, context=None):
        mid = super(updis_contract_contract, self).create(cr, uid, vals, context)
        self._update_contract_id(cr, uid, vals, mid, context)
        return mid

    def write(self, cr, uid, ids, vals, context=None):
        if len(ids) == 1:
            self._update_contract_id(cr, uid, vals, ids[0], context)
        result = super(updis_contract_contract, self).write(cr, uid, ids, vals, context=context)
        return result


class updis_project_project(osv.osv):
    _inherit = "project.project"
    _columns = {
        'contract_ids': fields.one2many('project.contract.contract', 'project_id',
                                        string='Project Contracts'),
    }