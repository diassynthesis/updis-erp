# coding=utf-8
__author__ = 'cysnak4713'

import httplib
import json
from suds.client import Client

if __name__ == '__main__':
    # TODO: 地址可配置
    client = Client('http://113.108.103.8:8369/WebService/DataInputService.asmx?wsdl')
    json_params = (
        {"msgid": 111111131, "class_code": 144, "title": u"文章标题", "author": u"张小虎", "deptname": u"信息发布中心", "deptcode": 78, "content": u"文章内容",
         "readcount": 122,
         "createdate": "2001-01-01T00:00:00", "overduedate": "2001-02-01T00:00:00", "lastmodidate": "2001-01-01T00:00:00"}
    )
    params = {
        'json': json.JSONEncoder().encode(json_params)
    }
    print client.service.CreateMessage(**params)
