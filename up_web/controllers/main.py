__author__ = 'cysnake4713'
# -*- coding: utf-8 -*-

from openerp.addons.web.controllers.main import *
from openerp.addons.web.controllers import main
from tools import config


def set_cookie_and_redirect(req, redirect_url):
    redirect = werkzeug.utils.redirect(redirect_url, 303)
    redirect.autocorrect_location_header = False
    cookie_val = urllib2.quote(simplejson.dumps(req.session_id))

    redirect.set_cookie('instance0|session_id', cookie_val, domain=config.get('domain', None))
    return redirect


html_template = """<!DOCTYPE html>
<html style="height: 100%%">
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <title>UpdisERP</title>
        <link rel="shortcut icon" href="/up_web/static/src/img/favicon.ico" type="image/x-icon"/>
        <link rel="stylesheet" href="/web/static/src/css/full.css" />
        %(css)s
        %(js)s
        <script type="text/javascript">
            $(function() {
                var s = new openerp.init(%(modules)s);
                %(init)s
            });
        </script>
    </head>
    <body>
        <!--[if lte IE 8]>
        <script src="//ajax.googleapis.com/ajax/libs/chrome-frame/1/CFInstall.min.js"></script>
        <script>CFInstall.check({mode: "overlay"});</script>
        <![endif]-->
        <div id="openerp-domain-value" style='display: none;'>""" + config.get('domain', "") + """</div>
    </body>
</html>
"""
main.html_template = html_template
main.set_cookie_and_redirect = set_cookie_and_redirect
#import sys
#sys.modules['|openerp.addons.web.controllers.main'].set_cookie_and_redirect = set_cookie_and_redirect

