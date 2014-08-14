from openerp.tools import config

__author__ = 'cysnake4713'
from suds.client import Client


class RtxClient(object):
    def __init__(self):
        self.rtx_user = config.get('rtx_user', '')
        self.rtx_password = config.get('rtx_password', '')
        self.rtx_key = config.get('rtx_key', '')
        self.session_id = '{F9A239EB-1728-4608-A4D3-7B17BAEB9F18}'

    def client(self):
        return Client(config.get('rtx_address', ''), timeout=5)


if __name__ == '__main__':
    url = 'http://113.108.103.8:8089/RTX_Service.asmx?wsdl'
    client = Client(url, timeout=1)
    # a = client.service.AddUser(userName='1111111', userPwd='111', DeptName='',  ChsName='', IGender=1, Cell='', Email='', Phone='',
    # Position='', AuthTYpe=0, key='tianvService2014')
    # a = client.service.IsUserExist(userName='kendy', key='tianvService2014')
    # a = client.service.SetUserPwd(userName='kendy', pwd='1', key='tianvService2014')
    # a = client.service.Login(userName='kendy', pwd='1', key='tianvService2014')
    # a = client.service.SendIM(sender='kendy', SenderPwd='1', Receivers='kendy', msg='test', SessionId='{F9A239EB-1728-4608-A4D3-7B17BAEB9F18}',
    # key='tianvService2014')

    a = client.service.SendNotify(Receivers='yanp', title='tests', msg='test', time='10000', key='tianvService2014')
    print a
