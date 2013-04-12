# -*- coding: utf-8 -*-
import hashlib
import random
import simplejson
import os
import time

import openerp
import ftputil
from openerp.addons.web.controllers.main import manifest_list



class InternalHome(openerp.addons.web.http.Controller):
    _cp_path = "/web/clupload"



    def _generate_file_name(self, s_file_name):

        def _get_salt(current_time, filename):
            salt = str(random.random)
            h = hashlib.md5(current_time + salt).hexdigest()
            return h

        current_time = time.strftime('%Y-%m-%d_%H-%M', time.localtime(time.time()))
        salt = _get_salt(current_time, s_file_name)
        return '%s_%s%s' % (current_time, salt, os.path.splitext(s_file_name)[1])


    def _upload_file_ftp(self, file_data, file_name):
        HOME = os.getenv("HOME") + '/tempfile'
        if not os.path.exists(HOME):
            os.mkdir(HOME)
        new_file_name = self._generate_file_name(file_name)
        output = open(HOME + '/' + new_file_name, 'wb')
        output.write(file_data)
        output.close()
        try:
            host = ftputil.FTPHost('10.100.100.196', 'ftpuser', 'updis_ftp_2013')
            host.upload(HOME + '/' + str(new_file_name), '/' + str(new_file_name))
            args = {
                'filename': new_file_name,
                'success': True,
            }
        except Exception, e:
            args = {'error': e.message}
        finally:
            host.close()
            if os.path.isfile(HOME + '/' + new_file_name):
                os.remove(HOME + '/' + new_file_name)
            return args

    def _create_attachment(self, req, qqfile, resize_image=False):
        context = req.context
        Model = req.session.model('ir.attachment')

        # datas = base64.encodestring(req.httprequest.data)
        # if resize_image:
        #     datas = tools.image_resize_image(datas, size=(700, 700))

        args = self._upload_file_ftp(req.httprequest.data, qqfile)

        # attachment_id = Model.create({
        #                                  'name': qqfile,
        #                                  'datas': datas,
        #                                  'datas_fname': qqfile,
        #                              }, context)
        return args

    @openerp.addons.web.http.httprequest
    def upload_image(self, req, qqfile):
        try:
            args = self._create_attachment(req, qqfile, True)
            # model, id, field, **kw
            url = 'http://10.100.100.196:8000/%s' % (args['filename'])
            args['url'] = url
        except Exception, e:
            args = {'error': e.message}
        return req.make_response(simplejson.dumps(args))

    @openerp.addons.web.http.httprequest
    def upload_file(self, req, qqfile):
        try:
            args = self._create_attachment(req, qqfile)
            # model, field, id=None, filename_field=None, **kw)
            url = 'http://10.100.100.196:8000/%s' % (args['filename'])
            args['url'] = url
        except Exception, e:
            args = {'error': e.message}
        return req.make_response(simplejson.dumps(args))