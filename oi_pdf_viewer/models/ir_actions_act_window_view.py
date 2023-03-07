'''
Created on May 23, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class IrActionsActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('pdf', 'PDF Viewer')], ondelete={'pdf' : 'cascade'})

