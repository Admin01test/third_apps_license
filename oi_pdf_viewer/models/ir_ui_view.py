'''
Created on May 23, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('pdf', 'PDF Viewer')], ondelete={'pdf' : 'cascade'})
