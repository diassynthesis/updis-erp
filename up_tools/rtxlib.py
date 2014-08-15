# coding=utf-8
__author__ = 'cysnake4713'
from suds.client import Client


if __name__ == '__main__':
    url = 'http://113.108.103.8:8089/RTX_Service.asmx?wsdl'
    client = Client(url)
    # a = client.service.AddUser(userName='1111111', userPwd='111', DeptName='',  ChsName='', IGender=1, Cell='', Email='', Phone='',
    # Position='', AuthTYpe=0, key='tianvService2014')
    # a = client.service.IsUserExist(userName='kendy', key='tianvService2014')
    # a = client.service.SetUserPwd(userName='kendy', pwd='1', key='tianvService2014')
    # a = client.service.Login(userName='kendy', pwd='1', key='tianvService2014')
    # a = client.service.SendIM(sender='kendy', SenderPwd='1', Receivers='kendy', msg='test', SessionId='{F9A239EB-1728-4608-A4D3-7B17BAEB9F18}',
    # key='tianvService2014')

    a = client.service.SendNotify(Receivers='yanp', title=u'离线', msg='www.baidu.com', time='10000', key='tianvService2014')
    print a
