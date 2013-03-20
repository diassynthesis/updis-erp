#
# Implements encrypting functions.
#
# Copyright (c) 2008, F S 3 Consulting Inc.
#
# Maintainer:
# Alec Joseph Rivera (agi<at>fs3.ph)
# refactored by Antony Lesuisse <al<at>openerp.com>
#

import hashlib
import hmac
import logging
from random import sample
from string import ascii_letters, digits

import openerp
from openerp.osv import fields, osv

_logger = logging.getLogger(__name__)

magic_md5 = '$1$'
magic_sha256 = '$5$'


def gen_salt(length=8, symbols=None):
    if symbols is None:
        symbols = ascii_letters + digits
    return ''.join(sample(symbols, length))


def md5crypt( raw_pw, salt='', magic=magic_md5 ):
    h = hashlib.md5(raw_pw).hexdigest()
    return h


def sh256crypt(cls, password, salt, magic=magic_sha256):
    iterations = 1000
    # see http://en.wikipedia.org/wiki/PBKDF2
    result = password.encode('utf8')
    for i in xrange(cls.iterations):
        result = hmac.HMAC(result, salt, hashlib.sha256).digest() # uses HMAC (RFC 2104) to apply salt
    result = result.encode('base64') # doesnt seem to be crypt(3) compatible
    return '%s%s$%s' % (magic_sha256, salt, result)


class res_users(osv.osv):
    _inherit = "res.users"

    def set_pw(self, cr, uid, id, name, value, args, context):
        if value:
            encrypted = md5crypt(value, gen_salt())
            cr.execute('update res_users set password_crypt=%s where id=%s', (encrypted, int(id)))
        del value

    def get_pw( self, cr, uid, ids, name, args, context ):
        cr.execute('select id, password from res_users where id in %s', (tuple(map(int, ids)),))
        stored_pws = cr.fetchall()
        res = {}

        for id, stored_pw in stored_pws:
            res[id] = stored_pw

        return res

    _columns = {
        'password': fields.function(get_pw, fnct_inv=set_pw, type='char', string='Password', invisible=True,
                                    store=True),
        'password_crypt': fields.char(string='Encrypted Password', invisible=True),
    }

    def check_credentials(self, cr, uid, password):
        # convert to base_crypt if needed
        cr.execute('SELECT password, password_crypt FROM res_users WHERE id=%s AND active', (uid,))
        if cr.rowcount:
            stored_password, stored_password_crypt = cr.fetchone()
            if password and not stored_password_crypt:
                salt = gen_salt()
                stored_password_crypt = md5crypt(stored_password, salt)
                cr.execute("UPDATE res_users SET password='', password_crypt=%s WHERE id=%s",
                           (stored_password_crypt, uid))
        try:
            return super(res_users, self).check_credentials(cr, uid, password)
        except openerp.exceptions.AccessDenied:
            # check md5crypt
            if stored_password_crypt == md5crypt(password):
                return
                # Reraise password incorrect
            raise


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
