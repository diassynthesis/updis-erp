__author__ = 'Zhou Guangwen'
import openerp.addons.web.http as openerpweb
import pycas
import werkzeug.utils

CAS_SERVER = "https://zhouguangwen-pc:8443"
SERVICE_URL = "http://zhouguangwen-pc:8069/cas/callback"


class CASController(openerpweb.Controller):
    _cp_path = "/cas"

    @openerpweb.httprequest
    def callback(self, req, *args, **kwargs):
        status, uid, cookies, attrs = pycas.login(req, CAS_SERVER, SERVICE_URL)
        print status, uid, cookies
        db, login, password, lang, uid = attrs
        wsgienv = req.httprequest.environ
        env = dict(
            base_location=None,
            HTTP_HOST=wsgienv['HTTP_HOST'],
            REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
        )
        ret = req.session.authenticate(db, login, password, env)
        return "%s"%ret

    @openerpweb.httprequest
    def cas_login(self, req):
        try:
            status, uid, cookies, attrs = pycas.login(req, CAS_SERVER, SERVICE_URL)
            return werkzeug.utils.redirect("/")
        except SystemExit, e:
            redirect = werkzeug.utils.redirect("%s/cas/login?service=%s" % (CAS_SERVER, SERVICE_URL))
            return redirect
    @openerpweb.httprequest
    def foo(self,req):
        req.session.authenticate("updis","admin","Freeborders#1",{})
        return werkzeug.utils.redirect("/")
