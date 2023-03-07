'''
Created on Jun 8, 2020

@author: Zuhair Hammadi
'''
from odoo import models, fields
from odoo.exceptions import Warning
import requests
import base64
from odoo.tools.pdf import merge_pdf
import zipfile
from .. import EXPORT_FORMAT

import logging
import io
import os
_logger = logging.getLogger(__name__)

class JasperReportRun(models.TransientModel):
    _name = 'jasper.report.run'
    _description = 'Jasper Report Run'
        
    report_id = fields.Many2one('jasper.report', required = True)
    format = fields.Selection(EXPORT_FORMAT, required = True, default = 'pdf')
    
    ignore_pagination = fields.Boolean()
    one_page_per_sheet = fields.Boolean()
    
    datas = fields.Binary(attachment = False, copy = False)
    filename = fields.Char()    
    mimetype = fields.Char()
    
    preview = fields.Boolean()
    
    def action_download(self):
        if len(self)==1:
            if self.format == 'html':
                action = self.action_pdf_preview(self.filename, title = self.report_id.name)
                action['context']['html'] = True
                action['res_id'] = self.id
                return action
            
            if self.preview and self.format=='pdf':
                return self.action_pdf_preview(self.filename, title = self.report_id.name)
            
            return {
                    'type': 'ir.actions.client',
                    'tag' : 'file_download',
                    'params' : {
                        'model' : self._name,
                        'field' : 'datas',
                        'id' : self.id,
                        'filename' : self.filename,
                        'filename_field' : 'filename',
                        'download' : True
                        }
                }
            
        if set(self.mapped('mimetype')) == {'application/pdf'}:
            pdf_data = []
            for record in self:
                data = base64.decodebytes(record.datas)
                pdf_data.append(data)
            data = merge_pdf(pdf_data)
            datas = base64.encodebytes(data)
            return self[0].copy({'datas' : datas}).action_download()     
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            filename, extension = os.path.splitext(self[0].filename)
            no =0
            for record in self:
                no +=1
                data = base64.decodebytes(record.datas)
                zip_file.writestr("%s%s%s" % (filename, no, extension), data)
        
        datas = base64.encodebytes(zip_buffer.getvalue())
        return self[0].copy({'datas' : datas, 'filename' : self[0].filename + ".zip", 'mimetype': 'application/zip'}).action_download()     
        
    def run_report(self, values = None):
        if self.report_id.multi:
            records = self.browse()
            for docid in self._context.get('docids'):
                record = self.copy()
                record.with_context(docid = docid)._run_report(values = values)
                records += record
            return records.action_download()
        
        return self._run_report(values = values)
                    
    def _run_report(self, values = None):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        url = "%(server_url)s/rest_v2/reports%(report_path)s.%(format)s" % {
            'server_url' : get_param('jasper_report.url'),
            'report_path' : self.report_id.report_path,
            'format' : self.format
            }
        params = dict(self._context)
        if values:
            params.update(values)
        params.update({
            'ignorePagination' : self.ignore_pagination,
            'onePagePerSheet' : self.one_page_per_sheet
            })
        
        for name in ['docids', 'active_ids']:
            if isinstance(params.get(name), list):
                params[name] = ','.join(map(str,params[name]))
                
        res = requests.get(url, params=params, auth=(get_param('jasper_report.user'), get_param('jasper_report.password')))
        if res.status_code == 200:
            mimetype = res.headers['content-type']
            self.write({
                'datas' : base64.encodebytes(res.content),
                'filename' : "%s.%s" % (self.report_id.name, self.format),
                'mimetype' : mimetype
                })
            return self.action_download()
        
        status = requests.status_codes._codes[res.status_code][0]
        _logger.warning(res.content)
        raise Warning(status)