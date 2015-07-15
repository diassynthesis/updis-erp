# coding=utf-8
__author__ = 'cysnak4713'

import json
from suds.client import Client
from openerp.tools import config
from openerp import exceptions


class OAClient():
    def __init__(self):
        self.HASH_CODE = config.get('oa_hass_code')

    def __getattr__(self, attr):
        if config.get('oa_is_sync'):
            # if False:
            return _Executable(attr)
        else:
            return lambda **o: None


class _Executable(object):
    def __init__(self, method):
        self.HTTP = 'http://%s/WebService/DataInputService.asmx?wsdl' % config.get('oa_server')
        self.method = method

    def __call__(self, **kw):
        oa_client = Client(self.HTTP).service
        function = getattr(oa_client, self.method)
        json_value = kw.pop('json', None)
        if json_value:
            for (key, value) in json_value.items():
                if not value:
                    json_value.pop(key)
                if isinstance(value, long):
                    json_value[key] = int(value)
            result = function(json=json.JSONEncoder().encode(json_value))
        else:
            result = function(**kw)
        result = json.JSONDecoder().decode(result)
        if result['error'] != 0:
            raise exceptions.Warning(u'同步远程OA出错:%s' % result['errmsg'])
        return result

    def __str__(self):
        return '_Executable (%s %s)' % (self._method, self._path)

    __repr__ = __str__


client = OAClient()

if __name__ == '__main__':
    # json_params = (
    # {"msgid": 1122231, "class_code": 144, "title": u"文章标题", "author": u"张小虎", "deptname": u"信息发布中心", "deptcode": 78, "content": u"文章内容",
    #      "readcount": 122,
    #      "createdate": "2001-01-01T00:00:00", "overduedate": "2001-02-01T00:00:00", "lastmodidate": "2001-01-01T00:00:00"}
    # )

    local_client = Client('http://113.108.103.8:8369/WebService/DataInputService.asmx?wsdl')

    value = {'iGroupID': 1539, 'hashcode': 'fast288675ad59usuakca'}
    print local_client.service.DeleteEmployee(iUserCode='1539', hashcode='fast288675ad59usuakca')