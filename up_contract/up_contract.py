from openerp.osv import fields
from openerp import osv

__author__ = 'cysnake4713'


class updis_contract_contract(osv.osv):
    _name = 'project.contract.contract'
    _columns = {
        'name': fields.char(size=128, string="Contract Name"),
    }
