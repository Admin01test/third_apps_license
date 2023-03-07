# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class bulk_set_draft(models.TransientModel):
    _name = "bulk.set.draft"

    def bulk_draft_set(self):
        model = self._context.get('active_model')
        model_ids = self.env[model].browse(self._context.get('active_ids'))
        for model_id in model_ids:
            if model == 'sale.order':
                if model_id.state != 'cancel':
                    raise ValidationError(_('Sale Order must be cancel Order !!!'))
                model_id.action_draft()
            if model =='stock.picking':
                if model_id.state != 'cancel':
                    raise ValidationError(_('Picking must be cancel Order !!!'))
                model_id.action_set_draft()
            if model == 'account.move':
                if model_id.state != 'cancel':
                    raise ValidationError(_('Invoice must be cancel Order !!!'))
                model_id.button_draft()
            if model == 'purchase.order':
                if model_id.state != 'cancel':
                    raise ValidationError(_('Purchase order must be cancel Order !!!'))
                model_id.button_draft()
                
            
            
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
