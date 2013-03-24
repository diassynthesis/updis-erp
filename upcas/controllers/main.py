import urllib
from openerp.addons.web.controllers.main import set_cookie_and_redirect

__author__ = 'Zhou Guangwen'
import openerp.addons.web.http as openerpweb
import pycas
import werkzeug.utils


class CASController(openerpweb.Controller):
    _cp_path = "/cas"

    def session_info(self, req):
        req.session.ensure_valid()
        return {
            "session_id": req.session_id,
            "uid": req.session._uid,
            "user_context": req.session.get_context() if req.session._uid else {},
            "db": req.session._db,
            "username": req.session._login,
        }

    def cas_login_info(self, req, path):
        return {
            'redirect_url': path
        }

    @openerpweb.jsonrequest
    def cas_login(self, req, base_location=None, ticket=None):
        path = "%s/cas/login?service=%s" % (pycas.CAS_SERVER, pycas.SERVICE_URL)

        try:
            status, uid, cookies, attrs = pycas.login(req, pycas.CAS_SERVER, pycas.SERVICE_URL)
            if attrs:
                db, login, password, lang, uid = attrs
                wsgienv = req.httprequest.environ
                env = dict(
                    base_location=base_location,
                    HTTP_HOST=wsgienv['HTTP_HOST'],
                    REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
                )
                if login:
                    req.session.authenticate(db, login, password, env)

                    ret = self.session_info(req)
                    ret.update({'password': password})
                    return ret
                else:
                    return self.cas_login_info(req, path)
            else:
                return self.cas_login_info(req, path)
        except SystemExit:
            return self.cas_login_info(req, path)

    @openerpweb.jsonrequest
    def cas_logout(self, req):
        return {
            'logout_url':pycas.CAS_SERVER + "/cas/logout"
        }
        # response = urllib.urlopen(pycas.CAS_SERVER + "/cas/logout")
        # response = response.read()
        # return {
        #     "response": response
        # }
