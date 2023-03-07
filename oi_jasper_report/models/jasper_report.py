'''
Created on Jun 8, 2020

@author: Zuhair Hammadi
'''
from odoo import models, fields
from .. import EXPORT_FORMAT

class JasperReport(models.Model):
    _name = 'jasper.report'
    _description = 'Jasper Report'
    
    name = fields.Char(required = True)
    report_path = fields.Char(required = True)
    active = fields.Boolean(default = True)
    model_id = fields.Many2one('ir.model', string='Object')
    action_id = fields.Many2one('ir.actions.server', readonly = True)
    
    multi = fields.Boolean('Execute per record', help = 'Report will run for each record then will be combined')
    format = fields.Selection(EXPORT_FORMAT, required = True, default = 'pdf')
    ignore_pagination = fields.Boolean()
    one_page_per_sheet = fields.Boolean()
    preview = fields.Boolean()
    
    format_selection = fields.Boolean('Format selected by user')
    
    def action_create_action(self):
        if not self.action_id:
            self.action_id = self.env['ir.actions.server'].create({
                'model_id' : self.model_id.id,
                'name' : self.name,
                'binding_model_id' : self.model_id.id,
                'binding_type' : 'report',
                'state' : 'code',
                'code' : "action=env['jasper.report'].browse(%d).run_report(records.ids)" % self.id,
                })
            
    def run_report(self, docids, data=None):                
        context = dict(self._context)
        context.update({
            'docids' : docids,
            'docid' : docids[0]
            })
        if data:
            context.update(data)
        
        if self.format_selection:
            context.update({
                'default_report_id' : self.id,
                'default_format' : self.format,
                'default_ignore_pagination' : self.ignore_pagination,
                'default_one_page_per_sheet' : self.one_page_per_sheet,
                'default_preview' : self.preview
                })
            return {
                'type' : 'ir.actions.act_window',
                'name' : self.name,
                'view_mode' : 'form',
                'target' : 'new',
                'res_model' : 'jasper.report.run',
                'context' : context
                }    
        
        wizard = self.env['jasper.report.run'].create({
            'report_id' : self.id,
            'format' : self.format,
            'ignore_pagination' : self.ignore_pagination,
            'one_page_per_sheet' : self.one_page_per_sheet,
            'preview' : self.preview
            })
        return wizard.with_context(context).run_report()