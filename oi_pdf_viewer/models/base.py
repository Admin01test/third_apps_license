'''
Created on Jul 17, 2019

@author: Zuhair Hammadi
'''
from odoo import models, api
from lxml.builder import E

class Base(models.AbstractModel):
    _inherit = 'base'
    
    @api.model
    def _get_default_pdf_view(self):
        fname = 'datas'
        
        if fname not in self:
            for name, field in self._fields.items():
                if field.type =='binary':
                    fname= name
                    break
        return E.pdf(datas = fname, string=self._description)
        
        
    def action_pdf_preview(self, report_name, title = 'Report'):
        return {
          'type' : 'ir.actions.act_window',
          'res_model' : self._name,
          'res_id' : len(self)==1 and self.id or 0,
          'target' : 'current',
          'view_type' : 'form',
          'view_mode' : 'pdf',
          'name' : title,
          'context' : {
              'report_name' : report_name,
              'docids' : self.ids
              }
          }