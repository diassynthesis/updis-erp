import hashlib

__author__ = 'cysnake4713'
from openerp.tools import config
import pyodbc


def change_password(username, password, connection=None):
    connect_params = connection
    if not connect_params:
        connect_params = {
            'dsn': config.get('guarder_dsn', ''),
            'username': config.get('guarder_sa', ''),
            'password': config.get('guarder_password', ''),
        }
    new_password = hashlib.md5(password).hexdigest()
    con_string = 'DSN=%(dsn)s;UID=%(username)s;PWD=%(password)s;DATABASE=Docguarder;' % connect_params
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    # update password
    cursor.execute("UPDATE dbo.hs_user set col_pword='%(new_password)s' where col_loginname='%(username)s'" % vars())

    cnxn.commit()


if __name__ == '__main__':
    connect = {
        'dsn': 'sqlserverdatasource',
        'username': 'sa',
        'password': '123.com',
    }
    change_password('kendy', '123', connect)