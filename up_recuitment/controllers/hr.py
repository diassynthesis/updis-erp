__author__ = 'cysnake4713'
import openerp
import simplejson
from openerp.addons.web.controllers.main import manifest_list


class MemberClient(openerp.addons.web.http.Controller):
    _cp_path = "/hr/member"

    @openerp.addons.web.http.httprequest
    def create_member(self, req):
        member_obj = req.session.model('hr.member')
        return simplejson.dumps({})
