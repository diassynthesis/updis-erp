from openerp.osv import fields
from openerp.osv import osv

__author__ = 'cysnake4713'


class updis_contract_invoice(osv.osv):
    _name = 'project.contract.invoice'
    _description = 'Project Contract Invoice'
    _columns = {
        'create_date': fields.date('Invoice Create Date'),
        'price': fields.float(string='Price', digits=(16, 4)),
        'comment': fields.text(string="Comment"),
        'handler': fields.many2one('hr.employee', string='Handler'),
        'contract_id': fields.many2one('project.contract.contract', string="Contract"),
        'income_ids': fields.many2many('project.contract.income', 'contract_invoice_income_rels', 'invoice_id',
                                       'income_id', string='Incomes'),
    }


class updis_contract_income(osv.osv):
    _name = 'project.contract.income'
    _columns = {
        'obtain_date': fields.date('Obtain Date'),
        'price': fields.float(string='Obtain Price', digits=(16, 4)),
        'comment': fields.text(string="Comment"),
        'handler': fields.many2one('hr.employee', string='Handler'),
        'contract_id': fields.many2one('project.contract.contract', string="Contract"),
        'invoice_ids': fields.many2many('project.contract.invoice', 'contract_invoice_income_rels', 'income_id',
                                        'invoice_id', string='Invoices'),
    }


class updis_contract_contract(osv.osv):
    _name = 'project.contract.contract'

    def _get_project_category(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = ""
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

        'income_ids': fields.one2many('project.contract.income', 'contract_id', string='Incomes'),
        'invoice_ids': fields.one2many('project.contract.invoice', 'contract_id', string='Invoices'),


    }


class updis_project_project(osv.osv):
    _inherit = "project.project"
    _columns = {
        'contract_ids': fields.one2many('project.contract.contract', 'project_id', string='Project Contracts'),
    }