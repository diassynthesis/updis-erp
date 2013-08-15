import openerp
from openerp.osv import osv, fields

__author__ = 'cysnake4713'


class up_contract_analysis(osv.osv):
    _name = "project.contract.contract.analysis"
    _description = "Project Contract Analysis"
    _auto = False

    _columns = {
        'contract_id': fields.many2one('project.contract.contract', 'Contract', readonly=1),
        'total_price': fields.float(string='Total Price', digits=(16, 4), readonly=1),
        'paid_price': fields.float(string='Paid Price', digits=(16, 4), readonly=1),
    }

    def init(self, cr):
        openerp.tools.sql.drop_view_if_exists(cr, 'project_contract_contract_analysis')
        cr.execute(" CREATE VIEW project_contract_contract_analysis AS ( " \
                   " SELECT " \
                   " c.id as id," \
                   " c.id as contract_id," \
                   " COALESCE(c.price, 0.0) as total_price," \
                   " COALESCE(SUM(i.price), 0.0) as paid_price" \
                   " FROM " \
                   " project_contract_contract as c LEFT JOIN project_contract_income as i" \
                   " on c.id = i.contract_id" \
                   " GROUP BY c.id" \
                   " )")
