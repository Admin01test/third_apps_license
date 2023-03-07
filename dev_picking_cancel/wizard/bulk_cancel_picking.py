# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

from odoo import api, fields, models, _

class bulk_cancel_picking(models.TransientModel):
    _name = "bulk.cancel.picking"

    def bulk_cancel_picking(self):
        model = self._context.get('active_model')
        model_ids = self.env[model].browse(self._context.get('active_ids'))
        for model_id in model_ids:
            if model in ["sale.order","stock.picking"]:
                model_id.action_cancel()
            if model in ["purchase.order","account.move"]:
                model_id.button_cancel()
            
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
